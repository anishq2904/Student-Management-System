import streamlit as st
import pandas as pd
import csv
import os

# --- Theme Colors ---
LIGHT_THEME = {
    "bg": "#ecf0f1",
    "fg": "#2c3e50",
    "button_bg": "#3498db",
    "button_fg": "white",
    "entry_bg": "#fff",
    "entry_fg": "#111"
}
DARK_THEME = {
    "bg": "#222831",
    "fg": "#eeeeee",
    "button_bg": "#393e46",
    "button_fg": "#00adb5",
    "entry_bg": "#393e46",
    "entry_fg": "#eeeeee"
}

# --- File Path ---
STUDENT_FILE = "students.csv"
LOG_FILE = "usage_logs.txt"

# --- Ensure CSV Exists ---
if not os.path.exists(STUDENT_FILE):
    with open(STUDENT_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Name", "Age", "Gender", "Date of Birth", "Grade / Class", "Section", "Roll Number / Student ID", "Contact Number", "Email Address"
        ])

# --- Theme State ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = LIGHT_THEME

# --- Theme CSS Injection ---
def apply_theme():
    theme = st.session_state['theme']
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {theme['bg']} !important;
            color: {theme['fg']} !important;
        }}
        .stButton>button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_fg']} !important;
        }}
        .stTextInput>div>div>input {{
            background-color: {theme['entry_bg']} !important;
            color: {theme['entry_fg']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def switch_theme():
    st.session_state['theme'] = DARK_THEME if st.session_state['theme'] == LIGHT_THEME else LIGHT_THEME
    st.rerun()

# --- Add Student ---
def add_student():
    st.subheader("➕ Add Student")
    with st.form("add_student_form"):
        name = st.text_input("Name")
        age = st.text_input("Age")
        gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
        dob = st.date_input("Date of Birth")
        grade = st.text_input("Grade / Class")
        section = st.text_input("Section")
        roll_number = st.text_input("Roll Number / Student ID")
        contact = st.text_input("Contact Number")
        email_addr = st.text_input("Email Address")
        submitted = st.form_submit_button("Save")
        if submitted:
            if not all([name, age, gender, dob, grade, section, roll_number, contact, email_addr]):
                st.warning("All fields are required.")
            else:
                try:
                    int(age)
                    with open(STUDENT_FILE, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([
                            name, age, gender, dob, grade, section, roll_number, contact, email_addr
                        ])
                    st.success(f"Student {name} added.")
                except ValueError:
                    st.warning("Age must be a number.")
                except Exception as e:
                    st.error(f"Could not save student: {e}")

# --- Manage Students ---
def manage_students():
    st.subheader("📝 Manage Students")
    df = pd.read_csv(STUDENT_FILE)
    if df.empty:
        st.info("No students found.")
        return
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes"):
        edited_df.to_csv(STUDENT_FILE, index=False)
        st.success("Changes saved.")

# --- Search Students ---
def search_students():
    st.subheader("🔎 Search Students")
    query = st.text_input("Search by Name or Grade:")
    if query:
        df = pd.read_csv(STUDENT_FILE)
        results = df[df['Name'].str.contains(query, case=False) | df['Grade'].str.contains(query, case=False)]
        if not results.empty:
            st.dataframe(results)
        else:
            st.info("No matching records found.")

# --- Export to Excel ---
def export_to_excel():
    df = pd.read_csv(STUDENT_FILE)
    export_file = "students_export.xlsx"
    df.to_excel(export_file, index=False)
    with open(export_file, "rb") as f:
        st.download_button("Download Excel File", f, file_name=export_file)

# --- Student Login with Email/Password ---
STUDENT_LOGIN_FILE = "student_logins.csv"  # Stores email, password, name, etc.

# Ensure login CSV exists
if not os.path.exists(STUDENT_LOGIN_FILE):
    with open(STUDENT_LOGIN_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Email", "Password", "Name"])  # Add more fields as needed

def lcs_length(a, b):
    # Longest Common Subsequence (LCS) length
    dp = [[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[-1][-1]

def student_login():
    st.subheader("🎓 Student Login (Email & Password)")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            st.success(f"Logged in as: {email}")
            # Extract and normalize email prefix
            name_from_email = email.split('@')[0].replace(' ', '').lower()
            st.info(f"Checking for student with at least 50% name match to: {name_from_email}")
            df = pd.read_csv(STUDENT_FILE)
            df['Name_normalized'] = df['Name'].str.replace(' ', '').str.lower()
            found = False
            for idx, row in df.iterrows():
                student_name = row['Name_normalized']
                lcs = lcs_length(name_from_email, student_name)
                max_len = max(len(name_from_email), len(student_name))
                if max_len == 0:
                    continue
                percent = lcs / max_len
                if percent >= 0.5:
                    st.success(f"Found matching student: {row['Name']} ({percent*100:.1f}% match)")
                    st.dataframe(df.loc[[idx]].drop(columns=['Name_normalized']))
                    found = True
                    break
            if not found:
                st.info("No sufficiently matching student record found.")

# --- Dashboard ---
def show_dashboard():
    st.subheader("📊 Dashboard")
    df = pd.read_csv(STUDENT_FILE)
    total = len(df)
    st.write(f"Total Students: {total}")
    if total > 0:
        import plotly.express as px
        grade_counts = df['Grade'].value_counts()
        fig = px.pie(
            values=grade_counts.values,
            names=grade_counts.index,
            title='Student Distribution by Grade',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Usage Logs ---
def view_usage_logs():
    st.subheader("📜 Usage Logs")
    # Show admin login counts
    st.markdown("**Admin Login Counts:**")
    if os.path.exists(ADMIN_LOGIN_LOG_FILE):
        from collections import Counter
        with open(ADMIN_LOGIN_LOG_FILE, 'r') as f:
            lines = f.readlines()
        emails = [line.split(',')[0].strip() for line in lines if ',' in line]
        if emails:
            counts = Counter(emails)
            for email, count in counts.items():
                st.write(f"{email}: {count} logins")
        else:
            st.info("No admin login logs found.")
    else:
        st.info("No admin login logs found.")
    # Show other logs if needed
    st.markdown("---")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            st.text(f.read())
    else:
        st.info("No logs found.")

# --- Main App Layout ---
st.set_page_config(page_title="Student Records & Dashboard", layout="wide")
# --- Theme Selector at the Top ---
theme_choice = st.radio(
    "Theme Mode", ("Light", "Dark"),
    index=0 if st.session_state['theme'] == LIGHT_THEME else 1,
    horizontal=True
)
if theme_choice == "Light" and st.session_state['theme'] != LIGHT_THEME:
    st.session_state['theme'] = LIGHT_THEME
    st.rerun()
elif theme_choice == "Dark" and st.session_state['theme'] != DARK_THEME:
    st.session_state['theme'] = DARK_THEME
    st.rerun()
apply_theme()

# --- Background Images ---
  # Example student image

tabs = st.tabs(["🔒 Admin Panel", "🎓 Student Panel"])

# Determine which tab is selected (Streamlit does not provide direct tab index, so use session_state workaround)
def set_tab(tab_name):
    st.session_state['active_tab'] = tab_name

# Default to Admin tab
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = "Admin"

# Tab selection logic
admin_tab, student_tab = tabs

with admin_tab:
    set_tab("Admin")
with student_tab:
    set_tab("Student")

# Inject background image CSS based on active tab
bg_url = ADMIN_BG_URL if st.session_state['active_tab'] == "Admin" else STUDENT_BG_URL
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{bg_url}');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("📚 Student Records & Dashboard")

# --- Admin Login with Email/Password ---
ADMIN_LOGIN_FILE = "admin_logins.csv"  # Stores email, password, admin_name

# Ensure admin login CSV exists
if not os.path.exists(ADMIN_LOGIN_FILE):
    with open(ADMIN_LOGIN_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Email", "Password", "AdminName"])  # Add more fields as needed

import datetime

ADMIN_LOGIN_LOG_FILE = "admin_login_logs.txt"

def admin_login():
    st.subheader("🔒 Admin Login (Email & Password)")
    email = st.text_input("Admin Email")
    password = st.text_input("Admin Password", type="password")
    login_btn = st.button("Login as Admin")
    if login_btn:
        if not email or not password:
            st.warning("Please enter both email and password.")
            return False
        else:
            # Log the login attempt
            with open(ADMIN_LOGIN_LOG_FILE, 'a') as logf:
                logf.write(f"{email},{datetime.datetime.now().isoformat()}\n")
            st.success(f"Logged in as admin: {email}")
            st.session_state['admin_logged_in'] = True
            st.session_state['admin_email'] = email
            return True
    return st.session_state.get('admin_logged_in', False)

with tabs[0]:
    st.header("Admin Panel")
    if not st.session_state.get('admin_logged_in', False):
        admin_login()
    if st.session_state.get('admin_logged_in', False):
        admin_action = st.radio(
            "Select Action:",
            ("Add Student", "Manage Students", "Import Data", "View Dashboard", "View Logs"),
            key="admin_action"
        )
        if admin_action == "Add Student":
            add_student()
        elif admin_action == "Manage Students":
            manage_students()
        elif admin_action == "Import Data":
            st.subheader("📤 Import Student Data (CSV or Excel)")
            uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])
            if uploaded_file is not None:
                import pandas as pd
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    st.dataframe(df)
                    if st.button("Overwrite Student Records with Imported Data"):
                        df.to_csv(STUDENT_FILE, index=False)
                        st.success("Student records have been updated with the imported file.")
                except Exception as e:
                    st.error(f"Failed to import file: {e}")
               
            export_to_excel()
        elif admin_action == "View Dashboard":
            show_dashboard()
        elif admin_action == "View Logs":
            view_usage_logs()

        # Theme selector (moved to top, so remove here)

with tabs[1]:
    st.header("Student Panel")
    student_action = st.radio(
        "Select Action:",
        ("View My Record", "Search Students"),
        key="student_action"
    )
    if student_action == "View My Record":
        student_login()
    elif student_action == "Search Students":
        search_students()
