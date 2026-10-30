"""
FoodBridge - Database Module
Manages reading and writing data to JSON storage files with atomic operations
and automatic seeding of initial sample data.
"""

import json
import os
import shutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
import config

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
DONATIONS_FILE = DATA_DIR / "donations.json"
REQUESTS_FILE = DATA_DIR / "requests.json"

_DB_LOCK = threading.Lock()

def _ensure_dir():
    """Ensure the data directory exists."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

def _read_json(filepath: Path) -> list:
    """Read data safely from a JSON file."""
    _ensure_dir()
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def _write_json(filepath: Path, data: list):
    """Write data atomically to a JSON file to prevent partial write corruption."""
    _ensure_dir()
    temp_file = filepath.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Atomic file replacement
        if os.name == 'nt' and filepath.exists():
            # On Windows, replace can fail if target exists and is open
            try:
                os.replace(temp_file, filepath)
            except OSError:
                shutil.copyfile(temp_file, filepath)
                if temp_file.exists():
                    temp_file.unlink()
        else:
            temp_file.replace(filepath)
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        if temp_file.exists():
            temp_file.unlink()

# --- Public API for Users ---

def get_users() -> list:
    with _DB_LOCK:
        return _read_json(USERS_FILE)

def save_users(users: list):
    with _DB_LOCK:
        _write_json(USERS_FILE, users)

# --- Public API for Donations ---

def get_donations() -> list:
    with _DB_LOCK:
        return _read_json(DONATIONS_FILE)

def save_donations(donations: list):
    with _DB_LOCK:
        _write_json(DONATIONS_FILE, donations)

# --- Public API for Requests ---

def get_requests() -> list:
    with _DB_LOCK:
        return _read_json(REQUESTS_FILE)

def save_requests(requests: list):
    with _DB_LOCK:
        _write_json(REQUESTS_FILE, requests)

# --- Initial Seed / Reset Function ---

def seed_sample_data(force: bool = False):
    """
    Populates sample users, donations, and requests if data is missing or if force=True.
    """
    _ensure_dir()
    
    # Check if data already exists
    if not force and USERS_FILE.exists() and DONATIONS_FILE.exists() and REQUESTS_FILE.exists():
        existing_users = get_users()
        if existing_users:
            return  # Already seeded
    
    import hashlib
    def quick_hash(pwd, salt="foodbridge_salt_2026"):
        return hashlib.sha256(f"{salt}:{pwd}".encode("utf-8")).hexdigest(), salt

    # 1. Users
    admin_hash, admin_salt = quick_hash("admin123")
    demo_hash, demo_salt = quick_hash("demo1234")
    
    sample_users = [
        {
            "id": "usr_admin_001",
            "name": "Platform Admin",
            "email": "admin@foodbridge.org",
            "password_hash": admin_hash,
            "salt": admin_salt,
            "role": config.ROLE_ADMIN,
            "organization": "FoodBridge Operations Central",
            "phone": "+91 98765 00001",
            "city": "Bangalore",
            "address": "100 Innovation Park, Outer Ring Road, Bangalore",
            "donor_type": "",
            "ngo_reg_number": "",
            "is_active": True,
            "created_at": "2026-10-01 10:00:00"
        },
        {
            "id": "usr_donor_001",
            "name": "Chef Ramesh Sharma",
            "email": "bistro@greenleaf.com",
            "password_hash": demo_hash,
            "salt": demo_salt,
            "role": config.ROLE_DONOR,
            "organization": "Green Leaf Gourmet Bistro",
            "donor_type": "Restaurant / Cafe",
            "phone": "+91 98765 43210",
            "city": "Bangalore",
            "address": "14, Indiranagar 100ft Road, Bangalore, Karnataka 560038",
            "ngo_reg_number": "",
            "is_active": True,
            "created_at": "2026-10-10 11:30:00"
        },
        {
            "id": "usr_donor_002",
            "name": "Priya Sen",
            "email": "orders@sunsetbakery.com",
            "password_hash": demo_hash,
            "salt": demo_salt,
            "role": config.ROLE_DONOR,
            "organization": "Sunset Artisanal Bakery",
            "donor_type": "Bakery & Confectionery",
            "phone": "+91 98765 43211",
            "city": "Bangalore",
            "address": "88, Koramangala 4th Block, Bangalore, Karnataka 560034",
            "ngo_reg_number": "",
            "is_active": True,
            "created_at": "2026-10-12 14:15:00"
        },
        {
            "id": "usr_ngo_001",
            "name": "Arun Kumar",
            "email": "contact@hopefoodbank.org",
            "password_hash": demo_hash,
            "salt": demo_salt,
            "role": config.ROLE_NGO,
            "organization": "Hope & Hunger Food Bank",
            "donor_type": "",
            "ngo_reg_number": "NGO-BLR-2021-7789",
            "phone": "+91 98765 88990",
            "city": "Bangalore",
            "address": "45/2, Shanti Nagar Community Hall, Bangalore, Karnataka 560027",
            "is_active": True,
            "created_at": "2026-10-05 09:00:00"
        },
        {
            "id": "usr_ngo_002",
            "name": "Dr. Sunita Rao",
            "email": "seva@annaraksha.org",
            "password_hash": demo_hash,
            "salt": demo_salt,
            "role": config.ROLE_NGO,
            "organization": "Anna Raksha Seva Foundation",
            "donor_type": "",
            "ngo_reg_number": "NGO-BLR-2019-3321",
            "phone": "+91 98765 88991",
            "city": "Bangalore",
            "address": "12, Jayanagar 7th Block, Near Bus Depot, Bangalore 560082",
            "is_active": True,
            "created_at": "2026-10-08 16:45:00"
        }
    ]
    
    # 2. Sample Donations with dynamic timestamps
    now = datetime.now()
    sample_donations = [
        {
            "id": "don_001",
            "donor_id": "usr_donor_001",
            "donor_name": "Chef Ramesh Sharma",
            "donor_org": "Green Leaf Gourmet Bistro",
            "donor_phone": "+91 98765 43210",
            "title": "Fresh Vegetable Dum Biryani & Mirchi Ka Salan",
            "category": "Cooked Meals",
            "dietary": "Vegetarian",
            "quantity": 45,
            "unit": "Plates / Meals",
            "approx_kg": 18.0,
            "storage": "Hot Holding (Above 60°C / 140°F)",
            "pickup_address": "Green Leaf Bistro, 14 Indiranagar 100ft Road, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Packed in thermal food-grade containers. Please collect from the back kitchen gate.",
            "safety_verified": True,
            "status": "Available",
            "claimed_by_ngo_id": None,
            "created_at": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_002",
            "donor_id": "usr_donor_002",
            "donor_name": "Priya Sen",
            "donor_org": "Sunset Artisanal Bakery",
            "donor_phone": "+91 98765 43211",
            "title": "Artisanal Multigrain Sourdough & Croissants",
            "category": "Bakery & Bread",
            "dietary": "Vegetarian",
            "quantity": 30,
            "unit": "Packets / Boxes",
            "approx_kg": 12.0,
            "storage": "Room Temperature (Cool & Dry)",
            "pickup_address": "88, Koramangala 4th Block, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now + timedelta(hours=28)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Individually bagged in eco-friendly paper packaging. Ready for pickup anytime.",
            "safety_verified": True,
            "status": "Available",
            "claimed_by_ngo_id": None,
            "created_at": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_003",
            "donor_id": "usr_donor_001",
            "donor_name": "Chef Ramesh Sharma",
            "donor_org": "Green Leaf Gourmet Bistro",
            "donor_phone": "+91 98765 43210",
            "title": "Farm-Fresh Seasonal Apples & Sweet Oranges",
            "category": "Fruits & Vegetables",
            "dietary": "Vegan",
            "quantity": 25,
            "unit": "Kilograms (kg)",
            "approx_kg": 25.0,
            "storage": "Room Temperature (Cool & Dry)",
            "pickup_address": "Green Leaf Bistro, 14 Indiranagar 100ft Road, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Packed in 5 ventilated crates. Perfect condition surplus from morning shipment.",
            "safety_verified": True,
            "status": "Available",
            "claimed_by_ngo_id": None,
            "created_at": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_004",
            "donor_id": "usr_donor_001",
            "donor_name": "Chef Ramesh Sharma",
            "donor_org": "Green Leaf Gourmet Bistro",
            "donor_phone": "+91 98765 43210",
            "title": "Paneer Butter Masala with Jeera Rice",
            "category": "Cooked Meals",
            "dietary": "Vegetarian",
            "quantity": 35,
            "unit": "Plates / Meals",
            "approx_kg": 14.0,
            "storage": "Refrigerated (Below 5°C / 40°F)",
            "pickup_address": "Green Leaf Bistro, 14 Indiranagar 100ft Road, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Stored in walk-in cold room at 4°C. Please bring insulated carriers.",
            "safety_verified": True,
            "status": "Requested",
            "claimed_by_ngo_id": "usr_ngo_001",
            "created_at": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_005",
            "donor_id": "usr_donor_002",
            "donor_name": "Priya Sen",
            "donor_org": "Sunset Artisanal Bakery",
            "donor_phone": "+91 98765 43211",
            "title": "Fresh Fruit Pastries & Sandwich Breads",
            "category": "Bakery & Bread",
            "dietary": "Vegetarian",
            "quantity": 50,
            "unit": "Plates / Meals",
            "approx_kg": 15.0,
            "storage": "Room Temperature (Cool & Dry)",
            "pickup_address": "88, Koramangala 4th Block, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Packed in standard bakery boxes. Approved by donor for Anna Raksha Foundation pickup.",
            "safety_verified": True,
            "status": "Accepted",
            "claimed_by_ngo_id": "usr_ngo_002",
            "created_at": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_006",
            "donor_id": "usr_donor_001",
            "donor_name": "Chef Ramesh Sharma",
            "donor_org": "Green Leaf Gourmet Bistro",
            "donor_phone": "+91 98765 43210",
            "title": "Dal Makhani & Chapati Packets",
            "category": "Cooked Meals",
            "dietary": "Vegetarian",
            "quantity": 60,
            "unit": "Plates / Meals",
            "approx_kg": 24.0,
            "storage": "Hot Holding (Above 60°C / 140°F)",
            "pickup_address": "Green Leaf Bistro, 14 Indiranagar 100ft Road, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now - timedelta(days=1, hours=18)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Successfully distributed to shelter home.",
            "safety_verified": True,
            "status": "Completed",
            "claimed_by_ngo_id": "usr_ngo_001",
            "created_at": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "don_007",
            "donor_id": "usr_donor_002",
            "donor_name": "Priya Sen",
            "donor_org": "Sunset Artisanal Bakery",
            "donor_phone": "+91 98765 43211",
            "title": "Cream Puffs & Milk Tartlets",
            "category": "Dairy Products",
            "dietary": "Vegetarian",
            "quantity": 20,
            "unit": "Items / Pieces",
            "approx_kg": 4.0,
            "storage": "Refrigerated (Below 5°C / 40°F)",
            "pickup_address": "88, Koramangala 4th Block, Bangalore",
            "city": "Bangalore",
            "cooked_time": (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M"),
            "expiry_time": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
            "instructions": "Time limit passed; marked expired for safety.",
            "safety_verified": True,
            "status": "Expired",
            "claimed_by_ngo_id": None,
            "created_at": (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # 3. Sample Requests matching the donations
    sample_requests = [
        {
            "id": "req_001",
            "donation_id": "don_004",
            "ngo_id": "usr_ngo_001",
            "ngo_name": "Arun Kumar",
            "ngo_org": "Hope & Hunger Food Bank",
            "ngo_phone": "+91 98765 88990",
            "pickup_time_estimate": (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "transport_type": "Insulated Van with Hot Boxes",
            "beneficiary_count": 35,
            "notes": "Will distribute to evening shelter home near MG Road.",
            "status": "Requested",
            "requested_at": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None
        },
        {
            "id": "req_002",
            "donation_id": "don_005",
            "ngo_id": "usr_ngo_002",
            "ngo_name": "Dr. Sunita Rao",
            "ngo_org": "Anna Raksha Seva Foundation",
            "ngo_phone": "+91 98765 88991",
            "pickup_time_estimate": (now + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "transport_type": "Volunteer Cargo Car",
            "beneficiary_count": 50,
            "notes": "For community kitchen distribution in Jayanagar cluster.",
            "status": "Accepted",
            "requested_at": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None
        },
        {
            "id": "req_003",
            "donation_id": "don_006",
            "ngo_id": "usr_ngo_001",
            "ngo_name": "Arun Kumar",
            "ngo_org": "Hope & Hunger Food Bank",
            "ngo_phone": "+91 98765 88990",
            "pickup_time_estimate": (now - timedelta(days=2, hours=-2)).strftime("%Y-%m-%d %H:%M"),
            "transport_type": "Insulated Van",
            "beneficiary_count": 60,
            "notes": "Food received in excellent condition and served at night shelter.",
            "status": "Completed",
            "requested_at": (now - timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": (now - timedelta(days=2, hours=-3)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    save_users(sample_users)
    save_donations(sample_donations)
    save_requests(sample_requests)
    print("FoodBridge sample database initialized successfully.")
