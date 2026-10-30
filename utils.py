"""
FoodBridge - Business Logic & Utility Functions
Handles expiry tracking, concurrency protection, status transitions,
metrics calculation, and input validation.
"""

import re
import uuid
from datetime import datetime, timedelta
import config
import database as db

DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATETIME_SEC_FORMAT = "%Y-%m-%d %H:%M:%S"

def parse_datetime(dt_str: str) -> datetime | None:
    """Safely parse a datetime string trying multiple formats."""
    if not dt_str:
        return None
    for fmt in (DATETIME_FORMAT, DATETIME_SEC_FORMAT, "%Y-%m-%d"):
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    return None

def is_expired(expiry_str: str) -> bool:
    """Return True if the given expiry datetime has already passed."""
    dt = parse_datetime(expiry_str)
    if not dt:
        return False
    return datetime.now() > dt

def time_remaining_badge(expiry_str: str) -> dict:
    """
    Compute readable time left until expiry.
    Returns dict with label, is_expired, and urgency level ('normal', 'urgent', 'expired').
    """
    dt = parse_datetime(expiry_str)
    if not dt:
        return {"text": "No expiry set", "is_expired": False, "urgency": "normal"}
    
    now = datetime.now()
    diff = dt - now
    
    if diff.total_seconds() <= 0:
        return {"text": "Expired", "is_expired": True, "urgency": "expired"}
    
    total_minutes = int(diff.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    if hours > 24:
        days = hours // 24
        rem_hours = hours % 24
        return {"text": f"{days}d {rem_hours}h left", "is_expired": False, "urgency": "normal"}
    elif hours > 3:
        return {"text": f"{hours}h {minutes}m left", "is_expired": False, "urgency": "normal"}
    else:
        # Less than 3 hours left: urgent!
        return {"text": f"⚠️ {hours}h {minutes}m left!", "is_expired": False, "urgency": "urgent"}

def auto_update_expired_donations():
    """
    Periodically called to automatically mark any available donation
    whose expiry timestamp has passed as 'Expired'.
    """
    donations = db.get_donations()
    updated = False
    
    for d in donations:
        if d.get("status") == config.STATUS_COLORS.get("Available", {}).get("text", "Available"):
            expiry = d.get("expiry_time", "")
            if is_expired(expiry):
                d["status"] = "Expired"
                updated = True
    
    if updated:
        db.save_donations(donations)

# --- Concurrency & Claim Protection ---

def claim_donation(
    donation_id: str,
    ngo_user: dict,
    pickup_time_estimate: str,
    transport_type: str,
    beneficiary_count: int,
    notes: str
) -> tuple[bool, str]:
    """
    Safely claim a donation for an NGO.
    Guarantees:
    1. Donation exists.
    2. Donation is not expired.
    3. Donation is still 'Available' (preventing double claims).
    """
    # 1. Update expired items first
    auto_update_expired_donations()
    
    donations = db.get_donations()
    donation = next((d for d in donations if d["id"] == donation_id), None)
    
    if not donation:
        return False, "Donation listing not found."
    
    # 2. Check Expiry
    if is_expired(donation.get("expiry_time", "")):
        donation["status"] = "Expired"
        db.save_donations(donations)
        return False, "This food donation has expired and cannot be requested for safety reasons."
    
    # 3. Check Status
    current_status = donation.get("status")
    if current_status != "Available":
        claimed_ngo = donation.get("claimed_by_ngo_id")
        if claimed_ngo == ngo_user["id"]:
            return False, "Your organization has already submitted a request for this donation."
        return False, f"Sorry, this donation is no longer available (Current status: {current_status}). Another NGO may have just requested it."
    
    # 4. Atomically mark as Requested
    donation["status"] = "Requested"
    donation["claimed_by_ngo_id"] = ngo_user["id"]
    
    # 5. Create Request record
    requests = db.get_requests()
    new_request = {
        "id": f"req_{uuid.uuid4().hex[:8]}",
        "donation_id": donation_id,
        "ngo_id": ngo_user["id"],
        "ngo_name": ngo_user["name"],
        "ngo_org": ngo_user.get("organization", ngo_user["name"]),
        "ngo_phone": ngo_user.get("phone", ""),
        "pickup_time_estimate": pickup_time_estimate,
        "transport_type": transport_type,
        "beneficiary_count": beneficiary_count,
        "notes": notes.strip(),
        "status": "Requested",
        "requested_at": datetime.now().strftime(DATETIME_SEC_FORMAT),
        "completed_at": None
    }
    requests.append(new_request)
    
    # Persist both
    db.save_donations(donations)
    db.save_requests(requests)
    
    return True, "Food donation requested successfully! The donor has been notified of your pickup plan."

# --- Donor Actions ---

def add_new_donation(donor_user: dict, donation_data: dict) -> tuple[bool, str]:
    """Validate and add a new food donation listing."""
    # Check expiry in future
    expiry_str = donation_data.get("expiry_time", "")
    expiry_dt = parse_datetime(expiry_str)
    
    if not expiry_dt:
        return False, "Please provide a valid expiry date and time."
    
    if expiry_dt <= datetime.now():
        return False, "Expiry time must be set in the future."
    
    qty = donation_data.get("quantity", 0)
    if qty <= 0:
        return False, "Quantity must be greater than zero."
    
    # Approximate kg calculation if plates or packets
    unit = donation_data.get("unit", "")
    if "Plates" in unit:
        approx_kg = round(qty * config.KG_PER_MEAL_ESTIMATE, 1)
    elif "kg" in unit:
        approx_kg = float(qty)
    else:
        approx_kg = round(qty * 0.5, 1)
    
    donations = db.get_donations()
    new_donation = {
        "id": f"don_{uuid.uuid4().hex[:8]}",
        "donor_id": donor_user["id"],
        "donor_name": donor_user["name"],
        "donor_org": donor_user.get("organization", donor_user["name"]),
        "donor_phone": donor_user.get("phone", ""),
        "title": donation_data["title"].strip(),
        "category": donation_data["category"],
        "dietary": donation_data.get("dietary", "Vegetarian"),
        "quantity": qty,
        "unit": unit,
        "approx_kg": approx_kg,
        "storage": donation_data.get("storage", "Room Temperature (Cool & Dry)"),
        "pickup_address": donation_data.get("pickup_address", "").strip(),
        "city": donation_data.get("city", donor_user.get("city", "Bangalore")).strip(),
        "cooked_time": donation_data.get("cooked_time", datetime.now().strftime(DATETIME_FORMAT)),
        "expiry_time": expiry_str,
        "instructions": donation_data.get("instructions", "").strip(),
        "safety_verified": donation_data.get("safety_verified", False),
        "status": "Available",
        "claimed_by_ngo_id": None,
        "created_at": datetime.now().strftime(DATETIME_SEC_FORMAT)
    }
    
    donations.insert(0, new_donation)
    db.save_donations(donations)
    return True, "Food donation posted successfully! NGOs in your area can now view and request it."

def edit_donation(donor_user: dict, donation_id: str, updated_data: dict) -> tuple[bool, str]:
    """Edit an existing donation listing owned by donor."""
    donations = db.get_donations()
    donation = next((d for d in donations if d["id"] == donation_id), None)
    
    if not donation:
        return False, "Donation not found."
    
    if donation["donor_id"] != donor_user["id"] and donor_user.get("role") != config.ROLE_ADMIN:
        return False, "You do not have permission to edit this listing."
    
    if donation["status"] in ["Completed", "Accepted"]:
        return False, f"Cannot edit donation that is already {donation['status']}."
    
    # Update fields
    donation["title"] = updated_data.get("title", donation["title"]).strip()
    donation["category"] = updated_data.get("category", donation["category"])
    donation["dietary"] = updated_data.get("dietary", donation.get("dietary", "Vegetarian"))
    donation["quantity"] = updated_data.get("quantity", donation["quantity"])
    donation["unit"] = updated_data.get("unit", donation["unit"])
    donation["storage"] = updated_data.get("storage", donation["storage"])
    donation["pickup_address"] = updated_data.get("pickup_address", donation["pickup_address"]).strip()
    donation["city"] = updated_data.get("city", donation["city"]).strip()
    donation["expiry_time"] = updated_data.get("expiry_time", donation["expiry_time"])
    donation["instructions"] = updated_data.get("instructions", donation["instructions"]).strip()
    
    # Recalculate approx kg
    qty = donation["quantity"]
    unit = donation["unit"]
    if "Plates" in unit:
        donation["approx_kg"] = round(qty * config.KG_PER_MEAL_ESTIMATE, 1)
    elif "kg" in unit:
        donation["approx_kg"] = float(qty)
    else:
        donation["approx_kg"] = round(qty * 0.5, 1)
        
    db.save_donations(donations)
    return True, "Donation listing updated successfully."

def delete_donation(donor_user: dict, donation_id: str) -> tuple[bool, str]:
    """Delete a donation if allowed."""
    donations = db.get_donations()
    donation = next((d for d in donations if d["id"] == donation_id), None)
    
    if not donation:
        return False, "Donation not found."
    
    if donation["donor_id"] != donor_user["id"] and donor_user.get("role") != config.ROLE_ADMIN:
        return False, "You do not have permission to delete this listing."
    
    if donation["status"] == "Completed":
        return False, "Completed donations cannot be deleted as they are part of the platform audit history."
    
    # Remove donation
    donations = [d for d in donations if d["id"] != donation_id]
    db.save_donations(donations)
    
    # Also cancel or update associated requests
    requests = db.get_requests()
    for req in requests:
        if req.get("donation_id") == donation_id:
            req["status"] = "Cancelled"
    db.save_requests(requests)
    
    return True, "Donation listing deleted successfully."

def update_request_status(
    request_id: str,
    new_status: str,
    user: dict
) -> tuple[bool, str]:
    """
    Transition request and donation status.
    E.g. Donor accepts a request: 'Requested' -> 'Accepted'.
    Or NGO/Donor completes pickup: 'Accepted' -> 'Completed'.
    Or request is cancelled: 'Cancelled' -> donation reverts to 'Available'.
    """
    requests = db.get_requests()
    donations = db.get_donations()
    
    req = next((r for r in requests if r["id"] == request_id), None)
    if not req:
        return False, "Request record not found."
    
    donation = next((d for d in donations if d["id"] == req["donation_id"]), None)
    
    req["status"] = new_status
    
    if new_status == "Completed":
        req["completed_at"] = datetime.now().strftime(DATETIME_SEC_FORMAT)
        if donation:
            donation["status"] = "Completed"
    elif new_status == "Accepted":
        if donation:
            donation["status"] = "Accepted"
    elif new_status == "Cancelled":
        if donation:
            # Reopen donation if not expired
            if is_expired(donation.get("expiry_time", "")):
                donation["status"] = "Expired"
            else:
                donation["status"] = "Available"
                donation["claimed_by_ngo_id"] = None
    
    db.save_requests(requests)
    db.save_donations(donations)
    return True, f"Status updated to '{new_status}'."

# --- Metrics & Impact Calculations ---

def get_platform_metrics() -> dict:
    """Calculate platform-wide totals and impact indicators."""
    auto_update_expired_donations()
    
    donations = db.get_donations()
    users = db.get_users()
    requests = db.get_requests()
    
    donors_count = sum(1 for u in users if u.get("role") == config.ROLE_DONOR and u.get("is_active", True))
    ngos_count = sum(1 for u in users if u.get("role") == config.ROLE_NGO and u.get("is_active", True))
    
    total_donations_count = len(donations)
    available_count = sum(1 for d in donations if d.get("status") == "Available")
    completed_donations = [d for d in donations if d.get("status") == "Completed"]
    completed_count = len(completed_donations)
    
    # Calculate rescued food weight
    total_kg_rescued = sum(float(d.get("approx_kg", 0.0)) for d in completed_donations)
    # Estimate meals served (~0.4 kg per meal)
    total_meals_saved = int(total_kg_rescued / config.KG_PER_MEAL_ESTIMATE) if total_kg_rescued > 0 else sum(
        int(d.get("quantity", 0)) for d in completed_donations if "Plate" in d.get("unit", "")
    )
    
    co2_diverted_kg = round(total_kg_rescued * config.CO2_PER_KG_FOOD_SAVED, 1)
    water_saved_liters = round(total_kg_rescued * config.WATER_SAVED_PER_KG, 0)
    
    return {
        "total_donors": donors_count,
        "total_ngos": ngos_count,
        "total_donations": total_donations_count,
        "available_donations": available_count,
        "completed_donations": completed_count,
        "total_kg_rescued": round(total_kg_rescued, 1),
        "total_meals_saved": total_meals_saved,
        "co2_diverted_kg": co2_diverted_kg,
        "water_saved_liters": water_saved_liters,
        "total_requests": len(requests)
    }

def get_donor_metrics(donor_id: str) -> dict:
    """Calculate personalized statistics for a specific donor."""
    donations = db.get_donations()
    my_donations = [d for d in donations if d.get("donor_id") == donor_id]
    
    completed = [d for d in my_donations if d.get("status") == "Completed"]
    available = [d for d in my_donations if d.get("status") == "Available"]
    active_requests = [d for d in my_donations if d.get("status") in ["Requested", "Accepted"]]
    
    total_kg = sum(float(d.get("approx_kg", 0.0)) for d in completed)
    total_meals = int(total_kg / config.KG_PER_MEAL_ESTIMATE)
    
    return {
        "total_posted": len(my_donations),
        "available": len(available),
        "in_progress": len(active_requests),
        "completed": len(completed),
        "kg_diverted": round(total_kg, 1),
        "meals_provided": total_meals,
        "co2_saved": round(total_kg * config.CO2_PER_KG_FOOD_SAVED, 1)
    }

def get_ngo_metrics(ngo_id: str) -> dict:
    """Calculate personalized statistics for a specific NGO."""
    requests = db.get_requests()
    donations = db.get_donations()
    don_lookup = {d["id"]: d for d in donations}
    
    my_requests = [r for r in requests if r.get("ngo_id") == ngo_id]
    completed_reqs = [r for r in my_requests if r.get("status") == "Completed"]
    active_reqs = [r for r in my_requests if r.get("status") in ["Requested", "Accepted"]]
    
    beneficiaries_reached = sum(int(r.get("beneficiary_count", 0)) for r in completed_reqs)
    
    kg_collected = 0.0
    for r in completed_reqs:
        d = don_lookup.get(r.get("donation_id"))
        if d:
            kg_collected += float(d.get("approx_kg", 0.0))
            
    return {
        "total_requests": len(my_requests),
        "active_pickups": len(active_reqs),
        "completed_pickups": len(completed_reqs),
        "beneficiaries_served": beneficiaries_reached,
        "kg_distributed": round(kg_collected, 1)
    }

# --- Input Validation Helpers ---

def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def is_valid_phone(phone: str) -> bool:
    """Validate phone number string."""
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone.strip())
    return len(cleaned) >= 7 and cleaned.isdigit()
