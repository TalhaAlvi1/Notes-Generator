import google.generative as genai
import requests
import PyPDF2
import pdf
import time

genai.configure(api_key ="                ")


def choose_file():
    """Allows user to upload a PDF in Google Colab"""
    uploaded = files.upload()
    if uploaded:
        return list(uploaded.keys())[0]
    return None

def send_content(message):
    generation_config = {
        "temperature": 0.8,
        "top_k": 60,
        "top_p": 0.9,
        "max_output_tokens": 300,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(f"""
    Analyze the outline and extract topics only.
    - Do NOT include 'Topics Included' as a heading.
    - Ignore attendance, presentations, and book names.
    - Keep topics short and simple.
    {message}
    """)
    
def save_to_pdf(text):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.set_auto_page_break(auto=True, margin=10)

    bold_pattern = re.compile(r'\*\*(.*?)\*\*|__(.*?)__')
    underline_pattern = re.compile(r'_(.*?)_|~~(.*?)~~')
    bullet_pattern = re.compile(r'\*(.*)', re.MULTILINE)
    h1_pattern = re.compile(r'^#\s+(.+)', re.MULTILINE)
    h2_pattern = re.compile(r'^##\s+(.+)', re.MULTILINE)

    segments = re.split(r'(\*\*.*?\*\*|__.*?__|_.*?_|~~.*?~~|-\s.*)', text)


    return response.text

def engine(topic, model_name):
    generation_config = {
        "temperature": 0.8,
        "top_k": 60,
        "top_p": 0.9,
        "max_output_tokens": 1000,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(f"""
    Generate detailed, easy-to-understand notes on: {topic}.
    Ensure completeness and clarity.
    """)

    return response.text

def note(pdf_file):
    extracted_text = ""
    final_notes = ""
    models = ["models/gemini-1.5-pro", "models/gemini-1.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"] # Changed here: remove empty string

    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text = page.extract_text()
            extracted_text += send_content(text) + "\n\n"
            time.sleep(3)

    topics_list = [line.strip() for line in extracted_text.split("\n") if line.strip()]

    mod = 0
    for i, topic in enumerate(topics_list):
        mod = (mod + 1) % len(models)
        notes = engine(topic, models[mod])
        final_notes += notes + "\n\n"
        time.sleep(5)

    save_to_pdf(final_notes)
