# 🍲 FoodBridge – Food Waste Management & Donation Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51%2B-FF4B4B.svg)](https://streamlit.io/)
[![Theme](https://img.shields.io/badge/Theme-Forest%20Green%20%26%20Cream-198754.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FoodBridge** is a modern, responsive web application built with Python and Streamlit that connects food donors (restaurants, hotels, bakeries, caterers, and individuals) directly with local NGOs and food banks. The platform prevents food wastage, alleviates community hunger, and tracks environmental carbon offsets.

---

## 🌟 Key Highlights & Requirements Fulfilled

- **Zero-Waste Pipeline**: End-to-end workflow from donor listing to NGO pickup and verified delivery.
- **Role-Based Dashboards**: Tailored views and controls for **Donors**, **NGOs**, and **Administrators**.
- **Double-Claim Prevention**: Atomic state validation prevents multiple NGOs from reserving the same donation concurrently.
- **Safety & Expiry Safeguards**: Automated expiry detection; expired food cannot be requested, protecting vulnerable recipients.
- **Cryptographic Security**: Salted SHA-256 password hashing.
- **☀️ Light Mode & 🌙 Dark Mode**: High-contrast, dynamic dual-theme switcher in the sidebar (Forest Green & Warm Cream for Light Mode; Emerald Green & Midnight Slate for Dark Mode).
- **Interactive Visualizations**: Plotly Donut and Pipeline charts for categories, status tracking, and environmental impact.
- **Beginner-Friendly Architecture**: Modular, clean code storing records in structured JSON files without complicated external database setup.

---

## 👥 User Roles & Features

### 1. 👨‍🍳 Food Donor
* **Registration & Sign-In**: Select donor business category (Restaurant, Hotel, Bakery, Catering, Household).
* **Post Food Donations**:
  * Title, Category (Cooked Meals, Bakery, Fresh Produce, Raw Groceries, Canned Goods, Dairy, Beverages).
  * Quantity, Unit (Plates/Meals, kg, Packets), and approximate kg calculation.
  * Cooked/Packaged Date & Time and Best-Before Expiry DateTime (strictly validated in the future).
  * Storage Requirement (Room Temperature, Refrigerated, Hot Holding, Frozen).
  * Pickup address, landmarks, and special notes.
  * **Food Safety Declaration**: Mandatory pledge verifying hygienic preparation.
* **Manage Listings**:
  * Filter own listings by status (`Available`, `Requested`, `Accepted`, `Completed`, `Expired`).
  * Edit active listings.
  * Delete unfulfilled listings.
* **Handover Pipeline**:
  * Review incoming NGO pickup requests.
  * Accept or decline requests.
  * Confirm physical handover to mark as `Completed`.
* **Impact Tracking**: Track meals donated, kilograms rescued, and CO₂ emissions averted.

### 2. 🏢 NGO / Charitable Organization
* **Registration & Sign-In**: Verified registration with NGO registration/Darpan ID and service address.
* **Browse & Search Available Food**:
  * Real-time search by food title, donor name, or location.
  * Filter by category, dietary classification (Vegetarian, Non-Veg, Vegan), or sorting (Expiring Soonest, Recently Posted).
  * Dynamic countdown badges (`3h 15m left`, `⚠️ Urgent`).
* **Request Surplus Food**:
  * Enter planned pickup arrival time, transport vehicle type (insulated van, cold box, etc.), and target beneficiary count.
  * Agree to transport and distribution safety terms.
  * **Protected by atomic claim validation** (double-claim attempt triggers instant warning).
* **Track Pickups**:
  * Track request status (`Requested` ➔ `Accepted` ➔ `Completed`).
  * Confirm food receipt upon delivery.
* **NGO Food Safety Protocol**: Guidelines for thermal retention, sensory inspection, and safe serving.

### 3. 🛡️ Platform Administrator
* **Platform Overview & KPIs**:
  * Donors, NGOs, total food diverted, meals served, CO₂ saved, water saved.
  * Interactive Plotly charts (Category distribution donut chart, Status pipeline bar chart).
* **User Management**:
  * Search and filter all users.
  * Toggle active/deactivated status.
  * Delete violating accounts (with self-deletion protection).
* **Donation Oversight**:
  * Complete visibility across all donor posts.
  * Force mark expired or delete invalid listings.
* **Audit Trail**: Full chronological log of all claim requests and fulfillment history.
* **System Tools**: Export live database backups (JSON) and one-click database sample re-seeding.

---

## 📂 Project Structure

```
FoodBridge/
├── app.py                      # Main entrypoint: routing, sidebar, public pages
├── config.py                   # Constants, colors, categories, status definitions
├── database.py                 # JSON database manager with atomic writes & seeding
├── auth.py                     # Password hashing (salted SHA-256), login, registration
├── utils.py                    # Business logic: expiry check, claim lock, metrics
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation & user manual
├── data/                       # JSON database storage
│   ├── users.json              # Donor, NGO, and Admin accounts
│   ├── donations.json          # Food donation listings
│   └── requests.json           # NGO claim requests and pickup records
└── components/
    ├── __init__.py
    ├── styles.py               # Custom CSS for Green & Cream theme
    ├── donor_dashboard.py      # Donor portal (Post, Edit, Delete, Accept)
    ├── ngo_dashboard.py        # NGO portal (Browse, Request, Track pickups)
    ├── admin_dashboard.py      # Admin control center & Plotly charts
    └── food_safety.py          # WHO/FSSAI Food safety standards & checklist
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed on your system.

### 2. Installation
Open your terminal or command prompt inside the project folder:

```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Start the Streamlit development server:

```bash
streamlit run app.py
```

The application will launch automatically in your default browser at:
`http://localhost:8501`

---

## 🔑 Pre-Configured Demo Credentials

The platform includes pre-seeded sample data so you can test all features right away without manually creating accounts. You can also use the **1-Click Demo Switcher** in the sidebar.

| Role | Name / Organization | Email | Password |
| :--- | :--- | :--- | :--- |
| **👨‍🍳 Donor** | Chef Ramesh (`Green Leaf Gourmet Bistro`) | `bistro@greenleaf.com` | `demo1234` |
| **🍞 Donor** | Priya Sen (`Sunset Artisanal Bakery`) | `orders@sunsetbakery.com` | `demo1234` |
| **🏢 NGO** | Arun Kumar (`Hope & Hunger Food Bank`) | `contact@hopefoodbank.org` | `demo1234` |
| **🤝 NGO** | Dr. Sunita Rao (`Anna Raksha Seva Foundation`) | `seva@annaraksha.org` | `demo1234` |
| **🛡️ Admin** | Platform Administrator (`FoodBridge Central`) | `admin@foodbridge.org` | `admin123` |

---

## 🛡️ Business Logic & Safeguards

1. **Password Hashing**: Passwords are never stored in plaintext. Each account is hashed with a cryptographically secure random salt using SHA-256 (`hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()`).
2. **Preventing Concurrent Claims**: When an NGO clicks "Submit Donation Request", the server locks and checks the donation status in real time. If another organization claims it first, the second request is rejected with a clear notification.
3. **Expiry Enforcement**:
   - The system checks donation timestamps against the system clock.
   - Any listing past its best-before time is automatically transitioned to `Expired`.
   - The UI disables request buttons and prevents claims on expired food.
4. **Food Safety Protocols**:
   - 4-Hour Rule: Cooked meals left at room temperature for over 4 hours cannot be donated.
   - Temperature Danger Zone: Guidelines to maintain hot food >60°C and cold food <5°C.
   - Interactive 5-point safety checklist before posting.

---

## 📊 Environmental Impact Calculation

FoodBridge measures social and environmental metrics:
- **Estimated Meals**: $\text{Meals} \approx \frac{\text{Rescued Food (kg)}}{0.40\text{ kg per meal}}$
- **CO₂ Offset**: $2.5\text{ kg of }\text{CO}_2\text{ averted per kg of food rescued}$ from landfills.
- **Water Conserved**: $250\text{ Liters of virtual water footprint saved per kg}$ of food diverted.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
