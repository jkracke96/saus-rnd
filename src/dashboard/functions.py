import requests
from bs4 import BeautifulSoup
import os
from io import BytesIO # To handle binary stream in memory
from azure.storage.blob import BlobServiceClient
import PyPDF2
from openai import AzureOpenAI 
from django.conf import settings


AZURE_STORAGE_CONNECTION_STRING = settings.AZURE_ACCOUNT_CONNECTION_STRING
CONTAINER_NAME = settings.AZURE_CONTAINER
AZURE_OPENAI_API_KEY = settings.AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
OPENAI_API_VERSION = settings.OPENAI_API_VERSION
OPENAI_MODEL = settings.OPENAI_MODEL


# --- 1. Access and Download the PDF from Blob Storage ---
def download_blob_to_stream(blob_name, connection_string=AZURE_STORAGE_CONNECTION_STRING, container_name=CONTAINER_NAME):
    """Downloads a blob content into an in-memory stream."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Download the blob content into a BytesIO stream
        stream = BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0) # Reset stream position to the beginning
        print(f"Successfully downloaded {blob_name} to stream.")
        return stream
    except Exception as e:
        print(f"Error downloading blob {blob_name}: {e}")
        return None

# --- 2. Extract Text from the PDF Stream ---
def extract_text_from_pdf_stream(pdf_stream):
    """Extracts text from a PDF file stream."""
    try:
        reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n" # Add newline between pages
        print("Successfully extracted text from PDF.")
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def get_text_from_url(url):
    response = requests.get(url)
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    title = soup.title.string if soup.title else 'No title found'
    return {'text': text, 'title': title}


def get_latest_cv(user_id, cv_documents_obj):
    # Get the latest CV document for the user
    latest_cv = cv_documents_obj.objects.filter(user_id=user_id).order_by('-uploaded_at').first()
    if latest_cv:
        return latest_cv.file.name
    else:
        return None
    

def generate_custom_cv(cv_text, job_description):
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,  
        api_version=OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )
    custom_cv = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"Generate a custom CV based on the following CV text and job description:\n\nCV Text: {cv_text}\n\nJob Description: {job_description}" \
                f"\n\nPlease ensure the CV is tailored to the job description and highlights relevant skills and experiences." \
                f"\n\nFormat the CV in a professional manner, including sections for contact information, summary, skills, experience, and education." \
                f"\n\nMake sure to not invent any skills and dont mix up the different positions. Fit everything on max 2 din a 4 pages." \
                f"For you response, only return a visually appealing and matching the type of job html code as plain text. Nothing else. Afterwards, I want to transform it to a pdf." \
            }
        ],
    )
    return custom_cv.choices[0].message.content
            

