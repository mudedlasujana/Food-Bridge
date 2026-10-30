"""
FoodBridge - UI Styles & Theme CSS
Supports both Light Mode (Forest Green, Cream, and White)
and Dark Mode (Emerald Green, Deep Slate, and Charcoal).
"""

import textwrap
import streamlit as st

def render_html(html_str: str, **kwargs):
    """
    Safely render HTML in Streamlit.
    Dedent eliminates any 4+ leading space indentation so Markdown parsers
    NEVER mistakenly convert HTML cards/blocks into <pre><code> code snippets.
    """
    clean_html = textwrap.dedent(html_str).strip()
    st.markdown(clean_html, unsafe_allow_html=True)

def apply_custom_styles(theme_mode: str = "Light"):
    """
    Inject high-specificity CSS rules tailored to the selected theme.
    Ensures colors are vibrant, legible, and consistent across all browsers and devices.
    """
    is_dark = (theme_mode == "Dark")

    if is_dark:
        # Dark Theme Palette
        bg_main = "#0B131F"
        bg_sub = "#111C2D"
        card_bg = "#152238"
        card_sub_bg = "#1A2942"
        border_color = "#23354E"
        border_highlight = "#10B981"
        text_title = "#34D399"
        text_primary = "#F1F5F9"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        hero_grad = "linear-gradient(135deg, #064E3B 0%, #022C22 100%)"
        hero_border = "1px solid #059669"
        hero_title = "#FFFFFF"
        hero_sub = "#A7F3D0"
        btn_bg = "#10B981"
        btn_hover = "#059669"
        btn_text = "#FFFFFF"
        badge_avail_bg = "#064E3B"
        badge_avail_border = "#10B981"
        badge_avail_text = "#6EE7B7"
        badge_req_bg = "#451A03"
        badge_req_border = "#F59E0B"
        badge_req_text = "#FCD34D"
        badge_acc_bg = "#0C4A6E"
        badge_acc_border = "#38BDF8"
        badge_acc_text = "#BAE6FD"
        badge_comp_bg = "#1E293B"
        badge_comp_border = "#64748B"
        badge_comp_text = "#CBD5E1"
        badge_exp_bg = "#4C0519"
        badge_exp_border = "#F43F5E"
        badge_exp_text = "#FDA4AF"
        badge_canc_bg = "#1E293B"
        badge_canc_border = "#475569"
        badge_canc_text = "#94A3B8"
        box_info_bg = "#064E3B"
        box_info_text = "#D1FAE5"
        box_info_border = "#10B981"
        box_warn_bg = "#451A03"
        box_warn_text = "#FEF3C7"
        box_warn_border = "#F59E0B"
        metric_value = "#34D399"
    else:
        # Light Theme Palette (Forest Green #198754, Warm Cream #FAF7F2, Clean White)
        bg_main = "#FAF7F2"
        bg_sub = "#F3EFE6"
        card_bg = "#FFFFFF"
        card_sub_bg = "#F8FAFC"
        border_color = "#E2DDD5"
        border_highlight = "#198754"
        text_title = "#0f5132"
        text_primary = "#1E293B"
        text_secondary = "#475569"
        text_muted = "#64748B"
        hero_grad = "linear-gradient(135deg, #198754 0%, #0f5132 100%)"
        hero_border = "none"
        hero_title = "#FFFFFF"
        hero_sub = "#D1E7DD"
        btn_bg = "#198754"
        btn_hover = "#146c43"
        btn_text = "#FFFFFF"
        badge_avail_bg = "#E8F5E9"
        badge_avail_border = "#4CAF50"
        badge_avail_text = "#1B5E20"
        badge_req_bg = "#FFF8E1"
        badge_req_border = "#FFB300"
        badge_req_text = "#B78103"
        badge_acc_bg = "#E1F5FE"
        badge_acc_border = "#03A9F4"
        badge_acc_text = "#0277BD"
        badge_comp_bg = "#ECEFF1"
        badge_comp_border = "#78909C"
        badge_comp_text = "#37474F"
        badge_exp_bg = "#FFEBEE"
        badge_exp_border = "#E53935"
        badge_exp_text = "#C62828"
        badge_canc_bg = "#F5F5F5"
        badge_canc_border = "#9E9E9E"
        badge_canc_text = "#616161"
        box_info_bg = "#E8F5E9"
        box_info_text = "#1B5E20"
        box_info_border = "#198754"
        box_warn_bg = "#FFF8E1"
        box_warn_text = "#856404"
        box_warn_border = "#FFB300"
        metric_value = "#0f5132"

    css_code = f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}

    /* Global App Background */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}

    header[data-testid="stHeader"] {{
        background-color: {bg_main} !important;
    }}

    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {bg_sub} !important;
        border-right: 1px solid {border_color} !important;
    }}

    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_title} !important;
        font-weight: 700 !important;
    }}

    p, span, label, div {{
        color: inherit;
    }}

    /* --- Hero / Welcome Banner --- */
    .fb-hero-banner {{
        background: {hero_grad} !important;
        border: {hero_border} !important;
        color: {hero_title} !important;
        padding: 2.2rem 2rem !important;
        border-radius: 16px !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }}

    .fb-hero-title {{
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: {hero_title} !important;
        letter-spacing: -0.5px !important;
    }}

    .fb-hero-sub {{
        font-size: 1.05rem !important;
        color: {hero_sub} !important;
        margin-top: 0.4rem !important;
        font-weight: 500 !important;
    }}

    /* --- Metric Cards --- */
    .fb-metric-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08) !important;
        text-align: center !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
        margin-bottom: 0.8rem !important;
    }}

    .fb-metric-card:hover {{
        transform: translateY(-3px) !important;
        border-color: {border_highlight} !important;
        box-shadow: 0 10px 18px -3px rgba(0, 0, 0, 0.15) !important;
    }}

    .fb-metric-icon {{
        font-size: 1.8rem !important;
        margin-bottom: 0.3rem !important;
        display: inline-block !important;
    }}

    .fb-metric-value {{
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: {metric_value} !important;
        line-height: 1.2 !important;
    }}

    .fb-metric-label {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-top: 0.3rem !important;
    }}

    /* --- Food Listing Card --- */
    .fb-food-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 14px !important;
        padding: 1.4rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.2s ease-in-out !important;
        color: {text_primary} !important;
    }}

    .fb-food-card:hover {{
        border-color: {border_highlight} !important;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15) !important;
    }}

    .fb-food-card-header {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        margin-bottom: 0.8rem !important;
    }}

    .fb-food-title {{
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: {text_title} !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }}

    .fb-food-meta {{
        color: {text_secondary} !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.6rem !important;
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 1rem !important;
    }}

    .fb-food-meta-item {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.3rem !important;
        color: {text_secondary} !important;
    }}

    .fb-food-subcard {{
        background-color: {card_sub_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
        color: {text_secondary} !important;
    }}

    /* --- Status Badges --- */
    .fb-badge {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.35rem !important;
        padding: 0.35rem 0.8rem !important;
        border-radius: 9999px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
    }}

    .fb-badge-available {{
        background-color: {badge_avail_bg} !important;
        color: {badge_avail_text} !important;
        border: 1px solid {badge_avail_border} !important;
    }}

    .fb-badge-requested {{
        background-color: {badge_req_bg} !important;
        color: {badge_req_text} !important;
        border: 1px solid {badge_req_border} !important;
    }}

    .fb-badge-accepted {{
        background-color: {badge_acc_bg} !important;
        color: {badge_acc_text} !important;
        border: 1px solid {badge_acc_border} !important;
    }}

    .fb-badge-completed {{
        background-color: {badge_comp_bg} !important;
        color: {badge_comp_text} !important;
        border: 1px solid {badge_comp_border} !important;
    }}

    .fb-badge-expired {{
        background-color: {badge_exp_bg} !important;
        color: {badge_exp_text} !important;
        border: 1px solid {badge_exp_border} !important;
    }}

    .fb-badge-cancelled {{
        background-color: {badge_canc_bg} !important;
        color: {badge_canc_text} !important;
        border: 1px solid {badge_canc_border} !important;
    }}

    /* Expiry Badges */
    .fb-expiry-badge {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.3rem !important;
        padding: 0.25rem 0.65rem !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }}

    .fb-expiry-normal {{
        background-color: {badge_avail_bg} !important;
        color: {badge_avail_text} !important;
        border: 1px solid {badge_avail_border} !important;
    }}

    .fb-expiry-urgent {{
        background-color: {badge_req_bg} !important;
        color: {badge_req_text} !important;
        border: 1px solid {badge_req_border} !important;
        animation: pulse-border 1.5s infinite !important;
    }}

    .fb-expiry-expired {{
        background-color: {badge_exp_bg} !important;
        color: {badge_exp_text} !important;
        border: 1px solid {badge_exp_border} !important;
    }}

    /* --- Buttons --- */
    div.stButton > button:first-child {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }}

    div.stButton > button:first-child:hover {{
        background-color: {btn_hover} !important;
        color: {btn_text} !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35) !important;
        transform: translateY(-1px) !important;
    }}

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"] {{
        background-color: {card_bg} !important;
        color: {btn_bg} !important;
        border: 1px solid {btn_bg} !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        background-color: {card_sub_bg} !important;
        color: {btn_hover} !important;
    }}

    /* Sidebar Logo & Profile */
    .fb-sidebar-logo {{
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        padding: 0.8rem 0 !important;
        border-bottom: 1px solid {border_color} !important;
        margin-bottom: 1.2rem !important;
    }}

    .fb-sidebar-title {{
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: {text_title} !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }}

    .fb-user-badge {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        margin-bottom: 1.2rem !important;
        color: {text_primary} !important;
    }}

    /* Info & Warning Alert Boxes */
    .fb-info-box {{
        background-color: {box_info_bg} !important;
        border-left: 4px solid {box_info_border} !important;
        padding: 1rem 1.2rem !important;
        border-radius: 0 8px 8px 0 !important;
        margin: 1rem 0 !important;
        color: {box_info_text} !important;
    }}

    .fb-warning-box {{
        background-color: {box_warn_bg} !important;
        border-left: 4px solid {box_warn_border} !important;
        padding: 1rem 1.2rem !important;
        border-radius: 0 8px 8px 0 !important;
        margin: 1rem 0 !important;
        color: {box_warn_text} !important;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1.5rem !important;
        border-bottom: 2px solid {border_color} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        padding-bottom: 0.8rem !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: {border_highlight} !important;
        border-bottom-color: {border_highlight} !important;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)
