import streamlit as st
import pandas as pd
import csv
import os

# --- File Path ---
ADMIN_LOGIN_FILE = "admin_logins.csv"  # Stores email, password, admin_name

# --- Ensure Admin Login CSV Exists ---
if not os.path.exists(ADMIN_LOGIN_FILE):
    with open(ADMIN_LOGIN_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Email", "Password", "AdminName"])  # Add more fields as needed

# --- Admin Login Panel ---
def admin_login_panel():
    st.header("🔒 Admin Login")
    email = st.text_input("Admin Email")
    password = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            df = pd.read_csv(ADMIN_LOGIN_FILE)
            # Normalize email prefix and admin names for comparison
            email_prefix = email.split('@')[0].replace(' ', '').lower()
            df['AdminName_normalized'] = df['AdminName'].str.replace(' ', '').str.lower()
            user = df[(df['Email'].str.lower() == email.strip().lower()) &
                      (df['Password'] == password) &
                      (df['AdminName_normalized'] == email_prefix)]
            if not user.empty:
                st.success(f"Welcome, {user.iloc[0]['AdminName']}! Admin access granted.")
                # Here you can show admin features or set a session state
            else:
                st.error("Invalid credentials or admin name does not match email prefix.")

if __name__ == "__main__":
    admin_login_panel()
