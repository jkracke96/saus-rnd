import requests
from bs4 import BeautifulSoup
import os
from io import BytesIO # To handle binary stream in memory
from azure.storage.blob import BlobServiceClient
import PyPDF2
from openai import AzureOpenAI 
from django.conf import settings
import uuid
from django.template.loader import render_to_string
from weasyprint import HTML


AZURE_STORAGE_CONNECTION_STRING = settings.AZURE_ACCOUNT_CONNECTION_STRING
CONTAINER_NAME = settings.AZURE_CONTAINER
AZURE_GENERATED_CV_CONTAINER=settings.AZURE_GENERATED_CV_CONTAINER
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


def convert_html_string_to_pdf_io(html_string):
    """
    Converts an HTML string into a BytesIO object containing PDF data.
    Returns BytesIO object on success, None on failure.
    """
    try:
        # Create an HTML object from the string
        html_string = html_string.replace("```html", "").replace("```", "")  # Remove newlines for better formatting
        html = HTML(string=html_string)

        # Render to PDF bytes
        pdf_bytes = html.write_pdf()

        # Wrap bytes in a BytesIO object (like an in-memory file)
        pdf_io = BytesIO(pdf_bytes)
        return pdf_io
    except Exception as e:
        # Log the error in a real application
        print(f"Error converting HTML to PDF: {e}")
        return None
    

def upload_pdf_io_to_azure(pdf_io, user_id, filename_prefix="generated_cv", connection_string=AZURE_STORAGE_CONNECTION_STRING):
    """
    Uploads a PDF BytesIO object to Azure Blob Storage.
    Returns the public URL of the uploaded blob on success, None on failure.
    """
    container_name = settings.AZURE_GENERATED_CV_CONTAINER

    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Generate a unique blob name (path within the container)
        # Using UUID helps prevent naming conflicts
        blob_name = f"{filename_prefix}/{user_id}/{uuid.uuid4()}.pdf"

        # Ensure the BytesIO cursor is at the beginning before uploading
        pdf_io.seek(0)

        # Upload the blob
        blob_client = container_client.upload_blob(name=blob_name, data=pdf_io, overwrite=True) # overwrite=True might be useful if you anticipate regenerating
        
        # Construct the blob URL
        pdf_url = blob_client.url

        response = {
            "pdf_url": pdf_url,
            "blob_name": blob_name,
        }
        
        return response

    except Exception as e:
        # Log the error in a real application
        print(f"Error uploading PDF to Azure Blob Storage: {e}")
        return None
            

