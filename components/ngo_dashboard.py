"""
FoodBridge - NGO Dashboard Component
Empowers verified NGOs and charity food banks to search available surplus food,
submit collection requests with safety guarantees, and track pickups.
"""

from datetime import datetime, timedelta
import streamlit as st
import config
import database as db
import utils
from components.styles import render_html

def render_ngo_dashboard(ngo_user: dict):
    """Render the primary dashboard for NGOs / Charitable Organizations."""
    utils.auto_update_expired_donations()
    
    # 1. Header Banner
    render_html(
        f"""
        <div class="fb-hero-banner">
            <div>
                <h1 class="fb-hero-title">NGO Food Rescue Dashboard 🤝</h1>
                <div class="fb-hero-sub">Welcome back, <strong>{ngo_user['name']}</strong> ({ngo_user.get('organization', 'Charitable NGO')})</div>
            </div>
            <div style="text-align: right; font-size: 0.95rem; background: rgba(255,255,255,0.15); padding: 0.6rem 1.2rem; border-radius: 10px;">
                <div>📍 {ngo_user.get('city', 'Bangalore')}</div>
                <div style="color: #d1e7dd; font-size: 0.85rem;">Reg ID: {ngo_user.get('ngo_reg_number', 'Verified NGO')}</div>
            </div>
        </div>
        """
    )
    
    # 2. Key Metrics Row
    metrics = utils.get_ngo_metrics(ngo_user["id"])
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">📋</div>
                <div class="fb-metric-value">{metrics['total_requests']}</div>
                <div class="fb-metric-label">Total Requests</div>
            </div>
            """
        )
    with col2:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🚚</div>
                <div class="fb-metric-value">{metrics['active_pickups']}</div>
                <div class="fb-metric-label">Active / In Transit</div>
            </div>
            """
        )
    with col3:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">✅</div>
                <div class="fb-metric-value">{metrics['completed_pickups']}</div>
                <div class="fb-metric-label">Completed Pickups</div>
            </div>
            """
        )
    with col4:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">👥</div>
                <div class="fb-metric-value">{metrics['beneficiaries_served']}</div>
                <div class="fb-metric-label">People Fed</div>
            </div>
            """
        )
    with col5:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🥦</div>
                <div class="fb-metric-value">{metrics['kg_distributed']} kg</div>
                <div class="fb-metric-label">Food Distributed</div>
            </div>
            """
        )
        
    st.write("") # spacing
    
    # 3. Main Action Tabs
    tab_browse, tab_my_requests, tab_safety = st.tabs([
        "🍲 Browse Available Food",
        "📦 My Requests & Pickups",
        "🛡️ NGO Safe Handling Protocol"
    ])
    
    with tab_browse:
        render_browse_food_tab(ngo_user)
        
    with tab_my_requests:
        render_ngo_requests_tab(ngo_user)
        
    with tab_safety:
        render_ngo_safety_tab()


def render_browse_food_tab(ngo_user: dict):
    """View and search available food donations with expiry check and atomic claiming."""
    st.subheader("Available Surplus Food Listings")
    st.caption("Browse food currently available for collection. Food items near expiration are highlighted in yellow.")
    
    donations = db.get_donations()
    # Filter only available items or expired for visibility
    available_items = [d for d in donations if d.get("status") == "Available"]
    
    # Search & Filters
    col_s1, col_s2, col_s3, col_s4 = st.columns([2, 1, 1, 1])
    with col_s1:
        search_kw = st.text_input("🔍 Search Food or Donor", placeholder="e.g. Biryani, Bakery, Green Leaf...", key="ngo_search")
    with col_s2:
        category_filter = st.selectbox("Category", ["All Categories"] + config.FOOD_CATEGORIES, key="ngo_cat")
    with col_s3:
        dietary_filter = st.selectbox("Dietary", ["All Types"] + config.DIETARY_TYPES, key="ngo_diet")
    with col_s4:
        sort_by = st.selectbox("Sort By", ["Expiring Soonest", "Recently Posted", "Highest Quantity"], key="ngo_sort")
        
    filtered = available_items
    if category_filter != "All Categories":
        filtered = [d for d in filtered if d.get("category") == category_filter]
    if dietary_filter != "All Types":
        filtered = [d for d in filtered if d.get("dietary") == dietary_filter]
    if search_kw:
        sk = search_kw.strip().lower()
        filtered = [
            d for d in filtered
            if sk in d.get("title", "").lower() 
            or sk in d.get("donor_name", "").lower()
            or sk in d.get("donor_org", "").lower()
            or sk in d.get("city", "").lower()
        ]
        
    # Sort
    if sort_by == "Expiring Soonest":
        filtered.sort(key=lambda x: x.get("expiry_time", "9999"))
    elif sort_by == "Recently Posted":
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_by == "Highest Quantity":
        filtered.sort(key=lambda x: float(x.get("quantity", 0)), reverse=True)
        
    st.write(f"Found **{len(filtered)}** available donation(s) ready for collection.")
    
    if not filtered:
        st.info("No surplus food matches your current search filters. Check back soon or broaden your search!")
        return
        
    # Render food cards
    for item in filtered:
        item_id = item["id"]
        cat = item.get("category", "Cooked Meals")
        cat_icon = config.CATEGORY_ICONS.get(cat, "🍲")
        exp_badge = utils.time_remaining_badge(item.get("expiry_time", ""))
        
        # Check if item is expired
        item_is_expired = exp_badge["is_expired"] or utils.is_expired(item.get("expiry_time", ""))
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card">
                    <div class="fb-food-card-header">
                        <div>
                            <h3 class="fb-food-title">{cat_icon} {item.get('title')}</h3>
                            <div class="fb-food-meta">
                                <span class="fb-food-meta-item">🏢 <strong>{item.get('donor_org')}</strong> ({item.get('donor_name')})</span>
                                <span class="fb-food-meta-item">📦 <strong>{item.get('quantity')} {item.get('unit')}</strong> (~{item.get('approx_kg')} kg)</span>
                                <span class="fb-food-meta-item">🥗 {item.get('dietary')}</span>
                                <span class="fb-food-meta-item">📍 {item.get('city')}</span>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem;">
                            <span class="fb-badge fb-badge-available">🟢 Available</span>
                            <span class="fb-expiry-badge fb-expiry-{exp_badge['urgency']}">⏳ {exp_badge['text']}</span>
                        </div>
                    </div>
                    <div class="fb-food-subcard">
                        <div><strong>Pickup Address:</strong> {item.get('pickup_address')}</div>
                        <div><strong>Storage Condition:</strong> {item.get('storage')} | <strong>Prepared at:</strong> {item.get('cooked_time')}</div>
                        {f"<div><strong>Special Instructions:</strong> {item.get('instructions')}</div>" if item.get('instructions') else ""}
                    </div>
                </div>
                """
            )
            
            # Interactive Request Expander / Action Form
            if item_is_expired:
                st.error("⚠️ This donation has passed its safe consumption time and cannot be requested.")
            else:
                with st.expander(f"🤝 Request to Collect: {item.get('title')}", expanded=False):
                    st.markdown("##### Schedule Pickup Details")
                    with st.form(f"claim_form_{item_id}"):
                        rc1, rc2 = st.columns(2)
                        with rc1:
                            # Default pickup in 2 hours
                            default_pickup = datetime.now() + timedelta(hours=2)
                            pickup_date = st.date_input("Planned Pickup Date *", value=default_pickup.date(), key=f"pdate_{item_id}")
                            pickup_time = st.time_input("Estimated Arrival Time *", value=default_pickup.time(), key=f"ptime_{item_id}")
                        with rc2:
                            transport_type = st.selectbox(
                                "Transport / Carrier Type *",
                                [
                                    "Insulated Cold/Hot Boxes in Van",
                                    "Dedicated Food Transport Vehicle",
                                    "Volunteer Car with Sanitized Crates",
                                    "Two-Wheeler with Thermal Delivery Bag"
                                ],
                                key=f"trans_{item_id}"
                            )
                            beneficiary_count = st.number_input(
                                "Target Beneficiaries Count (People Fed) *",
                                min_value=1,
                                max_value=5000,
                                value=int(item.get("quantity", 20)),
                                step=1,
                                key=f"ben_{item_id}"
                            )
                            
                        pickup_notes = st.text_input(
                            "Pickup Coordination Notes",
                            placeholder="e.g. Volunteer Driver: Mohan (KA-01-AB-1234), arriving via induction dock.",
                            key=f"notes_{item_id}"
                        )
                        
                        safety_agree = st.checkbox(
                            "I confirm that our team will use clean food-grade transport and distribute this food within safe temperature thresholds.",
                            value=False,
                            key=f"safe_ngo_{item_id}"
                        )
                        
                        submit_request = st.form_submit_button("🚀 Submit Donation Request", use_container_width=True)
                        
                        if submit_request:
                            if not safety_agree:
                                st.error("Please confirm safe handling agreement before requesting.")
                            else:
                                pickup_dt_str = f"{pickup_date.strftime('%Y-%m-%d')} {pickup_time.strftime('%H:%M')}"
                                
                                # Call atomic claim function
                                ok, msg = utils.claim_donation(
                                    donation_id=item_id,
                                    ngo_user=ngo_user,
                                    pickup_time_estimate=pickup_dt_str,
                                    transport_type=transport_type,
                                    beneficiary_count=beneficiary_count,
                                    notes=pickup_notes
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
            st.write("") # spacing


def render_ngo_requests_tab(ngo_user: dict):
    """View and manage all requests submitted by this NGO."""
    requests = db.get_requests()
    donations = db.get_donations()
    don_lookup = {d["id"]: d for d in donations}
    
    my_requests = [r for r in requests if r.get("ngo_id") == ngo_user["id"]]
    
    if not my_requests:
        st.info("You haven't requested any food donations yet. Switch to the **'🍲 Browse Available Food'** tab to claim surplus food.")
        return
        
    # Status filter
    status_filter = st.selectbox(
        "Filter by Status",
        ["All Requests", "Requested (Pending Donor Approval)", "Accepted (Ready for Pickup)", "Completed", "Cancelled"],
        index=0,
        key="ngo_req_filter"
    )
    
    filtered_reqs = my_requests
    if status_filter == "Requested (Pending Donor Approval)":
        filtered_reqs = [r for r in filtered_reqs if r.get("status") == "Requested"]
    elif status_filter == "Accepted (Ready for Pickup)":
        filtered_reqs = [r for r in filtered_reqs if r.get("status") == "Accepted"]
    elif status_filter == "Completed":
        filtered_reqs = [r for r in filtered_reqs if r.get("status") == "Completed"]
    elif status_filter == "Cancelled":
        filtered_reqs = [r for r in filtered_reqs if r.get("status") == "Cancelled"]
        
    st.write(f"Showing **{len(filtered_reqs)}** request(s)")
    
    for req in filtered_reqs:
        don = don_lookup.get(req.get("donation_id"), {})
        status = req.get("status", "Requested")
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card" style="border-left: 5px solid {config.STATUS_COLORS.get(status, {}).get('border', '#198754')};">
                    <div class="fb-food-card-header">
                        <div>
                            <h3 class="fb-food-title">🍲 {don.get('title', 'Food Listing')}</h3>
                            <div class="fb-food-meta" style="margin-top: 0.3rem;">
                                <span class="fb-food-meta-item">🏢 <strong>Donor:</strong> {don.get('donor_org')} ({don.get('donor_name')})</span>
                                <span class="fb-food-meta-item">📞 {don.get('donor_phone')}</span>
                                <span class="fb-food-meta-item">📦 {don.get('quantity')} {don.get('unit')}</span>
                            </div>
                        </div>
                        <span class="fb-badge fb-badge-{status.lower()}">{status}</span>
                    </div>
                    <div class="fb-food-subcard" style="margin-top: 0.5rem;">
                        <div>📍 <strong>Pickup Location:</strong> {don.get('pickup_address', 'Address on file')}</div>
                        <div>⏰ <strong>Scheduled Pickup:</strong> {req.get('pickup_time_estimate')}</div>
                        <div>👥 <strong>Beneficiaries:</strong> {req.get('beneficiary_count')} people | <strong>Transport:</strong> {req.get('transport_type')}</div>
                        {f"<div>💬 <strong>Notes:</strong> {req.get('notes')}</div>" if req.get('notes') else ""}
                    </div>
                </div>
                """
            )
            
            c_btn1, c_btn2, _ = st.columns([1.5, 1.2, 2])
            
            if status == "Accepted":
                with c_btn1:
                    if st.button("✅ Confirm Food Received / Complete", key=f"ngo_comp_{req['id']}", use_container_width=True):
                        ok, msg = utils.update_request_status(req["id"], "Completed", ngo_user)
                        if ok:
                            st.success("🎉 Pickup recorded as completed! Meals added to your impact statistics.")
                            st.rerun()
                        else:
                            st.error(msg)
            elif status == "Requested":
                with c_btn2:
                    if st.button("❌ Cancel Request", key=f"ngo_cancel_{req['id']}", use_container_width=True):
                        ok, msg = utils.update_request_status(req["id"], "Cancelled", ngo_user)
                        if ok:
                            st.info("Request cancelled. The donation has been returned to the available pool.")
                            st.rerun()
            st.write("") # spacing


def render_ngo_safety_tab():
    """Display safety procedures tailored for NGO collection & distribution teams."""
    st.subheader("🛡️ NGO Safe Food Transportation & Distribution Checklist")
    render_html(
        """
        When collecting and distributing surplus food, adherence to safety standards protects 
        vulnerable beneficiaries. Review these golden rules:
        
        <div class="fb-info-box">
            <h4>🚚 1. Rapid Transport & Cold Chain</h4>
            <ul>
                <li><strong>Hot Food:</strong> Transport in pre-warmed thermal insulated cambros. Must be consumed within 2 hours of pickup.</li>
                <li><strong>Cold / Perishable Food:</strong> Must remain refrigerated below 5°C with ice gel packs during transit.</li>
                <li>Never leave collected food in an unventilated vehicle exposed to direct sunlight.</li>
            </ul>
        </div>
        
        <div class="fb-warning-box">
            <h4>🔍 2. Receiving Inspection (Sensory Check)</h4>
            <ul>
                <li><strong>Visual Check:</strong> Check for signs of discoloration, mold, or improper sealed packaging.</li>
                <li><strong>Odor Check:</strong> Any off-odor or sourness indicates bacterial spoilage; discard immediately.</li>
                <li><strong>Packaging:</strong> Reject food packed in open, non-food-grade containers or chemical containers.</li>
            </ul>
        </div>
        
        <div class="fb-info-box">
            <h4>🍽️ 3. Safe Serving Guidelines</h4>
            <ul>
                <li>Distribution volunteers must wear clean gloves, hairnets, and wash hands thoroughly.</li>
                <li>Serve hot food piping hot or freshly re-heated to at least 74°C (165°F).</li>
                <li>Never mix fresh batches with previously served leftovers.</li>
            </ul>
        </div>
        """
    )
