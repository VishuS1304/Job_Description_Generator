import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pycountry

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_skills(job_title):
    prompt_1 = f"""
    List 15 key skills required for the role of a {job_title}.
    Provide a plain, unnumbered, and unformatted list of skills, separated by commas. Avoid headings or bullet points.
    """
    try:
        # Create the generative model instance
        model = genai.GenerativeModel('gemini-pro')
        response_1 = model.generate_content(prompt_1)

        # Split the response by commas and clean up any whitespace
        skills = [skill.strip() for skill in response_1.text.split(',') if skill.strip()]
        return skills
    except Exception as e:
        st.error(f"Error generating skills: {e}")

# Function to generate job description using Gemini API
def generate_job_description(job_title, department, work_mode, experience_range, experience_level, employment_type, mandatory_skills, selected_skills, location, salary_range, salary_basis, education=None, number_of_openings=None):
    # Start building the prompt
    prompt = f"""
    Write a detailed and professional job description for the role of {job_title}. Incorporate all the key details provided below:
    """

    # Adding department if specified
    if department:
        prompt += f"\n- Department: {department}."
    
    # Add mandatory details
    prompt += f"""
    - Work Mode: {work_mode}.
    - Experience Required: {experience_range} years ({experience_level} level).
    - Employment Type: {employment_type}.
    - Location: {location}.
    - Salary Range: {salary_range} ({salary_basis}).
    """

    # Add optional education and openings if specified
    if education:
        prompt += f"\n- Required Education: {education}."
    if number_of_openings:
        prompt += f"\n- Number of Openings: {number_of_openings}."

    # Include mandatory skills
    prompt += f"""
    ### Mandatory Skills
    Include the following as the mandatory skills required for the job:
    - {', '.join(mandatory_skills)}.
    Ensure that only these skills are labeled as mandatory and avoid including any other skills as mandatory.
    """

    # Include preferred skills
    if selected_skills:
        prompt += f"""
        ### Preferred Skills
        Highlight the following skills as preferred skills for the job:
        - {', '.join(selected_skills)}.
        Ensure that only these skills are presented as preferred skills and avoid including any other skills in this category.
        """

    # Additional instructions for the content
    prompt += """
    ### Additional Instructions
    - The job description should include detailed responsibilities and qualifications.
    - Clearly distinguish between mandatory and preferred skills.
    - Use a professional and concise tone.
    - Ensure all details provided above are accurately incorporated into the job description.
    """

    # Try generating the response
    try:
        model = genai.GenerativeModel('gemini-pro')  
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating content: {e}")


# Streamlit App
def main():
    # Set page config for wide layout and custom page title
    st.set_page_config(page_title="Job Description Generator", layout="wide")

    # Add background color using custom CSS
    st.markdown(
        """
        <style>
        body {
             background-color: #e6f7ff
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Job Description Generator")
    st.markdown("Fill in the details below to generate a professional job description.")

    # Input fields
    st.subheader("Basic Job Details")
    job_title = st.text_input("Job Title", placeholder="Enter job title (e.g., Data Scientist)", help="This is the title of the job you want to generate a description for.")
    
    departments = [
    "",  # Empty option for the user to select
    "IT", "Marketing", "Finance", "HR", "Sales", "Engineering", "Operations", 
    "Legal", "Product Management", "Customer Support", "Design", "R&D"
    ]
    department = st.selectbox("Department (Optional)", options=departments, format_func=lambda x: "Select Department" if x == "" else x, help="Select the department this role belongs to. If unsure, you can leave this blank.")
    department = None if department == "" else department

    work_mode = st.radio("Work Mode", options=["In-Office", "Hybrid", "Remote"], help="Specify the working mode for this role. Choose 'In-Office' for on-site roles, 'Hybrid' for a mix of on-site and remote, or 'Remote' for fully remote positions.")

    # Work experience range
    col1, col2 = st.columns(2)
    with col1:
        experience_start = st.number_input("Minimum Experience (Years)", min_value=0, step=1, value=0)
    with col2:
        experience_end = st.number_input("Maximum Experience (Years)", min_value=experience_start, step=1, value=experience_start + 1)

    # Country/Place selection using pycountry
    countries = ["Select the Location"] + [country.name for country in pycountry.countries]
    location = st.selectbox("Location (Country/Place)", options=countries, help="Specify the location for the job.")
    
    # Experience level
    experience_levels = ["Select Experience Level"] + ['Entry', 'Associate', 'Mid-Senior', 'Director/VP', 'Executive/President']
    experience_level = st.selectbox("Experience Level", options=experience_levels, help="Specify the level of experience required for this role. For example, 'Entry' for beginners or 'Mid-Senior' for experienced professionals.")

    # Employment type
    employment_types = ["Select Employment Type"] + ['Full-Time', 'Part-Time', 'Contract', 'Internship', 'Freelance']
    employment_type = st.selectbox("Employment Type", options=employment_types, help="Specify the type of employment for this role. For example, 'Full-Time' for permanent roles or 'Internship' for student opportunities.")

    # Salary range
    salary_basis_options =  ["Select Salary Basis"] + ["Hourly", "Monthly", "Annual"]
    salary_basis = st.selectbox("Salary Basis", options=salary_basis_options, help="Select how the salary is structured for this role: Hourly, Monthly, or Annual.")
    col3, col4 = st.columns(2)
    with col3:
        min_salary = st.number_input(f"Minimum Salary ({salary_basis})", min_value=0, step=1, value=0)
    with col4:
        max_salary = st.number_input(f"Maximum Salary ({salary_basis})", min_value=min_salary, step=1, value=min_salary + 1)
    
    # Skills Section
    st.subheader("Skills Required")
    if not job_title:
        st.error("Please enter a job title to generate skills.")
    else:
        # Generate skills based on job title and store in session state
        if 'skills' not in st.session_state or st.session_state.get('last_job_title') != job_title:
            skills = generate_skills(job_title)
            st.session_state['skills'] = skills[:20]
            st.session_state['last_job_title'] = job_title
            st.session_state['mandatory_skills'] = []  # Initialize starred skills
            st.session_state['selected_skills'] = skills.copy()
        # Display generated skills with checkboxes
        skills = st.session_state['skills']
        
        st.write("### Generated Skills")
        mandatory_skills = st.multiselect("Select Mandatory Skills", options=skills, default=st.session_state.get('mandatory_skills', []), 
                                          help= "Select the skills that are absolutely necessary for this role. These will be marked as mandatory.")
        st.session_state['mandatory_skills'] = mandatory_skills
        #st.session_state['mandatory_skills'] = mandatory_skills

        # Add Required skills selection
        selected_skills = st.multiselect(
            "Select Required Skills",
            options=skills,default=st.session_state.get('selected_skills', skills),
            help="Select the skills that are Required for this role. You can select multiple skills."
        )
        st.session_state['selected_skills'] = selected_skills  # Save selection to session state

        # Allow adding custom skills
        new_skill = st.text_input("Add a Custom Skill")
        if st.button("Add Skill") and new_skill:
            new_skill = new_skill.strip()
            if new_skill not in skills:
                skills.append(new_skill)
                st.session_state['skills'] = skills
                st.session_state['selected_skills'].append(new_skill)  # Add new skill to required skills
                st.session_state['mandatory_skills'].append(new_skill)

        # Allow removing custom skills
        if st.button("Remove Selected Skills"):
            for skill in selected_skills:
                skills.remove(skill)
            st.session_state['skills'] = skills



        # Validation: Ensure at least one important skill
        if len(mandatory_skills) <1:
            st.error("Please select at least one skill as mandatory for this job role.")

    # Education Section
    st.subheader("Optional Details")
    education_levels = [
    "",  # Empty option for optional selection
    "High School Diploma", "Associate's Degree", "Bachelor's Degree", "Master's Degree", 
    "Ph.D.", "Doctorate", "Diploma", "Certification", "Other"
    ]
    education = st.selectbox("Education Level (Optional)", options=education_levels, format_func=lambda x: "Select Education" if x == "" else x,  help="Select the required education level for the position. If not applicable, you can leave this blank.")
    education = None if education == "" else education

    # Number of openings
    number_of_openings = st.number_input(
        "Number of Openings (Optional)", min_value=1, step=1, value=1, key="num_openings", help="Specify how many positions are available for this role. Leave blank for a single opening."
    ) if st.checkbox("Specify Number of Openings") else None

    # Generate button
    if st.button("Generate Job Description"):
        if  (job_title and work_mode and experience_start <= experience_end and experience_level!="Select Experience Level" and employment_type!="Select Employment Type" and location != "Select the Location"  and 
             
             min_salary <= max_salary
        and mandatory_skills and selected_skills and salary_basis!="Select Salary Basis"):
            print(location)
            st.info("Generating job description...")
            salary_range = f"{min_salary}-{max_salary}"
            st.write(selected_skills)
            experience_range = f"{experience_start}-{experience_end} years"
            job_description = generate_job_description(
                job_title, department, work_mode, experience_range, experience_level, employment_type, mandatory_skills,selected_skills, location, salary_range, salary_basis, education, number_of_openings
            )
            st.subheader("Generated Job Description:")
            st.text_area("Output", value=job_description, height=300)
        else:
            st.error("Please fill out all the fields correctly and ensure at least one mandatory skills are selected.")

if __name__ == "__main__":
    main()