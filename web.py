import streamlit as st
import pycountry
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# ─── ENVIRONMENT & LLM CONFIG ───────────────────────────────
API_KEY = st.secrets.get("NVIDIA_API_KEY", "")
if not API_KEY or not API_KEY.startswith("nvapi-"):
    st.stop()  # Stop app with no error trace
    raise RuntimeError("Invalid or missing NVIDIA_API_KEY in Streamlit Secrets")

llm = ChatNVIDIA(
    model="meta/llama-3.2-3b-instruct",
    temperature=0.4,
    top_p=0.7,
    api_key=API_KEY
)

# ─── SKILLS GENERATION ───────────────────────────────────────
def generate_skills(job_title):
    prompt = f"""
    List 15 key skills required for the role of a {job_title}.
    Provide a plain, unnumbered, comma-separated list. No formatting or bullet points.
    """
    try:
        response = llm.invoke(prompt)
        skills = [skill.strip() for skill in response.content.split(',') if skill.strip()]
        return skills
    except Exception as e:
        st.error(f"Error generating skills: {e}")
        return []

# ─── JOB DESCRIPTION GENERATION ──────────────────────────────
def generate_job_description(job_title, department, work_mode, experience_range, experience_level, employment_type, mandatory_skills, selected_skills, location, salary_range, salary_basis, education=None, number_of_openings=None):
    prompt = f"""
    Write a detailed and professional job description for the role of {job_title} with the following details:
    """

    if department:
        prompt += f"\n- Department: {department}."

    prompt += f"""
    - Work Mode: {work_mode}.
    - Experience: {experience_range} years ({experience_level}).
    - Employment Type: {employment_type}.
    - Location: {location}.
    - Salary: {salary_range} ({salary_basis}).
    """

    if education:
        prompt += f"\n- Education: {education}."
    if number_of_openings:
        prompt += f"\n- Openings: {number_of_openings}."

    prompt += f"""
    ### Mandatory Skills
    - {', '.join(mandatory_skills)}.

    ### Preferred Skills
    - {', '.join(selected_skills)}.

    ### Instructions:
    - Use a professional and concise tone.
    - Include responsibilities and qualifications.
    - Do not invent skills outside those listed.
    """

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"Error generating job description: {e}")
        return "Error"

# ─── STREAMLIT APP ───────────────────────────────────────────
def main():
    st.set_page_config(page_title="Job Description Generator", layout="wide")

    st.markdown("""
        <style>body {background-color: #f0f7ff;}</style>
    """, unsafe_allow_html=True)

    st.title("🧠 Job Description Generator (NVIDIA LLM)")
    st.markdown("Fill in the details below to generate a professional job description.")

    st.subheader("🛠️ Basic Job Details")
    job_title = st.text_input("Job Title", placeholder="e.g., Data Scientist")

    department = st.selectbox("Department (Optional)", [""] + [
        "IT", "Marketing", "Finance", "HR", "Sales", "Engineering", "Operations",
        "Legal", "Product Management", "Customer Support", "Design", "R&D"
    ])
    department = None if department == "" else department

    work_mode = st.radio("Work Mode", ["In-Office", "Hybrid", "Remote"])

    col1, col2 = st.columns(2)
    with col1:
        experience_start = st.number_input("Min Experience (Years)", min_value=0, step=1, value=0)
    with col2:
        experience_end = st.number_input("Max Experience (Years)", min_value=experience_start, step=1, value=experience_start + 1)

    countries = ["Select Location"] + [c.name for c in pycountry.countries]
    location = st.selectbox("Location", countries)
    experience_level = st.selectbox("Experience Level", ["Select"] + ['Entry', 'Associate', 'Mid-Senior', 'Director/VP', 'Executive/President'])
    employment_type = st.selectbox("Employment Type", ["Select"] + ['Full-Time', 'Part-Time', 'Contract', 'Internship', 'Freelance'])

    salary_basis = st.selectbox("Salary Basis", ["Select"] + ["Hourly", "Monthly", "Annual"])
    col3, col4 = st.columns(2)
    with col3:
        min_salary = st.number_input("Min Salary", min_value=0, step=1000)
    with col4:
        max_salary = st.number_input("Max Salary", min_value=min_salary, step=1000)

    st.subheader("🧩 Skills Section")
    if not job_title:
        st.info("Please enter a job title to generate skills.")
        return

    if 'skills' not in st.session_state or st.session_state.get('last_job_title') != job_title:
        skills = generate_skills(job_title)
        st.session_state['skills'] = skills[:20]
        st.session_state['mandatory_skills'] = []
        st.session_state['selected_skills'] = skills.copy()
        st.session_state['last_job_title'] = job_title

    skills = st.session_state['skills']

    mandatory_skills = st.multiselect("Mandatory Skills", options=skills, default=st.session_state.get('mandatory_skills', []))
    st.session_state['mandatory_skills'] = mandatory_skills

    selected_skills = st.multiselect("Preferred Skills", options=skills, default=st.session_state.get('selected_skills', skills))
    st.session_state['selected_skills'] = selected_skills

    new_skill = st.text_input("Add Custom Skill")
    if st.button("Add Skill") and new_skill.strip():
        if new_skill not in skills:
            skills.append(new_skill)
            st.session_state['skills'] = skills
            st.session_state['selected_skills'].append(new_skill)
            st.session_state['mandatory_skills'].append(new_skill)

    if st.button("Remove Selected Skills"):
        for skill in selected_skills:
            if skill in skills:
                skills.remove(skill)
        st.session_state['skills'] = skills

    if not mandatory_skills:
        st.error("Select at least one mandatory skill.")
        return

    st.subheader("📘 Optional Details")
    education = st.selectbox("Education (Optional)", [""] + [
        "High School Diploma", "Associate's Degree", "Bachelor's Degree",
        "Master's Degree", "Ph.D.", "Diploma", "Certification", "Other"
    ])
    education = None if education == "" else education

    number_of_openings = st.number_input("Number of Openings (Optional)", min_value=1, step=1, value=1) if st.checkbox("Specify Openings") else None

    if st.button("🚀 Generate Job Description"):
        if location == "Select Location" or experience_level == "Select" or employment_type == "Select" or salary_basis == "Select":
            st.error("Please complete all required fields.")
            return

        st.info("Generating job description...")
        experience_range = f"{experience_start}-{experience_end}"
        salary_range = f"{min_salary}-{max_salary}"

        job_description = generate_job_description(
            job_title, department, work_mode, experience_range,
            experience_level, employment_type,
            mandatory_skills, selected_skills,
            location, salary_range, salary_basis,
            education, number_of_openings
        )
        st.subheader("📄 Generated Job Description")
        st.text_area("Job Description Output", job_description, height=400)

if __name__ == "__main__":
    main()
