import google.generativeai as genai
import PyPDF2
import time
import re
from fpdf import FPDF
from google.colab import files

genai.configure(api_key="AIzaSyDBHqTdwuLcAvK6rgCqtyfdBCHWS_GSSD8")

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
    models = ["models/gemini-1.5-pro", "models/gemini-1.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]

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

    for segment in segments:
        if bold_pattern.match(segment):
            pdf.set_font('Arial', 'B', 12)
            clean_text = re.sub(r'\*\*|__', '', segment)
        elif underline_pattern.match(segment):
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 255)
            clean_text = re.sub(r'_+|~+', '', segment)
        elif h1_pattern.match(segment):
            pdf.set_font('Arial', 'B', 16)
            clean_text = re.sub(r'^#\s+', '', segment)
        elif h2_pattern.match(segment):
            pdf.set_font('Arial', 'B', 14)
            clean_text = re.sub(r'^##\s+', '', segment)
        elif bullet_pattern.match(segment):
            pdf.set_font('Arial', '', 10)
            pdf.cell(5, 5, "•", ln=0)
            clean_text = re.sub(r'\*', '', segment)
        else:
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)
            clean_text = segment

        pdf.multi_cell(0, 5, clean_text.encode('latin-1', 'ignore').decode('latin-1'))

    pdf_file_name = "Generated_Notes.pdf"
    pdf.output(pdf_file_name)
    print(f"✅ Notes saved as: {pdf_file_name}")

pdf_path = choose_file()
if pdf_path:
    note(pdf_path)
