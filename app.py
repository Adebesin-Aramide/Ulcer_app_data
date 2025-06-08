import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Google Sheets setup ---
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "service_account.json"
SPREADSHEET_NAME = "Ulcer Data"

@st.cache_resource
def init_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    workbook = client.open(SPREADSHEET_NAME)
    headers = [
        "Date", "Age", "Gender", "TakeUlcerMed", "MedTime", "PainRating", "Symptoms",
        "Duration", "SymptomChange", "AteTriggers", "SkippedMeal", "AteLate",
        "TookNSAID", "StressLevel", "CancerDiag",
        "FamilyHistory", "LogTimestamp"
    ]
    try:
        sheet = workbook.worksheet("DailyLogs")
    except gspread.WorksheetNotFound:
        sheet = workbook.add_worksheet("DailyLogs", rows=100, cols=20)
    # Ensure header row
    first_row = sheet.row_values(1)
    if first_row != headers:
        sheet.insert_row(headers, 1)
    return sheet

sheet = init_sheet()

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Introduction", "Daily Log"])

# --- Introduction page ---
if page == "Introduction":
    st.title("Ulcer Management App")
    st.write("""

### About the Project
                
This app is part of our team’s entry for the **Deep Learning Indaba Community Competition**, led by Aramide Adebesin. We’re building a daily-logging App that helps people living with ulcers in Sub-Saharan Africa track their meals, symptoms, and medications. By collecting these details, we aim to power AI models that learn each user’s personal ulcer triggers, detect patterns that could increase gastric cancer risk, and alert users to unsafe medications.
                
### How It Works
        
- Daily Log Entry:
             
Enter your age and gender each day.
             
Record whether you took ulcer medication and at what time.
             
Rate your pain, select any symptoms, and note how long discomfort lasted.
             
Log meals (e.g. spicy, oily, acidic), stress level, and NSAID use.
             
Indicate any gastric-cancer diagnoses or family history.
                
                
- Data Storage:
             
All entries are saved securely to a Google Sheet.
             
Your data fuels our machine-learning backend to uncover personal triggers and flag high-risk patterns.
                
### Get Involved
             
Be accurate: Honest entries help our AI learn effectively.

***Select “Daily Log” from the sidebar to begin recording your day’s details!***
 """)

    st.write("✉️ Email the team: dsnoau@datascientistsfoundation.org for questions or feedback.")

# --- Daily Log page ---
elif page == "Daily Log":
    st.title("Daily Log Entry")

    # Demographics
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.radio("Gender", ["Male", "Female", "Other"])

    # Medication & Time
    took_ulcer_med = st.radio("Take ulcer medication today?", ["Yes", "No"])
    med_time = st.time_input("Medication time", datetime.now().time())

    # Pain & Symptoms
    pain_rating = st.slider("Pain rating (1–5)", 1, 5, 1)
    symptoms = st.multiselect(
        "Symptoms today:",
        ["Bloating", "Vomiting", "Acid reflux", "Heartburn", "Loss of appetite",
         "Indigestion", "Blood in vomit/stool", "Nausea", "Unintended weight loss",
         "Feeling full quickly", "Persistent fatigue", "Dark or tarry stools", "None"]
    )
    symptom_duration = st.radio(
        "Duration of discomfort:", ["<30 mins", "30 mins–2 hrs", ">2 hrs"]
    )
    symptom_change = st.slider("Compared to yesterday (1 good–10 bad)", 1, 10, 5)

    # Diet & Lifestyle
    ate_triggers = st.radio("Ate spicy/oily/caffeinated/carbonated/acidic food?", ["Yes", "No"])
    skipped_meal = st.radio("Skipped any meals today?", ["Yes", "No"])
    ate_late = st.radio("Ate late at night?", ["Yes", "No"])
    took_nsaid = st.radio("Took NSAIDs today? (like Ibuprofen)", ["Yes", "No"])
    stress = st.slider("Stress level (1–5)", 1, 5, 3)

    # Cancer Check
    cancer_diag = st.radio("Gastric cancer diagnosis during monitoring?", ["Yes", "No"])
    family_history = st.radio("Family history of gastric cancer?", ["Yes", "No", "Not sure"])

    if st.button("Submit Daily Log"):
        row = [
            datetime.now().strftime("%Y-%m-%d"),
            age, gender, took_ulcer_med, med_time.strftime("%H:%M"),
            pain_rating, ";".join(symptoms) or "None",
            symptom_duration, symptom_change,
            ate_triggers, skipped_meal, ate_late,
            took_nsaid,stress,
            cancer_diag, family_history,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
        st.success("Your daily log has been saved!")
