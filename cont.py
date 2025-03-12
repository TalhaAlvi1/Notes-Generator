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

    return response.text
