"""
FoodBridge - Authentication & Session Management
Handles secure password hashing with salts, user login, registration, and logout.
"""

import hashlib
import os
import uuid
from datetime import datetime
import streamlit as st
import database as db
import config

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password using SHA-256 with a random cryptographic salt.
    Returns (hashed_password, salt).
    """
    if salt is None:
        salt = os.urandom(16).hex()
    salted = f"{salt}:{password}".encode("utf-8")
    pwd_hash = hashlib.sha256(salted).hexdigest()
    return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify that a plaintext password matches the stored hash given its salt."""
    salted = f"{salt}:{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest() == stored_hash

def init_session_state():
    """Initialize necessary session state variables for authentication and navigation."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "Home"

def login_user(email: str, password: str) -> tuple[bool, str]:
    """
    Validate user credentials and set session state upon success.
    Returns (success, message).
    """
    email_clean = email.strip().lower()
    users = db.get_users()
    
    user = next((u for u in users if u["email"].lower() == email_clean), None)
    if not user:
        return False, "No account found with this email address."
    
    if not user.get("is_active", True):
        return False, "This account has been deactivated. Please contact an administrator."
    
    # Verify password hash
    stored_hash = user.get("password_hash", "")
    salt = user.get("salt", "")
    
    if not verify_password(password, stored_hash, salt):
        return False, "Incorrect password. Please try again."
    
    # Store user in session
    st.session_state.logged_in = True
    st.session_state.current_user = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "organization": user.get("organization", user["name"]),
        "city": user.get("city", "Bangalore"),
        "phone": user.get("phone", ""),
        "donor_type": user.get("donor_type", ""),
        "ngo_reg_number": user.get("ngo_reg_number", "")
    }
    st.session_state.active_nav = "Dashboard"
    return True, f"Welcome back, {user['name']}!"

def register_user(user_data: dict) -> tuple[bool, str]:
    """
    Register a new user into the JSON database.
    user_data must include: name, email, password, role, organization, phone, city
    """
    email_clean = user_data["email"].strip().lower()
    users = db.get_users()
    
    # Check for existing email
    if any(u["email"].lower() == email_clean for u in users):
        return False, "An account with this email address is already registered."
    
    pwd_hash, salt = hash_password(user_data["password"])
    
    new_user = {
        "id": f"usr_{uuid.uuid4().hex[:10]}",
        "name": user_data["name"].strip(),
        "email": email_clean,
        "password_hash": pwd_hash,
        "salt": salt,
        "role": user_data["role"],
        "organization": user_data.get("organization", "").strip(),
        "phone": user_data.get("phone", "").strip(),
        "city": user_data.get("city", "Bangalore").strip(),
        "address": user_data.get("address", "").strip(),
        "donor_type": user_data.get("donor_type", ""),
        "ngo_reg_number": user_data.get("ngo_reg_number", ""),
        "is_active": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    users.append(new_user)
    db.save_users(users)
    return True, "Registration successful! You can now log in."

def logout_user():
    """Log out the current user and reset session state."""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.active_nav = "Home"

def quick_switch_user(email: str):
    """Developer/Demo convenience tool: quickly sign in as one of the preconfigured test accounts."""
    users = db.get_users()
    user = next((u for u in users if u["email"].lower() == email.lower()), None)
    if user:
        st.session_state.logged_in = True
        st.session_state.current_user = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "organization": user.get("organization", user["name"]),
            "city": user.get("city", "Bangalore"),
            "phone": user.get("phone", ""),
            "donor_type": user.get("donor_type", ""),
            "ngo_reg_number": user.get("ngo_reg_number", "")
        }
        st.session_state.active_nav = "Dashboard"
        return True
    return False
