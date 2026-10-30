"""
FoodBridge - Donor Dashboard Component
Empowers food donors (restaurants, hotels, bakeries, individuals) to post surplus food,
track requests, edit or delete listings, and view community impact.
"""

from datetime import datetime, timedelta
import streamlit as st
import config
import database as db
import utils
from components.styles import render_html

def render_donor_dashboard(donor_user: dict):
    """Render the primary dashboard for Food Donors."""
    # Run auto-maintenance on expired donations
    utils.auto_update_expired_donations()
    
    # 1. Header Banner
    render_html(
        f"""
        <div class="fb-hero-banner">
            <div>
                <h1 class="fb-hero-title">Donor Dashboard 🍲</h1>
                <div class="fb-hero-sub">Welcome back, <strong>{donor_user['name']}</strong> ({donor_user.get('organization', 'Individual Donor')})</div>
            </div>
            <div style="text-align: right; font-size: 0.95rem; background: rgba(255,255,255,0.15); padding: 0.6rem 1.2rem; border-radius: 10px;">
                <div>📍 {donor_user.get('city', 'Bangalore')}</div>
                <div style="color: #d1e7dd; font-size: 0.85rem;">Role: {donor_user.get('donor_type', 'Food Donor')}</div>
            </div>
        </div>
        """
    )
    
    # 2. Key Metrics Row
    metrics = utils.get_donor_metrics(donor_user["id"])
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🍱</div>
                <div class="fb-metric-value">{metrics['total_posted']}</div>
                <div class="fb-metric-label">Total Listings</div>
            </div>
            """
        )
    with col2:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🟢</div>
                <div class="fb-metric-value">{metrics['available']}</div>
                <div class="fb-metric-label">Active / Available</div>
            </div>
            """
        )
    with col3:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🚚</div>
                <div class="fb-metric-value">{metrics['in_progress']}</div>
                <div class="fb-metric-label">In Progress</div>
            </div>
            """
        )
    with col4:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🤝</div>
                <div class="fb-metric-value">{metrics['completed']}</div>
                <div class="fb-metric-label">Completed Pickups</div>
            </div>
            """
        )
    with col5:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🌱</div>
                <div class="fb-metric-value">{metrics['kg_diverted']} kg</div>
                <div class="fb-metric-label">Food Saved (~{metrics['meals_provided']} meals)</div>
            </div>
            """
        )
        
    st.write("") # spacing
    
    # 3. Main Action Tabs
    tab_manage, tab_add, tab_requests = st.tabs([
        "📋 My Food Donations",
        "➕ Post New Donation",
        "🤝 Incoming NGO Requests"
    ])
    
    # ==========================================
    # TAB 1: MANAGE DONATIONS
    # ==========================================
    with tab_manage:
        render_manage_donations_tab(donor_user)
        
    # ==========================================
    # TAB 2: POST NEW DONATION
    # ==========================================
    with tab_add:
        render_add_donation_tab(donor_user)
        
    # ==========================================
    # TAB 3: INCOMING REQUESTS
    # ==========================================
    with tab_requests:
        render_donor_requests_tab(donor_user)


def render_add_donation_tab(donor_user: dict):
    """Render form to create a new donation listing with live validation."""
    st.subheader("Post Surplus Food for Donation")
    st.caption("Fill in the details below to notify nearby NGOs about surplus food ready for collection.")
    
    # Instructions Alert
    render_html(
        """
        <div class="fb-info-box">
            <strong>🛡️ Food Safety First:</strong> Only donate food that is freshly prepared, unadulterated, 
            and stored within recommended temperature thresholds. Hot food should be maintained >60°C; 
            perishables must be kept refrigerated <5°C.
        </div>
        """
    )
    
    with st.form("add_donation_form", clear_on_submit=False):
        c1, c2 = st.columns([2, 1])
        with c1:
            title = st.text_input(
                "Food Item / Title *",
                placeholder="e.g., 40 Portions Vegetable Biryani with Raita",
                help="Be descriptive so NGOs can quickly assess suitability."
            )
        with c2:
            category = st.selectbox("Category *", config.FOOD_CATEGORIES, index=0)
            
        c3, c4, c5 = st.columns(3)
        with c3:
            dietary = st.selectbox("Dietary Classification *", config.DIETARY_TYPES, index=0)
        with c4:
            quantity = st.number_input("Quantity *", min_value=1.0, max_value=5000.0, value=20.0, step=1.0)
        with c5:
            unit = st.selectbox("Unit *", config.UNITS, index=0)
            
        c6, c7 = st.columns(2)
        with c6:
            storage = st.selectbox("Storage Requirement *", config.STORAGE_REQUIREMENTS, index=0)
        with c7:
            city = st.text_input("City *", value=donor_user.get("city", "Bangalore"))
            
        # Timestamps
        st.write("##### ⏰ Time & Expiry Tracking")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            cooked_date = st.date_input("Prepared / Cooked Date", value=datetime.now().date())
            cooked_time = st.time_input("Prepared / Cooked Time", value=datetime.now().time())
        with col_t2:
            # Default expiry 8 hours from now
            default_expiry = datetime.now() + timedelta(hours=8)
            expiry_date = st.date_input("Best Before / Expiry Date *", value=default_expiry.date())
            expiry_time = st.time_input("Expiry Time *", value=default_expiry.time())
            
        pickup_address = st.text_area(
            "Pickup Address & Directions *",
            value=donor_user.get("address", ""),
            placeholder="Complete street address, landmarks, and parking/gate instructions",
            height=75
        )
        
        instructions = st.text_input(
            "Packaging & Handover Notes (Optional)",
            placeholder="e.g. Bring own stainless steel containers; ask for Chef Ramesh at reception."
        )
        
        st.markdown("---")
        st.write("##### 🛡️ Quality & Safety Verification")
        safety_checked = st.checkbox(
            "I hereby certify that this food was prepared under hygienic conditions, has been stored safely, "
            "and is wholesome and safe for human consumption as per basic food safety norms.",
            value=False
        )
        
        submitted = st.form_submit_button("🚀 Publish Food Donation Listing", use_container_width=True)
        
        if submitted:
            # Form Validations
            if not title or len(title.strip()) < 5:
                st.error("Please enter a descriptive food title (at least 5 characters).")
                return
            if not pickup_address or len(pickup_address.strip()) < 10:
                st.error("Please provide a complete pickup address (at least 10 characters).")
                return
            if not safety_checked:
                st.error("You must agree to the Food Safety Verification declaration before posting.")
                return
            
            cooked_str = f"{cooked_date.strftime('%Y-%m-%d')} {cooked_time.strftime('%H:%M')}"
            expiry_str = f"{expiry_date.strftime('%Y-%m-%d')} {expiry_time.strftime('%H:%M')}"
            
            # Check expiry is strictly in the future
            exp_dt = utils.parse_datetime(expiry_str)
            if not exp_dt or exp_dt <= datetime.now():
                st.error("The expiry date and time must be set in the future.")
                return
                
            donation_payload = {
                "title": title,
                "category": category,
                "dietary": dietary,
                "quantity": quantity,
                "unit": unit,
                "storage": storage,
                "pickup_address": pickup_address,
                "city": city,
                "cooked_time": cooked_str,
                "expiry_time": expiry_str,
                "instructions": instructions,
                "safety_verified": safety_checked
            }
            
            success, msg = utils.add_new_donation(donor_user, donation_payload)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def render_manage_donations_tab(donor_user: dict):
    """Render donor's listings with filters, status badges, edit, and delete functionality."""
    donations = db.get_donations()
    my_donations = [d for d in donations if d.get("donor_id") == donor_user["id"]]
    
    if not my_donations:
        st.info("You haven't posted any food donations yet. Click on the **'➕ Post New Donation'** tab to create your first listing!")
        return
        
    # Search and Filter Bar
    c_search, c_filter = st.columns([2, 1])
    with c_search:
        search_query = st.text_input("🔍 Search my listings", placeholder="Search by title or category...", key="donor_search")
    with c_filter:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All Statuses", "Available", "Requested", "Accepted", "Completed", "Expired"],
            index=0,
            key="donor_status_filter"
        )
        
    filtered = my_donations
    if status_filter != "All Statuses":
        filtered = [d for d in filtered if d.get("status") == status_filter]
    if search_query:
        q = search_query.strip().lower()
        filtered = [d for d in filtered if q in d.get("title", "").lower() or q in d.get("category", "").lower()]
        
    st.write(f"Showing **{len(filtered)}** donation(s)")
    
    # Check if an edit modal/form is active in session state
    if "editing_donation_id" not in st.session_state:
        st.session_state.editing_donation_id = None
        
    # If user selected an item to edit, render edit form at top
    if st.session_state.editing_donation_id:
        render_edit_donation_form(donor_user, st.session_state.editing_donation_id)
        st.markdown("---")
        
    # Render donation items
    all_requests = db.get_requests()
    
    for item in filtered:
        status = item.get("status", "Available")
        cat = item.get("category", "Cooked Meals")
        cat_icon = config.CATEGORY_ICONS.get(cat, "🍲")
        exp_badge = utils.time_remaining_badge(item.get("expiry_time", ""))
        
        status_style_class = f"fb-badge-{status.lower()}"
        dietary_style_class = f"fb-badge-{item.get('dietary', 'Vegetarian').lower().replace('-', '').replace(' ', '')}"
        expiry_style_class = f"fb-expiry-{exp_badge['urgency']}"
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card">
                    <div class="fb-food-card-header">
                        <div>
                            <h3 class="fb-food-title">{cat_icon} {item.get('title')}</h3>
                            <div class="fb-food-meta" style="margin-top: 0.4rem;">
                                <span class="fb-food-meta-item">📦 <strong>{item.get('quantity')} {item.get('unit')}</strong> (~{item.get('approx_kg')} kg)</span>
                                <span class="fb-food-meta-item">📍 {item.get('city')}</span>
                                <span class="fb-food-meta-item">❄️ {item.get('storage')}</span>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem;">
                            <span class="fb-badge {status_style_class}">{config.STATUS_COLORS.get(status, {}).get('icon', '⚪')} {status}</span>
                            <span class="fb-expiry-badge {expiry_style_class}">⏳ {exp_badge['text']}</span>
                        </div>
                    </div>
                    <div class="fb-food-subcard">
                        <div><strong>Pickup Address:</strong> {item.get('pickup_address')}</div>
                        <div><em>Notes:</em> {item.get('instructions') or 'None provided'}</div>
                    </div>
                </div>
                """
            )
            
            # Interactive action buttons row
            col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
            
            # Show request details if requested or accepted
            if status in ["Requested", "Accepted"]:
                matched_req = next((r for r in all_requests if r.get("donation_id") == item["id"] and r.get("status") in ["Requested", "Accepted"]), None)
                if matched_req:
                    with col_act1:
                        render_html(
                            f"""
                            <div class="fb-food-subcard" style="border: 1px dashed rgba(128, 128, 128, 0.4);">
                                <strong>Claimed by NGO:</strong> {matched_req.get('ngo_org')} ({matched_req.get('ngo_name')})<br/>
                                <strong>Phone:</strong> {matched_req.get('ngo_phone')} | <strong>Est. Pickup:</strong> {matched_req.get('pickup_time_estimate')}
                            </div>
                            """
                        )
                    
                    if status == "Requested":
                        with col_act2:
                            if st.button("✅ Accept Request", key=f"acc_{item['id']}", use_container_width=True):
                                ok, msg = utils.update_request_status(matched_req["id"], "Accepted", donor_user)
                                if ok:
                                    st.success("You accepted the request! The NGO has been notified to proceed with pickup.")
                                    st.rerun()
                                else:
                                    st.error(msg)
                        with col_act3:
                            if st.button("❌ Decline", key=f"dec_{item['id']}", use_container_width=True):
                                ok, msg = utils.update_request_status(matched_req["id"], "Cancelled", donor_user)
                                if ok:
                                    st.warning("Request declined. Food is available for other NGOs.")
                                    st.rerun()
                    elif status == "Accepted":
                        with col_act2:
                            if st.button("🚚 Confirm Handover", key=f"comp_{item['id']}", use_container_width=True):
                                ok, msg = utils.update_request_status(matched_req["id"], "Completed", donor_user)
                                if ok:
                                    st.success("🎉 Food donation completed and marked delivered! Thank you for reducing waste.")
                                    st.rerun()
                                else:
                                    st.error(msg)
            
            # Available items: Allow Edit and Delete
            elif status == "Available":
                with col_act2:
                    if st.button("✏️ Edit", key=f"edit_btn_{item['id']}", use_container_width=True):
                        st.session_state.editing_donation_id = item["id"]
                        st.rerun()
                with col_act3:
                    if st.button("🗑️ Delete", key=f"del_btn_{item['id']}", use_container_width=True):
                        ok, msg = utils.delete_donation(donor_user, item["id"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
            elif status == "Expired":
                with col_act1:
                    st.warning("⚠️ This food listing has expired past safe consumption hours and is archived.")
                with col_act3:
                    if st.button("🗑️ Remove", key=f"del_exp_{item['id']}", use_container_width=True):
                        ok, msg = utils.delete_donation(donor_user, item["id"])
                        st.rerun()
                        
            st.write("") # divider


def render_edit_donation_form(donor_user: dict, donation_id: str):
    """Render inline editing form for a donation."""
    donations = db.get_donations()
    donation = next((d for d in donations if d["id"] == donation_id), None)
    
    if not donation:
        st.session_state.editing_donation_id = None
        return
        
    st.markdown("### ✏️ Edit Food Donation Listing")
    with st.form("edit_donation_form"):
        ec1, ec2 = st.columns([2, 1])
        with ec1:
            title = st.text_input("Title *", value=donation.get("title", ""))
        with ec2:
            current_cat = donation.get("category", config.FOOD_CATEGORIES[0])
            cat_idx = config.FOOD_CATEGORIES.index(current_cat) if current_cat in config.FOOD_CATEGORIES else 0
            category = st.selectbox("Category *", config.FOOD_CATEGORIES, index=cat_idx)
            
        ec3, ec4 = st.columns(2)
        with ec3:
            quantity = st.number_input("Quantity *", min_value=1.0, value=float(donation.get("quantity", 10.0)), step=1.0)
        with ec4:
            current_unit = donation.get("unit", config.UNITS[0])
            unit_idx = config.UNITS.index(current_unit) if current_unit in config.UNITS else 0
            unit = st.selectbox("Unit *", config.UNITS, index=unit_idx)
            
        ec5, ec6 = st.columns(2)
        with ec5:
            current_storage = donation.get("storage", config.STORAGE_REQUIREMENTS[0])
            storage_idx = config.STORAGE_REQUIREMENTS.index(current_storage) if current_storage in config.STORAGE_REQUIREMENTS else 0
            storage = st.selectbox("Storage Requirement *", config.STORAGE_REQUIREMENTS, index=storage_idx)
        with ec6:
            city = st.text_input("City *", value=donation.get("city", "Bangalore"))
            
        address = st.text_area("Pickup Address *", value=donation.get("pickup_address", ""))
        instructions = st.text_input("Notes", value=donation.get("instructions", ""))
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            save_changes = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with btn_c2:
            cancel = st.form_submit_button("❌ Cancel Editing", use_container_width=True)
            
        if save_changes:
            updated = {
                "title": title,
                "category": category,
                "quantity": quantity,
                "unit": unit,
                "storage": storage,
                "city": city,
                "pickup_address": address,
                "instructions": instructions
            }
            ok, msg = utils.edit_donation(donor_user, donation_id, updated)
            if ok:
                st.success(msg)
                st.session_state.editing_donation_id = None
                st.rerun()
            else:
                st.error(msg)
        if cancel:
            st.session_state.editing_donation_id = None
            st.rerun()


def render_donor_requests_tab(donor_user: dict):
    """View all incoming NGO requests across all donations owned by this donor."""
    donations = db.get_donations()
    requests = db.get_requests()
    
    my_donation_ids = {d["id"] for d in donations if d.get("donor_id") == donor_user["id"]}
    don_lookup = {d["id"]: d for d in donations}
    
    my_requests = [r for r in requests if r.get("donation_id") in my_donation_ids]
    
    if not my_requests:
        st.info("No incoming NGO requests at the moment. As soon as an NGO claims your food, it will appear here.")
        return
        
    st.write(f"Total Requests: **{len(my_requests)}**")
    
    for req in my_requests:
        don = don_lookup.get(req.get("donation_id"), {})
        req_status = req.get("status", "Requested")
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card" style="border-left: 4px solid #10B981;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0;">Donation: {don.get('title', 'Unknown Food Item')}</h4>
                            <div class="fb-food-subcard" style="margin-top: 0.6rem;">
                                <strong>Requesting NGO:</strong> {req.get('ngo_org')} ({req.get('ngo_name')})<br/>
                                <strong>Contact Phone:</strong> {req.get('ngo_phone')}<br/>
                                <strong>Target Beneficiaries:</strong> {req.get('beneficiary_count')} people<br/>
                                <strong>Transport Type:</strong> {req.get('transport_type')}<br/>
                                <strong>Estimated Pickup:</strong> {req.get('pickup_time_estimate')}<br/>
                                <em>NGO Notes:</em> {req.get('notes') or 'None'}
                            </div>
                        </div>
                        <span class="fb-badge fb-badge-{req_status.lower()}">{req_status}</span>
                    </div>
                </div>
                """
            )
            
            c_btn1, c_btn2, _ = st.columns([1, 1, 2])
            if req_status == "Requested":
                with c_btn1:
                    if st.button("✅ Accept Request", key=f"req_tab_acc_{req['id']}", use_container_width=True):
                        ok, msg = utils.update_request_status(req["id"], "Accepted", donor_user)
                        st.rerun()
                with c_btn2:
                    if st.button("❌ Decline", key=f"req_tab_dec_{req['id']}", use_container_width=True):
                        ok, msg = utils.update_request_status(req["id"], "Cancelled", donor_user)
                        st.rerun()
            elif req_status == "Accepted":
                with c_btn1:
                    if st.button("🚚 Confirm Food Handover", key=f"req_tab_handover_{req['id']}", use_container_width=True):
                        ok, msg = utils.update_request_status(req["id"], "Completed", donor_user)
                        st.rerun()
            st.write("")
