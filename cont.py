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

