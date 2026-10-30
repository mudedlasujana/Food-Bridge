"""
FoodBridge - Food Safety & Guidelines Component
Provides educational resources, FSSAI / WHO temperature standards,
and an interactive donor self-audit checklist.
"""

import streamlit as st
from components.styles import render_html

def render_food_safety_page():
    """Render the comprehensive Food Safety & Hygiene Guidelines page."""
    render_html(
        """
        <div class="fb-hero-banner" style="background: linear-gradient(135deg, #198754 0%, #157347 100%);">
            <div>
                <h1 class="fb-hero-title">🛡️ Food Safety & Handling Guidelines</h1>
                <div class="fb-hero-sub">Standard Operating Procedures for Donors & NGOs to Ensure Food Remains Wholesome</div>
            </div>
            <div style="font-size: 2.5rem;">🥗</div>
        </div>
        """
    )
    
    st.markdown(
        """
        Food rescue is only impactful when the food shared is **wholesome, hygienic, and safe to consume**. 
        All donors and recipient organizations participating in FoodBridge must adhere to standard food hygiene guidelines 
        modeled on WHO and Food Safety standards.
        """
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_html(
            """
            <div class="fb-food-card" style="border-top: 4px solid #10B981;">
                <h3 style="margin-top: 0;">🌡️ The Temperature Danger Zone</h3>
                <p>Bacteria multiply rapidly between <strong>5°C (40°F) and 60°C (140°F)</strong>. Food must spend minimal time in this zone.</p>
                <ul>
                    <li><strong>Hot Food Holding:</strong> Must be kept above <strong>60°C (140°F)</strong> using chafing dishes, warmers, or insulated boxes.</li>
                    <li><strong>Cold Storage:</strong> Perishables and dairy must be kept below <strong>5°C (40°F)</strong>.</li>
                    <li><strong>Frozen Food:</strong> Stored and transported below <strong>-18°C (0°F)</strong> without thaw-refreeze cycles.</li>
                </ul>
            </div>
            """
        )
        
        render_html(
            """
            <div class="fb-food-card" style="border-top: 4px solid #38BDF8;">
                <h3 style="margin-top: 0;">⏱️ The 4-Hour / 2-Hour Rule</h3>
                <p>For cooked meals and prepared foods:</p>
                <ul>
                    <li><strong>Under 2 Hours:</strong> Food can be safely refrigerated or consumed immediately.</li>
                    <li><strong>2 to 4 Hours:</strong> Food must be consumed immediately; cannot be re-chilled.</li>
                    <li><strong>Over 4 Hours at Room Temp:</strong> Food <strong>must be discarded</strong> and cannot be donated through FoodBridge.</li>
                </ul>
            </div>
            """
        )
        
    with col2:
        render_html(
            """
            <div class="fb-food-card" style="border-top: 4px solid #20c997;">
                <h3 style="margin-top: 0;">✅ Acceptable Foods for Donation</h3>
                <ul>
                    <li>Freshly prepared cooked meals that have not been served on customer tables or buffet lines.</li>
                    <li>Surplus unserved food from banquet kitchens, bakeries, catering events.</li>
                    <li>Unblemished whole raw fruits, vegetables, and tubers.</li>
                    <li>Dry packaged rations (grains, pulses, flours, unopened biscuits, noodles).</li>
                    <li>Pasteurized sealed dairy products with intact packaging and safe dates.</li>
                </ul>
            </div>
            """
        )
        
        render_html(
            """
            <div class="fb-food-card" style="border-top: 4px solid #F43F5E;">
                <h3 style="margin-top: 0;">❌ Strictly Prohibited Items</h3>
                <ul>
                    <li>Food leftovers from diners' individual plates or opened buffet self-serve trays.</li>
                    <li>Food showing any signs of spoilage, abnormal odors, sourness, discoloration, or mold.</li>
                    <li>Food stored at ambient temperature exceeding 4 hours.</li>
                    <li>Swollen, leaking, or severely rusted canned goods.</li>
                    <li>Expired baby food or raw uninspected meat products.</li>
                </ul>
            </div>
            """
        )
        
    st.markdown("---")
    
    # Interactive Self-Audit Checklist
    st.subheader("📋 Interactive Food Safety Self-Audit for Donors")
    st.caption("Complete this quick 5-point verification before publishing or dispatching a food donation.")
    
    c_check1, c_check2 = st.columns(2)
    with c_check1:
        q1 = st.checkbox("1. Food was prepared in a sanitized commercial or domestic kitchen with clean drinking water.")
        q2 = st.checkbox("2. Food handlers practiced hand hygiene, wore gloves/hairnets, and showed no respiratory illnesses.")
        q3 = st.checkbox("3. Food has been held safely (Hot >60°C or Cold <5°C) and never left at room temperature past 2 hours.")
    with c_check2:
        q4 = st.checkbox("4. Packaging consists of clean, food-grade containers, aluminum foil containers, or sealed liners.")
        q5 = st.checkbox("5. Food is clearly labeled with preparation time, dietary classification (Veg/Non-Veg), and allergen info.")
        
    all_passed = q1 and q2 and q3 and q4 and q5
    if all_passed:
        st.success("🌟 100% Compliance Verified! This food meets all standard safety benchmarks for donation.")
    else:
        st.info("ℹ️ Check all 5 compliance standards to verify safe donation protocol.")
