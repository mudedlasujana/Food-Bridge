"""
FoodBridge – Food Waste Management and Donation Platform
Main Streamlit Application Entrypoint

Connects food donors (restaurants, hotels, bakeries, individuals) with NGOs 
to donate surplus food and eradicate food wastage.
"""

from datetime import datetime
import streamlit as st
import config
import database as db
import auth
import utils
from components import styles, donor_dashboard, ngo_dashboard, admin_dashboard, food_safety

# 1. Page Configuration
st.set_page_config(
    page_title=f"{config.APP_NAME} – Food Waste Management & Donation Platform",
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Theme State Initialization
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# 3. Apply Custom Dynamic Theme Styles (Light or Dark)
styles.apply_custom_styles(theme_mode=st.session_state.theme_mode)

# 4. System Initialization
auth.init_session_state()
db.seed_sample_data(force=False)
utils.auto_update_expired_donations()


def main():
    # Render Sidebar (with Theme Toggle & Navigation)
    render_sidebar()

    # Route based on session state and active navigation
    logged_in = st.session_state.logged_in
    current_user = st.session_state.current_user
    nav = st.session_state.active_nav

    if logged_in and current_user:
        # Route to role-specific dashboard
        role = current_user.get("role")
        if nav == "Food Safety":
            food_safety.render_food_safety_page()
        elif role == config.ROLE_DONOR:
            donor_dashboard.render_donor_dashboard(current_user)
        elif role == config.ROLE_NGO:
            ngo_dashboard.render_ngo_dashboard(current_user)
        elif role == config.ROLE_ADMIN:
            admin_dashboard.render_admin_dashboard(current_user)
        else:
            st.error("Unknown user role. Please log out and try again.")
    else:
        # Public Pages
        if nav == "Home":
            render_home_page()
        elif nav == "Login":
            render_login_page()
        elif nav == "Register":
            render_register_page()
        elif nav == "Food Safety":
            food_safety.render_food_safety_page()
        else:
            render_home_page()


def render_sidebar():
    """Render consistent sidebar with branding, theme switcher, navigation, and quick demo switchers."""
    with st.sidebar:
        # App Branding Header
        styles.render_html(
            f"""
            <div class="fb-sidebar-logo">
                <span style="font-size: 2.2rem;">{config.APP_ICON}</span>
                <div>
                    <h2 class="fb-sidebar-title">{config.APP_NAME}</h2>
                    <div style="font-size: 0.8rem; color: #10B981; font-weight: 600;">Surplus Food Rescue Network</div>
                </div>
            </div>
            """
        )

        # ☀️ Light Mode / 🌙 Dark Mode Toggle
        st.write("##### 🎨 Display Theme")
        theme_index = 0 if st.session_state.theme_mode == "Light" else 1
        theme_toggle = st.radio(
            "Select Display Theme:",
            ["☀️ Light Mode", "🌙 Dark Mode"],
            index=theme_index,
            horizontal=True,
            label_visibility="collapsed",
            key="theme_selector"
        )
        selected_theme = "Dark" if "Dark" in theme_toggle else "Light"
        if selected_theme != st.session_state.theme_mode:
            st.session_state.theme_mode = selected_theme
            st.rerun()

        st.markdown("---")

        logged_in = st.session_state.logged_in
        current_user = st.session_state.current_user

        if logged_in and current_user:
            # Active User Card
            u_role = current_user.get("role", "User")
            
            styles.render_html(
                f"""
                <div class="fb-user-badge">
                    <div style="font-size: 0.8rem; text-transform: uppercase; font-weight: 700; opacity: 0.7;">Logged In As</div>
                    <div style="font-size: 1.05rem; font-weight: 700; margin-top: 2px;">{current_user['name']}</div>
                    <div style="font-size: 0.85rem; opacity: 0.8;">{current_user.get('organization', '')}</div>
                    <div style="margin-top: 8px;">
                        <span class="fb-badge fb-badge-available">Role: {u_role}</span>
                    </div>
                </div>
                """
            )

            # Navigation Options for Logged In User
            st.write("### 🧭 Navigation")
            if st.button("🏠 My Dashboard", use_container_width=True, key="sb_dash"):
                st.session_state.active_nav = "Dashboard"
                st.rerun()

            if st.button("🛡️ Food Safety Rules", use_container_width=True, key="sb_safety"):
                st.session_state.active_nav = "Food Safety"
                st.rerun()

            st.write("")
            if st.button("🚪 Log Out", use_container_width=True, key="sb_logout"):
                auth.logout_user()
                st.rerun()

        else:
            # Public Navigation
            st.write("### 🧭 Navigation")
            nav_options = ["🏠 Home & Mission", "🔑 Sign In", "📝 Register New Account", "🛡️ Food Safety Standards"]
            nav_keys = ["Home", "Login", "Register", "Food Safety"]

            current_idx = 0
            if st.session_state.active_nav in nav_keys:
                current_idx = nav_keys.index(st.session_state.active_nav)

            selected = st.radio(
                "Go to page:",
                nav_options,
                index=current_idx,
                label_visibility="collapsed"
            )

            # Sync selection
            new_nav = nav_keys[nav_options.index(selected)]
            if new_nav != st.session_state.active_nav:
                st.session_state.active_nav = new_nav
                st.rerun()

        # Quick Demo Role Switcher (For Evaluation & Testing)
        st.markdown("---")
        st.write("##### ⚡ Quick Demo Switcher")
        st.caption("Instantly log in as any role for testing:")
        
        c_d1, c_d2 = st.columns(2)
        with c_d1:
            if st.button("👨‍🍳 Donor", help="Chef Ramesh (Green Leaf Bistro)", use_container_width=True):
                auth.quick_switch_user("bistro@greenleaf.com")
                st.rerun()
        with c_d2:
            if st.button("🏢 NGO", help="Hope & Hunger Food Bank", use_container_width=True):
                auth.quick_switch_user("contact@hopefoodbank.org")
                st.rerun()

        if st.button("🛡️ Platform Admin", help="System Administrator", use_container_width=True):
            auth.quick_switch_user("admin@foodbridge.org")
            st.rerun()

        st.caption("Default test password: `demo1234` | Admin: `admin123`")


def render_home_page():
    """Render public Landing / Mission page showcasing live community impact and active food."""
    kpis = utils.get_platform_metrics()

    # Hero Banner
    styles.render_html(
        f"""
        <div class="fb-hero-banner">
            <div>
                <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">
                    🌱 Zero Food Waste Platform
                </span>
                <h1 class="fb-hero-title" style="margin-top: 0.8rem;">Bridge the Gap Between Surplus Food & Hunger</h1>
                <div class="fb-hero-sub">
                    Connecting restaurants, hotels, bakeries, and individuals directly with local NGOs 
                    to feed communities and prevent greenhouse gas emissions from food waste.
                </div>
            </div>
        </div>
        """
    )

    # Call to Action Row
    col_cta1, col_cta2, col_cta3 = st.columns([1.5, 1.5, 1])
    with col_cta1:
        if st.button("🍲 I Have Surplus Food (Donate Now)", use_container_width=True, key="home_donate_cta"):
            st.session_state.active_nav = "Register"
            st.rerun()
    with col_cta2:
        if st.button("🤝 I Am an NGO (Claim Surplus Food)", use_container_width=True, key="home_ngo_cta"):
            st.session_state.active_nav = "Register"
            st.rerun()
    with col_cta3:
        if st.button("🔑 Sign In", use_container_width=True, key="home_login_cta"):
            st.session_state.active_nav = "Login"
            st.rerun()

    st.write("") # spacing

    # Live Impact Metrics Row
    st.write("### 🌍 Live Platform Impact")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        styles.render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🍽️</div>
                <div class="fb-metric-value">{kpis['total_meals_saved']}</div>
                <div class="fb-metric-label">Meals Provided</div>
            </div>
            """
        )
    with col2:
        styles.render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">⚖️</div>
                <div class="fb-metric-value">{kpis['total_kg_rescued']} kg</div>
                <div class="fb-metric-label">Food Rescued</div>
            </div>
            """
        )
    with col3:
        styles.render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🟢</div>
                <div class="fb-metric-value">{kpis['available_donations']}</div>
                <div class="fb-metric-label">Active Listings</div>
            </div>
            """
        )
    with col4:
        styles.render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">🌱</div>
                <div class="fb-metric-value">{kpis['co2_diverted_kg']} kg</div>
                <div class="fb-metric-label">CO2 Prevented</div>
            </div>
            """
        )
    with col5:
        styles.render_html(
            f"""
            <div class="fb-metric-card">
                <div class="fb-metric-icon">💧</div>
                <div class="fb-metric-value">{int(kpis['water_saved_liters'])} L</div>
                <div class="fb-metric-label">Water Conserved</div>
            </div>
            """
        )

    st.markdown("---")

    # How It Works 3-Step Guide
    st.write("### 🔄 How FoodBridge Operates")
    col_w1, col_w2, col_w3 = st.columns(3)

    with col_w1:
        styles.render_html(
            """
            <div class="fb-food-card" style="text-align: center; border-top: 4px solid #10B981;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">👨‍🍳</div>
                <h4 style="margin: 0;">1. Donors List Surplus</h4>
                <p style="font-size: 0.88rem; opacity: 0.85; margin-top: 0.5rem;">
                    Restaurants, catering halls, bakeries, or individuals log available surplus meals, 
                    fresh produce, or bakery items with safe expiration times.
                </p>
            </div>
            """
        )

    with col_w2:
        styles.render_html(
            """
            <div class="fb-food-card" style="text-align: center; border-top: 4px solid #F59E0B;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🚚</div>
                <h4 style="margin: 0;">2. Verified NGOs Claim</h4>
                <p style="font-size: 0.88rem; opacity: 0.85; margin-top: 0.5rem;">
                    Verified charities and food banks browse real-time listings, submit pickup timelines, 
                    and reserve donations with double-claim prevention.
                </p>
            </div>
            """
        )

    with col_w3:
        styles.render_html(
            """
            <div class="fb-food-card" style="text-align: center; border-top: 4px solid #38BDF8;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">❤️</div>
                <h4 style="margin: 0;">3. Safe Delivery & Impact</h4>
                <p style="font-size: 0.88rem; opacity: 0.85; margin-top: 0.5rem;">
                    Food is transported using temperature-safe containers and served to shelter homes, 
                    daycares, and families in need within hours.
                </p>
            </div>
            """
        )

    st.markdown("---")

    # Preview of Currently Available Food
    st.write("### 🍲 Current Surplus Food Ready for Rescue")
    st.caption("Sign in as a registered NGO to request any of the active listings below.")
    
    donations = db.get_donations()
    available = [d for d in donations if d.get("status") == "Available"][:4]

    if not available:
        st.info("All currently posted food has been matched with NGOs! New listings are posted daily.")
    else:
        grid_cols = st.columns(2)
        for i, item in enumerate(available):
            with grid_cols[i % 2]:
                cat = item.get("category", "Cooked Meals")
                cat_icon = config.CATEGORY_ICONS.get(cat, "🍲")
                exp_badge = utils.time_remaining_badge(item.get("expiry_time", ""))
                
                styles.render_html(
                    f"""
                    <div class="fb-food-card">
                        <div class="fb-food-card-header">
                            <div>
                                <h4 class="fb-food-title">{cat_icon} {item.get('title')}</h4>
                                <div class="fb-food-meta">
                                    <span>🏢 {item.get('donor_org')}</span>
                                    <span>📍 {item.get('city')}</span>
                                    <span>🥗 {item.get('dietary')}</span>
                                </div>
                            </div>
                            <span class="fb-expiry-badge fb-expiry-{exp_badge['urgency']}">⏳ {exp_badge['text']}</span>
                        </div>
                        <div class="fb-food-subcard">
                            <div><strong>Quantity:</strong> {item.get('quantity')} {item.get('unit')} (~{item.get('approx_kg')} kg)</div>
                            <div><strong>Storage:</strong> {item.get('storage')}</div>
                        </div>
                    </div>
                    """
                )


def render_login_page():
    """Render user authentication screen with credentials verification."""
    styles.render_html(
        f"""
        <div class="fb-hero-banner" style="padding: 1.5rem 2rem;">
            <div>
                <h2 class="fb-hero-title">Sign In to {config.APP_NAME} 🔑</h2>
                <div class="fb-hero-sub">Enter your credentials to access your donor, NGO, or administrator dashboard.</div>
            </div>
        </div>
        """
    )

    col_center, col_right = st.columns([1.5, 1])

    with col_center:
        styles.render_html(
            """
            <div class="fb-food-card">
                <h3 style="margin-top: 0;">Account Login</h3>
            </div>
            """
        )

        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="name@organization.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    success, msg = auth.login_user(email, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.write("")
        st.markdown("Don't have an account yet?")
        if st.button("Create New Account", use_container_width=True):
            st.session_state.active_nav = "Register"
            st.rerun()

    with col_right:
        styles.render_html(
            """
            <div class="fb-food-card">
                <h4 style="margin-top: 0;">💡 Quick Test Credentials</h4>
                <p style="font-size: 0.88rem; opacity: 0.8;">You can test the system using any of the pre-configured accounts:</p>
                <div class="fb-food-subcard" style="line-height: 1.7;">
                    <div style="margin-bottom: 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px dashed rgba(128,128,128,0.3);">
                        <strong>👨‍🍳 Donor (Restaurant):</strong><br/>
                        Email: <code>bistro@greenleaf.com</code><br/>
                        Password: <code>demo1234</code>
                    </div>
                    <div style="margin-bottom: 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px dashed rgba(128,128,128,0.3);">
                        <strong>🏢 NGO (Food Bank):</strong><br/>
                        Email: <code>contact@hopefoodbank.org</code><br/>
                        Password: <code>demo1234</code>
                    </div>
                    <div>
                        <strong>🛡️ Admin (System Administrator):</strong><br/>
                        Email: <code>admin@foodbridge.org</code><br/>
                        Password: <code>admin123</code>
                    </div>
                </div>
            </div>
            """
        )


def render_register_page():
    """Render user registration screen with role selection and data validation."""
    styles.render_html(
        f"""
        <div class="fb-hero-banner" style="padding: 1.5rem 2rem;">
            <div>
                <h2 class="fb-hero-title">Join FoodBridge 📝</h2>
                <div class="fb-hero-sub">Register as a Food Donor or Charitable NGO partner to begin saving surplus meals.</div>
            </div>
        </div>
        """
    )

    with st.container():
        role_choice = st.radio(
            "Select Account Type:",
            [f"🍲 {config.ROLE_DONOR} (Restaurant, Bakery, Hotel, Caterer, Individual)", f"🏢 {config.ROLE_NGO} (Charity, Food Bank, Shelter Home)"],
            index=0,
            horizontal=True
        )
        selected_role = config.ROLE_DONOR if "Donor" in role_choice else config.ROLE_NGO

        with st.form("register_form"):
            st.markdown(f"### Register as a **{selected_role}**")
            
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Contact Person Name *", placeholder="e.g. Ramesh Sharma")
                email = st.text_input("Email Address *", placeholder="e.g. contact@domain.com")
            with c2:
                org_name = st.text_input(
                    "Organization / Business Name *" if selected_role == config.ROLE_DONOR else "NGO / Charity Name *",
                    placeholder="e.g. Green Leaf Bistro or Hope Foundation"
                )
                phone = st.text_input("Contact Phone Number *", placeholder="e.g. +91 98765 43210")

            c3, c4 = st.columns(2)
            with c3:
                city = st.text_input("Operating City *", value="Bangalore")
            with c4:
                if selected_role == config.ROLE_DONOR:
                    extra_field = st.selectbox("Donor Business Category *", config.DONOR_TYPES)
                    ngo_reg = ""
                else:
                    ngo_reg = st.text_input("NGO Registration ID / Darpan ID *", placeholder="e.g. NGO-KA-2023-1234")
                    extra_field = ""

            address = st.text_area("Physical Address / Landmark *", placeholder="Street address for food collection / verification", height=70)

            c5, c6 = st.columns(2)
            with c5:
                password = st.text_input("Password (min 6 characters) *", type="password")
            with c6:
                confirm_password = st.text_input("Confirm Password *", type="password")

            terms_agreed = st.checkbox(
                "I agree to follow FoodBridge Food Safety Standards and Ethical Distribution Terms.",
                value=False
            )

            submit_reg = st.form_submit_button(f"Create {selected_role} Account", use_container_width=True)

            if submit_reg:
                # Basic Validation
                if not name.strip() or not email.strip() or not org_name.strip() or not phone.strip():
                    st.error("Please fill in all mandatory fields marked with an asterisk (*).")
                elif not utils.is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif not utils.is_valid_phone(phone):
                    st.error("Please enter a valid phone number.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif password != confirm_password:
                    st.error("Passwords do not match. Please re-enter carefully.")
                elif selected_role == config.ROLE_NGO and not ngo_reg.strip():
                    st.error("Please provide your NGO registration number.")
                elif not terms_agreed:
                    st.error("You must accept the Food Safety and Ethical Terms to join.")
                else:
                    user_payload = {
                        "name": name,
                        "email": email,
                        "password": password,
                        "role": selected_role,
                        "organization": org_name,
                        "phone": phone,
                        "city": city,
                        "address": address,
                        "donor_type": extra_field if selected_role == config.ROLE_DONOR else "",
                        "ngo_reg_number": ngo_reg if selected_role == config.ROLE_NGO else ""
                    }
                    success, msg = auth.register_user(user_payload)
                    if success:
                        st.success(f"{msg} Automatically redirecting to Sign In...")
                        st.session_state.active_nav = "Login"
                        st.rerun()
                    else:
                        st.error(msg)


if __name__ == "__main__":
    main()
