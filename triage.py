import streamlit as st
import re
import requests

# Streamlit App Title
st.title("AiDentify's AI-Powered Dental Triage Model")

# Function to get or set the OpenAI API key
def get_openai_api_key():
    if 'openai_api_key' not in st.session_state:
        st.session_state['openai_api_key'] = ''
    api_key = st.text_input("Enter your OpenAI API key:", type="password", value=st.session_state['openai_api_key'])
    st.session_state['openai_api_key'] = api_key
    return api_key

# Function to generate the triaging response
def generate_dental_triage(subjective_info):
    api_key = st.session_state['openai_api_key']
    if not api_key:
        return "Error: Please enter a valid OpenAI API key to use this feature."
    
    # Prepare the request headers and data
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a dental expert assisting in triage."},
            {"role": "user", "content": f"Provide a comprehensive triaging assessment for this subjective information: {subjective_info}"}
        ]
    }

    # Send the request to the OpenAI API endpoint
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()  # Raises an error for bad responses
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract key symptoms and details from patient input
def extract_dental_info(conversation):
    # Extract subjective (patient-reported) information
    subjective_match = re.search(r'Symptoms:(.*?)(?:$', conversation, re.DOTALL | re.IGNORECASE)
    subjective = subjective_match.group(1).strip() if subjective_match else "No symptoms reported."
    return subjective

# Ensure the API key is requested first and stored
api_key = get_openai_api_key()

if api_key:
    # Only show the triage form if the API key is provided
    st.subheader("Dental Triage Information")

    # Input for dental symptoms
    st.write("### Please provide your symptoms by selecting options or entering details below.")

    # Predefined dental symptom options
    common_symptoms = st.multiselect(
        "Select common symptoms you are experiencing:",
        ["Toothache", "Swelling in mouth or face", "Bleeding gums", "Jaw pain", "Sensitivity to hot/cold", "Bad breath", "Mouth sores"]
    )

    # Additional questions to gather more information about the condition
    st.write("### Triage Questions")

    pain_level = st.selectbox("How severe is the pain?", ["No pain", "Mild", "Moderate", "Severe"])
    symptom_duration = st.selectbox("How long have you been experiencing these symptoms?", ["Less than a day", "1-3 days", "4-7 days", "More than a week"])
    location = st.radio("Is the pain or discomfort localized in one area or spread across your mouth?", ["Localized", "Spread across"])

    # Free-text input for symptoms not covered by predefined options
    free_text_symptoms = st.text_area("Describe any other symptoms you are experiencing (optional):", height=100)

    # Combine inputs for triage processing
    if st.button('Generate Triage Assessment'):
        # Combine selected symptoms with free-text input
        all_symptoms = ', '.join(common_symptoms)
        combined_symptoms = f"Common symptoms: {all_symptoms}\nPain level: {pain_level}\nSymptom duration: {symptom_duration}\nPain location: {location}\nOther symptoms: {free_text_symptoms}"

        # Display extracted subjective info
        st.subheader('Collected Information for Triage')
        st.write(combined_symptoms)

        # Generate and display triage assessment using OpenAI
        with st.spinner("Generating dental triage assessment..."):
            triage_note = generate_dental_triage(combined_symptoms)
        st.subheader('Generated Triage Assessment')
        st.text_area("", value=triage_note, height=400)

# Sidebar Information
st.sidebar.title('About')
st.sidebar.info('This app uses OpenAI\'s API to provide dental triage assessments based on patient-reported symptoms. It helps in recommending potential diagnoses, treatments, and next steps for patients in a dental care setting.')

# Add a note about the API key
st.sidebar.title('API Key')
st.sidebar.info('To use this app, you need to enter your OpenAI API key. The key is not stored permanently and must be re-entered each time you restart the app.')

# Disclaimer
st.sidebar.title('Disclaimer')
st.sidebar.warning('This app is for educational and demonstration purposes only. The information generated by the app should not be used for actual medical decision-making without review and approval by a licensed healthcare professional.')
