"""
FoodBridge - Administrator Dashboard Component
Provides platform-wide oversight, user management, donation monitoring,
request audit logs, visual Plotly analytics, and data management tools.
"""

from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import config
import database as db
import utils
import auth
from components.styles import render_html

def render_admin_dashboard(admin_user: dict):
    """Render the primary dashboard for Platform Administrators."""
    utils.auto_update_expired_donations()
    
    # 1. Header Banner
    render_html(
        f"""
        <div class="fb-hero-banner" style="background: linear-gradient(135deg, #13653f 0%, #0a3622 100%);">
            <div>
                <h1 class="fb-hero-title">Platform Administration 🛡️</h1>
                <div class="fb-hero-sub">Welcome back, <strong>{admin_user['name']}</strong> | Operations Control & Impact Analytics</div>
            </div>
            <div style="text-align: right; font-size: 0.95rem; background: rgba(255,255,255,0.15); padding: 0.6rem 1.2rem; border-radius: 10px;">
                <div>⚡ System Status: <strong>Operational</strong></div>
                <div style="color: #d1e7dd; font-size: 0.85rem;">Storage: JSON Database</div>
            </div>
        </div>
        """
    )
    
    # 2. Platform KPI Metrics Row
    kpis = utils.get_platform_metrics()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🏢</div>
                <div class="fb-metric-value">{kpis['total_donors']}</div>
                <div class="fb-metric-label">Food Donors</div>
            </div>
            """
        )
    with c2:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🤝</div>
                <div class="fb-metric-value">{kpis['total_ngos']}</div>
                <div class="fb-metric-label">Partner NGOs</div>
            </div>
            """
        )
    with c3:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🍲</div>
                <div class="fb-metric-value">{kpis['total_donations']}</div>
                <div class="fb-metric-label">Total Listings</div>
            </div>
            """
        )
    with c4:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">⚖️</div>
                <div class="fb-metric-value">{kpis['total_kg_rescued']} kg</div>
                <div class="fb-metric-label">Rescued Food</div>
            </div>
            """
        )
    with c5:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🍽️</div>
                <div class="fb-metric-value">{kpis['total_meals_saved']}</div>
                <div class="fb-metric-label">Meals Provided</div>
            </div>
            """
        )
    with c6:
        render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🌱</div>
                <div class="fb-metric-value">{kpis['co2_diverted_kg']} kg</div>
                <div class="fb-metric-label">CO2 Prevented</div>
            </div>
            """
        )
        
    st.write("") # spacing
    
    # 3. Analytics Charts Section (Plotly)
    render_analytics_section()
    
    st.markdown("---")
    
    # 4. Admin Management Tabs
    tab_users, tab_donations, tab_requests, tab_system = st.tabs([
        "👥 User Management",
        "🍲 Donation Management",
        "📝 Request Audit Logs",
        "⚙️ System & Backup"
    ])
    
    with tab_users:
        render_user_management_tab(admin_user)
        
    with tab_donations:
        render_donation_management_tab(admin_user)
        
    with tab_requests:
        render_requests_audit_tab(admin_user)
        
    with tab_system:
        render_system_tools_tab()


def render_analytics_section():
    """Render interactive Plotly charts with custom brand color palette."""
    donations = db.get_donations()
    users = db.get_users()
    
    if not donations:
        st.info("No donation data available to generate charts.")
        return
        
    df_donations = pd.DataFrame(donations)
    
    is_dark = (st.session_state.get("theme_mode", "Light") == "Dark")
    chart_font_color = "#F1F5F9" if is_dark else "#1E293B"
    chart_grid_color = "#23354E" if is_dark else "#E2DDD5"
    
    # Plotly Green / Earth palette
    brand_palette = ["#10B981", "#20c997", "#38BDF8", "#F59E0B", "#A855F7", "#FB923C", "#34D399"]
    
    st.subheader("📊 Platform Analytics & Trends")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 1. Donations by Category Donut Chart
        if "category" in df_donations.columns:
            cat_counts = df_donations["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            
            fig_cat = px.pie(
                cat_counts,
                names="Category",
                values="Count",
                title="<b>Donations by Category</b>",
                hole=0.45,
                color_discrete_sequence=brand_palette
            )
            fig_cat.update_traces(textposition='inside', textinfo='percent+label')
            fig_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans, sans-serif", color=chart_font_color),
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
    with chart_col2:
        # 2. Donation Status Pipeline
        if "status" in df_donations.columns:
            status_counts = df_donations["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            status_colors = {
                "Available": "#10B981",
                "Requested": "#F59E0B",
                "Accepted": "#38BDF8",
                "Completed": "#64748B",
                "Expired": "#F43F5E",
                "Cancelled": "#94A3B8"
            }
            
            fig_status = px.bar(
                status_counts,
                x="Status",
                y="Count",
                title="<b>Donations Status Pipeline</b>",
                color="Status",
                color_discrete_map=status_colors,
                text="Count"
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans, sans-serif", color=chart_font_color),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=chart_grid_color),
                margin=dict(t=40, b=20, l=20, r=20),
                showlegend=False
            )
            st.plotly_chart(fig_status, use_container_width=True)


def render_user_management_tab(admin_user: dict):
    """View, search, toggle status, and delete users."""
    users = db.get_users()
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        search_user = st.text_input("🔍 Search Users", placeholder="Search by name, email, organization, or city...", key="admin_u_search")
    with col_u2:
        role_filter = st.selectbox("Filter by Role", ["All Roles", config.ROLE_DONOR, config.ROLE_NGO, config.ROLE_ADMIN], key="admin_u_role")
        
    filtered_users = users
    if role_filter != "All Roles":
        filtered_users = [u for u in filtered_users if u.get("role") == role_filter]
    if search_user:
        su = search_user.strip().lower()
        filtered_users = [
            u for u in filtered_users
            if su in u.get("name", "").lower() 
            or su in u.get("email", "").lower()
            or su in u.get("organization", "").lower()
            or su in u.get("city", "").lower()
        ]
        
    st.write(f"Showing **{len(filtered_users)}** user accounts")
    
    # Interactive Table / Cards
    for u in filtered_users:
        u_id = u["id"]
        is_active = u.get("is_active", True)
        u_role = u.get("role", "Donor")
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card" style="padding: 1rem 1.2rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0;">{u.get('name')} <span style="font-size: 0.85rem; font-weight: normal; opacity: 0.7;">({u.get('email')})</span></h4>
                            <div class="fb-food-subcard" style="margin-top: 0.4rem;">
                                🏢 <strong>{u.get('organization', 'N/A')}</strong> | 📍 {u.get('city', 'Bangalore')} | 📞 {u.get('phone', 'N/A')}
                                {f" | <strong>Type:</strong> {u.get('donor_type')}" if u.get('donor_type') else ""}
                                {f" | <strong>Reg ID:</strong> {u.get('ngo_reg_number')}" if u.get('ngo_reg_number') else ""}
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <span class="fb-badge fb-badge-accepted">{u_role}</span>
                            <span class="fb-badge fb-badge-{'available' if is_active else 'expired'}">{'Active' if is_active else 'Deactivated'}</span>
                        </div>
                    </div>
                </div>
                """
            )
            
            # Action buttons for this user
            cu_btn1, cu_btn2, _ = st.columns([1.2, 1.2, 3])
            
            # Prevent admin from deactivating/deleting themselves
            if u["id"] != admin_user["id"]:
                with cu_btn1:
                    toggle_label = "🚫 Deactivate" if is_active else "✅ Reactivate"
                    if st.button(toggle_label, key=f"toggle_u_{u_id}", use_container_width=True):
                        u["is_active"] = not is_active
                        db.save_users(users)
                        st.success(f"Updated status for {u['name']} to {'Active' if u['is_active'] else 'Deactivated'}.")
                        st.rerun()
                with cu_btn2:
                    if st.button("🗑️ Delete User", key=f"del_u_{u_id}", use_container_width=True):
                        users = [item for item in users if item["id"] != u_id]
                        db.save_users(users)
                        st.success(f"Deleted user account {u['name']}.")
                        st.rerun()
            else:
                with cu_btn1:
                    st.caption("🔒 Current Logged-in Admin Account")
                    
            st.write("") # spacing


def render_donation_management_tab(admin_user: dict):
    """View and oversee all donations across the entire platform."""
    donations = db.get_donations()
    
    col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
    with col_d1:
        search_d = st.text_input("🔍 Search Donations", placeholder="Search by title, donor name, or location...", key="admin_d_search")
    with col_d2:
        status_d = st.selectbox("Status Filter", ["All Statuses", "Available", "Requested", "Accepted", "Completed", "Expired", "Cancelled"], key="admin_d_status")
    with col_d3:
        cat_d = st.selectbox("Category Filter", ["All Categories"] + config.FOOD_CATEGORIES, key="admin_d_cat")
        
    filtered_d = donations
    if status_d != "All Statuses":
        filtered_d = [d for d in filtered_d if d.get("status") == status_d]
    if cat_d != "All Categories":
        filtered_d = [d for d in filtered_d if d.get("category") == cat_d]
    if search_d:
        sd = search_d.strip().lower()
        filtered_d = [
            d for d in filtered_d
            if sd in d.get("title", "").lower()
            or sd in d.get("donor_name", "").lower()
            or sd in d.get("donor_org", "").lower()
            or sd in d.get("city", "").lower()
        ]
        
    st.write(f"Total Listings Found: **{len(filtered_d)}**")
    
    for item in filtered_d:
        item_id = item["id"]
        status = item.get("status", "Available")
        exp_badge = utils.time_remaining_badge(item.get("expiry_time", ""))
        
        with st.container():
            render_html(
                f"""
                <div class="fb-food-card" style="padding: 1rem 1.2rem; margin-bottom: 0.6rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0;">{item.get('title')}</h4>
                            <div class="fb-food-subcard" style="margin-top: 0.4rem;">
                                <strong>Donor:</strong> {item.get('donor_org')} ({item.get('donor_name')}) | 📞 {item.get('donor_phone')}<br/>
                                📦 {item.get('quantity')} {item.get('unit')} (~{item.get('approx_kg')} kg) | 🥗 {item.get('dietary')} | 📍 {item.get('city')}<br/>
                                ⏰ <em>Expiry:</em> {item.get('expiry_time')} ({exp_badge['text']})
                            </div>
                        </div>
                        <span class="fb-badge fb-badge-{status.lower()}">{status}</span>
                    </div>
                </div>
                """
            )
            
            # Admin action overrides
            ca_btn1, ca_btn2, _ = st.columns([1.5, 1.5, 3])
            with ca_btn1:
                if status != "Expired" and st.button("⚠️ Force Mark Expired", key=f"force_exp_{item_id}", use_container_width=True):
                    item["status"] = "Expired"
                    db.save_donations(donations)
                    st.rerun()
            with ca_btn2:
                if st.button("🗑️ Delete Listing", key=f"admin_del_{item_id}", use_container_width=True):
                    donations = [d for d in donations if d["id"] != item_id]
                    db.save_donations(donations)
                    st.success("Donation deleted.")
                    st.rerun()
            st.write("")


def render_requests_audit_tab(admin_user: dict):
    """View full audit log of all NGO requests and fulfillment pipeline."""
    requests = db.get_requests()
    donations = db.get_donations()
    don_lookup = {d["id"]: d for d in donations}
    
    st.subheader("📝 Request & Pickup Audit Trail")
    st.caption("Complete history of food claims, assigned vehicles, and delivery statuses.")
    
    if not requests:
        st.info("No requests have been submitted yet.")
        return
        
    df_reqs = []
    for r in requests:
        d = don_lookup.get(r.get("donation_id"), {})
        df_reqs.append({
            "Request ID": r.get("id"),
            "Food Listing": d.get("title", "Unknown"),
            "Donor": d.get("donor_org", "Unknown"),
            "Requesting NGO": r.get("ngo_org", r.get("ngo_name")),
            "Beneficiaries": r.get("beneficiary_count", 0),
            "Scheduled Pickup": r.get("pickup_time_estimate", "N/A"),
            "Transport": r.get("transport_type", "N/A"),
            "Status": r.get("status", "N/A"),
            "Requested At": r.get("requested_at", "N/A")
        })
        
    df = pd.DataFrame(df_reqs)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_system_tools_tab():
    """Tools for exporting database backups and resetting demo data."""
    st.subheader("⚙️ System Tools & Database Utilities")
    
    c_tools1, c_tools2 = st.columns(2)
    
    with c_tools1:
        render_html(
            """
            <div class="fb-food-card">
                <h4 style="margin-top: 0;">📥 Data Export & Backup</h4>
                <p style="font-size: 0.9rem; opacity: 0.8;">Download live database snapshots in JSON format for backup or external auditing.</p>
            </div>
            """
        )
        
        users_json = db.USERS_FILE.read_text(encoding="utf-8") if db.USERS_FILE.exists() else "[]"
        donations_json = db.DONATIONS_FILE.read_text(encoding="utf-8") if db.DONATIONS_FILE.exists() else "[]"
        requests_json = db.REQUESTS_FILE.read_text(encoding="utf-8") if db.REQUESTS_FILE.exists() else "[]"
        
        st.download_button("Download Users (JSON)", users_json, file_name="users_backup.json", mime="application/json")
        st.download_button("Download Donations (JSON)", donations_json, file_name="donations_backup.json", mime="application/json")
        st.download_button("Download Requests (JSON)", requests_json, file_name="requests_backup.json", mime="application/json")
        
    with c_tools2:
        render_html(
            """
            <div class="fb-food-card">
                <h4 style="margin-top: 0;">🔄 Reset Sample Data</h4>
                <p style="font-size: 0.9rem; opacity: 0.8;">Re-seed the platform with fresh demonstration donors, NGOs, food listings, and pickup records.</p>
            </div>
            """
        )
        if st.button("⚠️ Reset & Re-Seed Sample Database", type="secondary"):
            db.seed_sample_data(force=True)
            st.success("Sample database re-seeded successfully! All test accounts and donations are restored.")
            st.rerun()
