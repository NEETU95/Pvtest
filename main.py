from fastapi import FastAPI, HTTPException, APIRouter
import requests
from PyPDF2 import PdfReader
from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
import spacy
import pysftp
from fastapi import FastAPI


# Create a FastAPI instance
router = APIRouter()


@router.post("/pdf-to-json")
def pdf_extraction(pdf_info:str):
    try:
        ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969')
        with ftp.cd('/var/sftp/upload/pvtestusers/'):
            files = ftp.listdir()
            for file in files:
                if pdf_info in file:
                    ftp.get(file)
                    print('yes downloaded both files')
                    if 'Weekly' in file:
                        weekly_reader = file
                    else:
                        source_document = file
        weekly_reader = PdfReader(weekly_reader)
        source_file_reader = PdfReader(source_document)
        # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
        weekly_reader_num_pages = len(weekly_reader.pages)

        source_file_num_pages = len(source_file_reader.pages)
        weekly_text = ""
        all_text = ""
        nlp = spacy.load("en_core_web_sm")
        nlp_1 = spacy.load("en_ner_bc5cdr_md")
        # Loop through all pages and extract text
        for page_num in range(source_file_num_pages):
            page = source_file_reader.pages[page_num]
            text = page.extract_text()
            all_text += text
        for page_num in range(weekly_reader_num_pages):
            page = weekly_reader.pages[page_num]
            text = page.extract_text()
            weekly_text += text
        meta = source_file_reader.metadata
        general_extraction, reporter_extraction = get_general_reporter(
            source_text=all_text,
            weekly_text_1=weekly_text,
            en_core=nlp,
            meta_data=meta
        )
        print(general_extraction, reporter_extraction)
        patient_extraction = get_patient_text(source_text=all_text, en_core=nlp,bcd5r=nlp_1)
        parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)

        response = {
            "general_information": general_extraction,
            "reporter": reporter_extraction,
            "patient": patient_extraction,
            "parent": parent_extraction
        }


        url = "https://demo.topiatech.co.uk/PV/createCaseAI"

        # Send the POST request with JSON data
        response = requests.post(url, json=response)

        # Check the response status code
        if response.status_code == 200:
            # Request was successful
            print("API request successful.")
            print("Status Code:", response.status_code)
            print("Response Headers:", response.headers)

        else:
            # Request failed
            print(f"API request failed with status code {response.status_code}: {response.text}")
            print(response.text)

    #   if ftp:
    #         ftp.close()

        return response.status_code

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


app = FastAPI()

app.include_router(pdf_extraction.router, prefix="/api", tags=["pdf_extraction"])