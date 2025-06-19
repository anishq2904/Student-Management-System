import streamlit as st
import pandas as pd
import csv
import os

# --- File Path ---
STUDENT_LOGIN_FILE = "student_logins.csv"  # Stores email, password, name, etc.

# --- Ensure Login CSV Exists ---
if not os.path.exists(STUDENT_LOGIN_FILE):
    with open(STUDENT_LOGIN_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Email", "Password", "Name"])  # Add more fields as needed

# --- Student Login Panel ---
def student_login_panel():
    st.header("🎓 Student Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            df = pd.read_csv(STUDENT_LOGIN_FILE)
            user = df[(df['Email'].str.lower() == email.strip().lower()) & (df['Password'] == password)]
            if not user.empty:
                # Fetch the student's name (exact, case-sensitive)
                student_name = user.iloc[0]['Name']
                # Fetch the admin's name for the same email
                admin_df = pd.read_csv("admin_logins.csv")
                admin_user = admin_df[admin_df['Email'].str.lower() == email.strip().lower()]
                if not admin_user.empty:
                    admin_name = admin_user.iloc[0]['AdminName']
                    if student_name == admin_name:
                        st.success(f"Welcome, {user.iloc[0]['Name']}!")
                        # You can display more student info here or redirect to their dashboard
                    else:
                        st.error("Wrong user name")
                else:
                    st.error("No admin record found for this email. Login not allowed.")
            else:
                st.error("Invalid email or password.")

if __name__ == "__main__":
    student_login_panel()
