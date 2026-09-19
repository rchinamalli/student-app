import re
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "students.csv"
COLUMNS = [
    "student_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "date_of_birth",
    "gender",
    "grade",
    "address",
    "registered_on",
]
GRADES = [f"Grade {n}" for n in range(1, 13)] + ["Undergraduate", "Graduate"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_students() -> pd.DataFrame:
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=COLUMNS)


def save_student(record: dict) -> None:
    df = pd.concat([load_students(), pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


def validate(record: dict, existing: pd.DataFrame) -> list[str]:
    errors = []
    if not record["student_id"]:
        errors.append("Student ID is required.")
    elif record["student_id"] in existing["student_id"].values:
        errors.append(f"Student ID {record['student_id']} already exists.")
    if not record["first_name"] or not record["last_name"]:
        errors.append("First and last name are required.")
    if not EMAIL_RE.match(record["email"]):
        errors.append("Enter a valid email address.")
    if record["phone"] and not re.fullmatch(r"[\d\s()+\-]{7,20}", record["phone"]):
        errors.append("Enter a valid phone number.")
    return errors


st.set_page_config(page_title="Student Information", page_icon="🎓", layout="centered")
st.title("🎓 Student Information")

tab_add, tab_view = st.tabs(["Add student", "View records"])

with tab_add:
    with st.form("student_form", clear_on_submit=True):
        student_id = st.text_input("Student ID *")
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First name *")
        last_name = col2.text_input("Last name *")
        col3, col4 = st.columns(2)
        email = col3.text_input("Email *")
        phone = col4.text_input("Phone")
        col5, col6, col7 = st.columns(3)
        dob = col5.date_input(
            "Date of birth",
            value=date(2005, 1, 1),
            min_value=date(1950, 1, 1),
            max_value=date.today(),
        )
        gender = col6.selectbox("Gender", ["Female", "Male", "Non-binary", "Prefer not to say"])
        grade = col7.selectbox("Grade / Level", GRADES)
        address = st.text_area("Address")
        submitted = st.form_submit_button("Save student", type="primary")

    if submitted:
        record = {
            "student_id": student_id.strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "date_of_birth": dob.isoformat(),
            "gender": gender,
            "grade": grade,
            "address": address.strip(),
            "registered_on": date.today().isoformat(),
        }
        errors = validate(record, load_students())
        if errors:
            for msg in errors:
                st.error(msg)
        else:
            save_student(record)
            st.success(f"Saved {record['first_name']} {record['last_name']} to {DATA_FILE.name}.")

with tab_view:
    students = load_students()
    st.caption(f"{len(students)} student(s) stored in {DATA_FILE.name}")
    query = st.text_input("Search by name, ID or email")
    if query:
        mask = students.apply(
            lambda row: query.lower() in " ".join(row.astype(str)).lower(), axis=1
        )
        students = students[mask]
    st.dataframe(students, width="stretch", hide_index=True)
    if not students.empty:
        st.download_button(
            "Download CSV",
            students.to_csv(index=False),
            file_name="students.csv",
            mime="text/csv",
        )
