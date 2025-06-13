import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Google Sheets setup ---
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Ulcer Data"

@st.cache_resource
def init_sheet():
    # Load credentials
    creds_dict = st.secrets["google_credentials"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    workbook = client.open(SPREADSHEET_NAME)

    # Desired headers
    headers = [
        "Date", "Age", "Gender",
        "TakeUlcerMed", "MedTime",
        "PainRating", "Symptoms", "Duration", "SymptomChange",
        "Meals", "TriggerCauses",
        "AteTriggers", "SkippedMeal", "AteLate", "TookNSAID",
        "StressLevel",
        "CancerDiag", "FamilyHistory",
        "HpyloriUlcer",
        "LogTimestamp"
    ]

    # Get or create sheet
    try:
        sheet = workbook.worksheet("DailyLogs")
    except gspread.WorksheetNotFound:
        sheet = workbook.add_worksheet("DailyLogs", rows=200, cols=len(headers))

    # Update header row explicitly (preserving existing data)
    sheet.update('A1:{}'.format(chr(ord('A') + len(headers) - 1) + '1'), [headers])

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

This app is part of our team’s entry for the **Deep Learning Indaba Community Competition**, led by Aramide Adebesin. We’re building a daily-logging tool that helps people living with ulcers in Sub-Saharan Africa track their meals, symptoms, and medications. By collecting these details, we aim to power AI models that learn each user’s personal ulcer triggers, detect patterns that could increase gastric cancer risk, and alert users to unsafe medications.

### How It Works

- **Daily Log Entry:**  
  Enter your age and gender.  
  Record ulcer medication, pain ratings, and symptoms.  
  Select all meals you ate from a list of common foods.  
  Pick any trigger causes you suspect today.  
  Track stress level, NSAID use, and H. pylori diagnosis.  

- **Data Storage:**  
  All entries are saved securely to a Google Sheet.  
  Your data fuels our ML backend to uncover personal triggers and flag high-risk patterns.

### Get Involved

Be accurate: Honest entries help our AI learn effectively.  
Select **Daily Log** from the sidebar to start logging your day!

**Contact Us:** [✉️ adebesinaramide@gmail.com](mailto:adebesinaramide@gmail.com)
""")

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
        ["Bloating", "Vomiting", "Acid reflux", "Heartburn",
         "Loss of appetite", "Indigestion", "Blood in vomit/stool",
         "Nausea", "Unintended weight loss", "Feeling full quickly",
         "Persistent fatigue", "Dark or tarry stools", "None"]
    )
    symptom_duration = st.radio("Duration of discomfort:", ["<30 mins", "30 mins–2 hrs", ">2 hrs"])
    symptom_change = st.slider("Compared to yesterday (1 good–10 bad)", 1, 10, 5)

    # Meals selection
    meals = st.multiselect(
        "Meals eaten today (select all that apply):",
        [
            "Eba", "Amala", "Semovita", "Fufu", "Pounded Yam", "Tuwo", "Wheat",
            "White Rice", "Jollof Rice", "Fried Rice", "Ofada Rice", "Coconut Rice",
            "Oats", "Pap", "Custard", "Spaghetti", "Noodles", "Corn Meal",
            "Beans", "Moi Moi", "Akara", "Boiled Egg", "Fried Egg", "Boiled Chicken",
            "Fried Chicken", "Grilled Fish", "Boiled Fish", "Goat Meat", "Beef",
            "Snail", "Liver", "Cow Skin (Ponmo)", "Boiled Yam", "Yam Porridge",
            "Fried Yam", "Boiled Potato", "Sweet Potato", "Fried Plantain",
            "Boiled Plantain", "Roasted Plantain (Boli)", "Boiled Corn", "Egusi Soup",
            "Okro Soup", "Ogbono Soup", "Efo Riro", "Afang Soup", "Edikang Ikong",
            "Vegetable Soup", "Bitterleaf Soup", "Gbegiri", "Ewedu", "Banga Soup",
            "Groundnut Soup", "Pepper Soup", "Garden Egg Sauce", "Tomato Stew",
            "Palm Oil Sauce", "Fish Sauce", "Egg Sauce", "Zobo", "Smoothies",
            "Juice", "Soft Drinks", "Water", "Energy Drinks", "Milk"
        ]
    )

    # Trigger causes
    trigger_causes = st.multiselect(
        "Possible triggers for your symptoms:",
        [
            "Spicy foods", "Tomatoes", "Citrus fruits", "Fried foods",
            "Fatty foods", "Dairy", "Chocolate", "Caffeinated drinks",
            "Carbonated drinks", "Alcohol", "Fermented foods",
            "Raw onions/garlic", "Skipped a meal", "Ate late",
            "Overate", "Ate under stress", "Took NSAIDs", "Stress"
        ]
    )

    # Diet & Lifestyle
    ate_triggers = st.radio("Ate spicy/oily/caffeinated/carbonated/acidic food?", ["Yes", "No"])
    skipped_meal = st.radio("Skipped any meals today?", ["Yes", "No"])
    ate_late = st.radio("Ate late at night?", ["Yes", "No"])
    took_nsaid = st.radio("Took NSAIDs today? (like Ibuprofen)", ["Yes", "No"])
    stress = st.slider("Stress level (1–5)", 1, 5, 3)

    # Cancer & H. pylori
    cancer_diag = st.radio("Gastric cancer diagnosis during monitoring?", ["Yes", "No"])
    family_history = st.radio("Family history of gastric cancer?", ["Yes", "No", "Not sure"])
    h_pylori_ulcer = st.radio("Diagnosed with ulcer caused by H. pylori?", ["Yes", "No"])

    if st.button("Submit Daily Log"):
        row = [
            datetime.now().strftime("%Y-%m-%d"),
            age, gender,
            took_ulcer_med, med_time.strftime("%H:%M"),
            pain_rating,
            ";".join(symptoms) or "None",
            symptom_duration, symptom_change,
            ";".join(meals) or "None",
            ";".join(trigger_causes) or "None",
            ate_triggers, skipped_meal, ate_late,
            took_nsaid, stress,
            cancer_diag, family_history,
            h_pylori_ulcer,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
        st.success("Your daily log has been saved!")

