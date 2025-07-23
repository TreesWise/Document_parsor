# import os
# import shutil
# import uuid
# import json
# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# from current_doc_parsor import process_document_to_json
# from fastapi.security.api_key import APIKeyHeader
# import tempfile


# from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Security, Depends


# from dict_file import mapping_dict


# app = FastAPI(title="Document Parser API", version="1.0")

# # Secure API Key Authentication
# API_KEY = os.getenv("your_secure_api_key")
# API_KEY_NAME = os.getenv("api_key_name")
 

# # Define API Key Security
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     """Validate API Key"""
#     if not api_key or api_key != API_KEY:
#         raise HTTPException(status_code=403, detail=" Invalid API Key")
#     return api_key



# # UPLOAD_DIR = "uploads"
# # os.makedirs(UPLOAD_DIR, exist_ok=True)

# @app.post("/upload/")

# async def upload_file(api_key: str = Depends(verify_api_key), file: UploadFile = File(...),Doctype: str = Form("")):
    
#     file_ext = os.path.splitext(file.filename)[1]
#     if file_ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
#         return JSONResponse({"error": "Only PDF or image files allowed."}, status_code=400)

#     # temp_filename = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")
#     # with open(temp_filename, "wb") as buffer:
#     #     shutil.copyfileobj(file.file, buffer)
#     with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as temp_file:
#         shutil.copyfileobj(file.file, temp_file)
#         temp_file_path = temp_file.name

#     try:
#         result = process_document_to_json(temp_file_path)

#         # If result is a JSON string, convert it to a Python object
#         if isinstance(result, str):
#             result = json.loads(result)

#         # Normalize and flatten the mapping dictionary
#         normalized_mapping = {}
#         for key, value in mapping_dict.items():
#             aliases = [alias.strip().lower() for alias in key.split("/")]
#             for alias in aliases:
#                 normalized_mapping[alias] = value

#         # Perform docName mapping
#         for item in result:
#             original_doc_name = item.get("docName", "").strip().lower()
#             mapped_doc_name = normalized_mapping.get(original_doc_name)
#             if mapped_doc_name:
#                 item["docName"] = mapped_doc_name

#         return JSONResponse(content=result, media_type="application/json")

#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)
#     finally:
#         os.remove(temp_file_path)




import os
import shutil
import uuid
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from current_doc_parsor import process_document_to_json
from fastapi.security.api_key import APIKeyHeader
import tempfile
import platform
import asyncio
from dotenv import load_dotenv
from fastapi import HTTPException, Form, Security, Depends
from dict_file import mapping_dict
from country_mapping import country_mapping

import subprocess
import asyncio

load_dotenv()

app = FastAPI(title="Document Parser API", version="1.0")

# Secure API Key Authentication
API_KEY = os.getenv("your_secure_api_key")
API_KEY_NAME = os.getenv("api_key_name")

# Define API Key Security
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate API Key"""
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=403, detail=" Invalid API Key")
    return api_key


# Function to convert DOCX to PDF (Linux or Windows)
async def convert_docx_to_pdf(docx_path):
    """ Converts DOCX to PDF using LibreOffice (Linux) or Microsoft Word (Windows). """
    pdf_path = docx_path.replace(".docx", ".pdf")

    try:
        if platform.system() == "Windows":
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Documents.Open(os.path.abspath(docx_path))
            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # PDF format
            doc.Close()
            word.Quit()
            print(f"Converted {docx_path} to {pdf_path} using Microsoft Word")
        else:
            libreoffice_path = "/usr/bin/libreoffice"
            if not os.path.exists(libreoffice_path):
                raise FileNotFoundError(f"LibreOffice not found at {libreoffice_path}")

            process = await asyncio.create_subprocess_exec(
                libreoffice_path, "--headless", "--convert-to", "pdf",
                "--outdir", os.path.dirname(docx_path), docx_path
            )
            await process.communicate()  # Ensure subprocess completes

            print(f"Converted {docx_path} to {pdf_path} using LibreOffice")

        return pdf_path
    except Exception as e:
        print(f"DOCX to PDF conversion failed: {e}")
        raise HTTPException(status_code=500, detail=f"DOCX to PDF conversion failed: {e}")


# Endpoint for uploading the file
@app.post("/upload/")
async def upload_file(api_key: str = Depends(verify_api_key), file: UploadFile = File(...), Doctype: str = Form("")):
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".jpg", ".jpeg", ".png", ".docx"]:
        return JSONResponse({"error": "Only PDF, DOCX, or image files allowed."}, status_code=400)

    # Handle DOCX conversion if the file is a DOCX
    if file_ext == ".docx":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        try:
            pdf_path = await convert_docx_to_pdf(temp_file_path)
            result = process_document_to_json(pdf_path)
            # return JSONResponse(content=result, media_type="application/json")
            # if isinstance(result, str):
            #     result = json.loads(result)

            # Normalize and flatten the mapping dictionary
            normalized_mapping = {}
            for key, value in mapping_dict.items():
                aliases = [alias.strip().lower() for alias in key.split("/")]
                for alias in aliases:
                    normalized_mapping[alias] = value

            # Perform docName mapping
            for item in result:
                original_doc_name = item.get("docName", "").strip().lower()
                mapped_doc_name = normalized_mapping.get(original_doc_name)
                if mapped_doc_name:
                    item["docName"] = mapped_doc_name

            return JSONResponse(content=result, media_type="application/json")
        
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
        finally:
            os.remove(temp_file_path)
    else:
        # Handle PDF and image files as before
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        try:
            result = process_document_to_json(temp_file_path)

            # If result is a JSON string, convert it to a Python object
            if isinstance(result, str):
                result = json.loads(result)

            # Normalize and flatten the mapping dictionary
            normalized_mapping = {}
            for key, value in mapping_dict.items():
                aliases = [alias.strip().lower() for alias in key.split("/")]
                for alias in aliases:
                    normalized_mapping[alias] = value

            # Perform docName mapping
            for item in result:
                original_doc_name = item.get("docName", "").strip().lower()
                mapped_doc_name = normalized_mapping.get(original_doc_name)
                if mapped_doc_name:
                    item["docName"] = mapped_doc_name
                  # Perform issuedCountry mapping
                original_country = item.get("issuedCountry", "").strip().lower()
                for key, value in country_mapping.items():
                    if key.strip().lower() == original_country:
                        item["issuedCountry"] = value
                        break

            return JSONResponse(content=result, media_type="application/json")

        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
        finally:
            os.remove(temp_file_path)
