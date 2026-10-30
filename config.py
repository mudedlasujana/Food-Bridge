"""
FoodBridge - Configuration & Constants
Defines theme colors, statuses, categories, and application settings.
"""

# App Information
APP_NAME = "FoodBridge"
APP_TAGLINE = "Connecting Surplus Food with Those in Need"
APP_ICON = "🍲"
APP_VERSION = "1.0.0"

# Color Palette (Green, Cream, and White theme)
PRIMARY_GREEN = "#198754"        # Vibrant Forest / Bootstrap Success Green
DARK_GREEN = "#0f5132"           # Dark Green for headings & strong contrast
LIGHT_GREEN = "#d1e7dd"          # Soft light green tint
CREAM_BG = "#FDFBF7"             # Warm Cream background
WHITE = "#FFFFFF"                # Crisp clean white
BORDER_COLOR = "#E2E8F0"         # Soft slate border
TEXT_DARK = "#1E293B"            # Rich slate text
TEXT_MUTED = "#64748B"           # Secondary muted text
CARD_BG = "#FFFFFF"              # White card surface

# Status Colors
STATUS_COLORS = {
    "Available": {"bg": "#E8F5E9", "border": "#4CAF50", "text": "#1B5E20", "icon": "🟢"},
    "Requested": {"bg": "#FFF8E1", "border": "#FFB300", "text": "#B78103", "icon": "🟡"},
    "Accepted":  {"bg": "#E1F5FE", "border": "#03A9F4", "text": "#0277BD", "icon": "🔵"},
    "Completed": {"bg": "#ECEFF1", "border": "#78909C", "text": "#37474F", "icon": "✅"},
    "Expired":   {"bg": "#FFEBEE", "border": "#E53935", "text": "#C62828", "icon": "⚠️"},
    "Cancelled": {"bg": "#F5F5F5", "border": "#9E9E9E", "text": "#616161", "icon": "❌"}
}

# User Roles
ROLE_DONOR = "Donor"
ROLE_NGO = "NGO"
ROLE_ADMIN = "Admin"
ROLES = [ROLE_DONOR, ROLE_NGO, ROLE_ADMIN]

# Food Categories
FOOD_CATEGORIES = [
    "Cooked Meals",
    "Bakery & Bread",
    "Fruits & Vegetables",
    "Raw Groceries & Grains",
    "Packaged & Canned Goods",
    "Dairy Products",
    "Beverages & Juices"
]

CATEGORY_ICONS = {
    "Cooked Meals": "🍲",
    "Bakery & Bread": "🍞",
    "Fruits & Vegetables": "🍎",
    "Raw Groceries & Grains": "🌾",
    "Packaged & Canned Goods": "🥫",
    "Dairy Products": "🧀",
    "Beverages & Juices": "🧃"
}

# Donor Types
DONOR_TYPES = [
    "Restaurant / Cafe",
    "Hotel & Banquet Hall",
    "Catering Service",
    "Bakery & Confectionery",
    "Supermarket / Grocery",
    "Corporate / College Cafeteria",
    "Individual / Household"
]

# Quantity Units
UNITS = [
    "Plates / Meals",
    "Kilograms (kg)",
    "Packets / Boxes",
    "Liters",
    "Items / Pieces"
]

# Dietary Types
DIETARY_TYPES = [
    "Vegetarian",
    "Non-Vegetarian",
    "Vegan",
    "Eggitarian"
]

# Storage Requirements
STORAGE_REQUIREMENTS = [
    "Room Temperature (Cool & Dry)",
    "Refrigerated (Below 5°C / 40°F)",
    "Hot Holding (Above 60°C / 140°F)",
    "Frozen (Below -18°C / 0°F)"
]

# Environmental & Social Impact Multipliers
KG_PER_MEAL_ESTIMATE = 0.40       # ~400g per meal average
CO2_PER_KG_FOOD_SAVED = 2.5       # kg CO2 emissions prevented per kg food diverted from landfill
WATER_SAVED_PER_KG = 250          # Liters of water footprint saved per kg food diverted
