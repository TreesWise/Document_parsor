# import os
# import json
# import base64
# import fitz
# from dotenv import load_dotenv
# from openai import AzureOpenAI
# from datetime import datetime


# load_dotenv()

# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
# OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

# current_date = datetime.now().strftime("%d-%m-%Y")  # get today's date as dd-mm-yyyy

# print("current_date:",current_date)
# client = AzureOpenAI(
#     api_key=AZURE_OPENAI_API_KEY,
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_version=OPENAI_API_VERSION
# )

# def convert_to_base64(file_path):
#     ext = os.path.splitext(file_path)[-1].lower()
#     images_b64 = []

#     if ext == ".pdf":
#         doc = fitz.open(file_path)
#         for page in doc:
#             pix = page.get_pixmap(dpi=150)
#             b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
#             images_b64.append(b64)
#     elif ext in [".jpg", ".jpeg", ".png"]:
#         with open(file_path, "rb") as f:
#             b64 = base64.b64encode(f.read()).decode("utf-8")
#             images_b64.append(b64)
#     else:
#         raise ValueError("Unsupported file format.")
#     print("Image converted.............................................")
#     return images_b64




# def extract_json(images_b64):
#     prompt_text = f"""You are an expert in document data extraction. Extract and translate into English only the following details in JSON format:

# JSON Format:
# {{
#   "docName": "...",              
#   "DocNumber": "...",            
#   "uploadedDate": "{current_date}",
#   "issuedCountry": "...",     
#   "issueDate": "dd-mm-yyyy",     
#   "expDate": "dd-mm-yyyy",       
#   "isNationalDoc": "No"     
# }}

# Extract the following details from the document:

# 1. "docName" refers to the official name of the document (e.g., "Seafarer's Identity Document").Full name of the document, including the role or certification type if available (e.g., 'Certificate of Competency (Master)', 'Endorsement (GMDSS Radio Operator)')
# 2. "DocNumber" refers to the unique document number (e.g., "LM040496") or "Certificate Number" or "seamans book no" (if explicitly mentioned).
# 3. The "uploadedDate" field should NEVER be extracted from the document.
#    It must always be set to the current system date of extraction, which is "{current_date}".
# 4. "issuedCountry" refers to the country where the document was issued (e.g., "Spain").
# 5. "issueDate" refers to the document's issue date (ensure proper date format: dd-mm-yyyy).
# 6. "expDate" refers to the document's expiry date, if available.
# 7. "isNationalDoc" should default to "No".

# Instructions:
# - If the document contains multiple sections, endorsements, or certificates, **extract each separately** and return them as individual JSON objects.
# - **Only extract valid endorsements and documents** with **valid document numbers**. 
#     - **DocNumber** should correspond to the number explicitly labeled as "Doc Number," "Certificate No.," "seamansbook no.," or similar labels (avoid "Serial No" or "ID" unless explicitly labeled as such).
#     - If there are multiple numbers such as "Serial No" or "ID" numbers, **ensure to capture only the "DocNumber"**.
# - **Filter out irrelevant sections** (such as revalidation entries) that do not contain a valid "DocNumber" or issue/expiry dates.
# - Return the extracted information as **an array of JSON objects** if the document contains multiple valid sections.
# - Handle multiple documents or sections within a single file carefully, ensuring no entries are missed or merged incorrectly.
# - If there are multiple document numbers or expiry dates mentioned, capture all of them accurately.
# - The "uploadedDate" must always be set to the current system date of extraction, which is "{current_date}".
# - Do NOT extract "uploadedDate" from any part of the document.
# - Ensure **dates are in "dd-mm-yyyy" format**, and the **"DocNumber"** should be extracted exactly as seen on the document without any formatting changes.
# - Do not include unnecessary or incorrect values. Return only the required fields in **English**.
# If no convincing document data is available (i.e., no valid docName,DocNumber,issuedCountry, issue date, or expiry date), return null.

# Return the results as a **list of JSON objects**, one for each extracted document or endorsement section. Only include documents like endorsements or certificates with valid details.

# For each document, ensure:
# - The correct **DocNumber** is identified, and avoid confusing it with other numbers like "Serial No" or "ID" or number wothout any label unless clearly specified.
# - Handle each document as an individual entry.
# """

#     prompt = [
#         {
#             "type": "text",
#             "text": prompt_text
#         },
#         *[
#             {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/png;base64,{img}"
#                 }
#             } for img in images_b64
#         ]
#     ]

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     content = response.choices[0].message.content.strip()
#     if content.startswith("```json"):
#         content = content.replace("```json", "").replace("```", "").strip()

#     return content



# def postprocess_json(raw_json):
#     try:
#         json_objects = raw_json.split('}\n{')
#         if json_objects:
#             json_objects[0] += '}'
#             json_objects[-1] = '{' + json_objects[-1]
#         results = [json.loads(obj) for obj in json_objects]
#     except json.JSONDecodeError:
#         return raw_json

#     formatted = [] 
#     for obj in results:
#         known_fields = {
         
          
#             "docName": obj.get("docName", "").strip(),
#             "DocNumber": obj.get("DocNumber", "").strip(),
#             "uploadedDate": obj.get("uploadedDate", "Not Available"),
#             "issuedCountry": obj.get("issuedCountry", "").strip(),
#             "issueDate": obj.get("issueDate", "").strip(),
#             "expDate": obj.get("expDate", "Not Available").strip(),
           
#             "isNationalDoc": obj.get("isNationalDoc", "No").strip(),
   
#         }

#         # Capture any additional fields not listed in the known schema
#         extra_fields = {
#             k: v for k, v in obj.items()
#             if k not in known_fields and k not in known_fields.keys()
#         }

#         if extra_fields:
#             known_fields["metadata"] = extra_fields

#         formatted.append(known_fields)

#     return formatted






# def process_document_to_json(file_path):
#     images_b64 = convert_to_base64(file_path)
#     raw_json = extract_json(images_b64)
#     final_json = postprocess_json(raw_json)
 
#     return final_json







import os
import json
import base64
import fitz
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

current_date = datetime.now().strftime("%d-%m-%Y")  # get today's date as dd-mm-yyyy

print("current_date:", current_date)
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)

def convert_to_base64(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    images_b64 = []

    if ext == ".pdf":
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            images_b64.append(b64)
    elif ext in [".jpg", ".jpeg", ".png"]:
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            images_b64.append(b64)
    else:
        raise ValueError("Unsupported file format.")
    print("Image converted.............................................")
    return images_b64

# def extract_json(images_b64):
#     prompt_text = f"""You are an expert in document data extraction. Extract and translate into English only the following details in JSON format:

# JSON Format:
# {{
#   "docName": "...",              
#   "DocNumber": "...",            
#   "uploadedDate": "{current_date}",
#   "issuedCountry": "...",  
#   "IssuedPlace": "...",   
#   "issueDate": "dd-mm-yyyy",     
#   "expDate": "dd-mm-yyyy",       
#   "isNationalDoc": "No"     
# }}

# Extract the following details from the document:

# 1. "docName" refers to the official name of the document (e.g., "Seafarer's Identity Document"). Full name of the document, including the role or certification type if available (e.g., 'Certificate of Competency (Master)', 'Endorsement (GMDSS Radio Operator)')
# 2. "DocNumber" refers to the unique document number (e.g., "LM040496") or "Certificate Number" or "seamans book no" (if explicitly mentioned).
# 3. The "uploadedDate" field should NEVER be extracted from the document.
#    It must always be set to the current system date of extraction, which is "{current_date}".
# 4. "issuedCountry" refers to the country where the document was issued (e.g., "Spain").
# 5. "issueDate" refers to the document's issue date (ensure proper date format: dd-mm-yyyy).
# 6. "expDate" refers to the document's expiry date, if available.
# 7. "isNationalDoc" should default to "No".
# 8."IssuedPlace" refers to the place where the document was issued.
# 9. "IssuedPlace" refers to the place (e.g., city, port, country) where the document was issued. 
# Do not return organizational or institutional names (e.g., "Ministry of...", "Department of...", "Authority...").
# If only an institution or department is available (not a place), omit "IssuedPlace" or set it to null.

# Instructions:
# - If the document contains multiple sections, endorsements, or certificates, **extract each separately** and return them as individual JSON objects.
# - **Only extract valid endorsements and documents** with **valid document numbers**. 
#     - **DocNumber** should correspond to the number explicitly labeled as "Doc Number," "Certificate No.," "seamansbook no.," or similar labels (avoid "Serial No" or "ID" unless explicitly labeled as such).
#     - If there are multiple numbers such as "Serial No" or "ID" numbers, **ensure to capture only the "DocNumber"**.
# - **Filter out irrelevant sections** (such as revalidation entries) that do not contain a valid "DocNumber" or issue/expiry dates.
# - Return the extracted information as **an array of JSON objects** if the document contains multiple valid sections.
# - Handle multiple documents or sections within a single file carefully, ensuring no entries are missed or merged incorrectly.
# - If there are multiple document numbers or expiry dates mentioned, capture all of them accurately.
# - The "uploadedDate" must always be set to the current system date of extraction, which is "{current_date}".
# - Do NOT extract "uploadedDate" from any part of the document.
# - Ensure **dates are in "dd-mm-yyyy" format**, and the **"DocNumber"** should be extracted exactly as seen on the document without any formatting changes.
# - Do not include unnecessary or incorrect values. Return only the required fields in **English**.
# If no convincing document data is available (i.e., no valid docName,DocNumber,issuedCountry,IssuedPlace, issue date, or expiry date), return null.


# **Output Formatting:**
#     - **Return only a clean JSON object** with no extra text, explanations, code blocks, or Markdown formatting.
#     - **Do not use code block syntax (```json ... ```) around the response.**
#     - **Do not add extra indentation, explanations, or formatting.** Return the raw JSON directly.
#     - **The JSON output should start with `{' and end with '}` and should be valid JSON syntax.**

    
# Return the results as a **list of JSON objects**, one for each extracted document or endorsement section. Only include documents like endorsements or certificates with valid details.

# For each document, ensure:
# - The correct **DocNumber** is identified, and avoid confusing it with other numbers like "Serial No" or "ID" or number without any label unless clearly specified.
# - Handle each document as an individual entry.
# """

#     prompt = [
#         {
#             "type": "text",
#             "text": prompt_text
#         },
#         *[
#             {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/png;base64,{img}"
#                 }
#             } for img in images_b64
#         ]
#     ]

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     content = response.choices[0].message.content.strip()
#     if content.startswith("```json"):
#         content = content.replace("```json", "").replace("```", "").strip()

#     return content


def extract_json(images_b64):
    prompt_text = f"""You are an expert in document data extraction. Extract and translate into English only the following details in the following JSON format:

    JSON Format:
    {{
    "docName": "...",              
    "DocNumber": "...",            
    "uploadedDate": "{current_date}",
    "issuedCountry": "...",  
    "IssuedPlace": "...",   
    "issueDate": "dd-mm-yyyy",     
    "expDate": "dd-mm-yyyy",       
    "isNationalDoc": "No"     
    }}

    Instructions:

    Extract **all valid certificates, endorsements, medical documents, and training courses** from the document image(s). Return each as a separate JSON object.

    ### Field Rules:

    1. **"docName"** – Official name of the certificate or training (e.g., "Certificate of Competency (Master)", "Advanced Fire Fighting", etc.).
    2. **"DocNumber"** – Only use values explicitly labeled as “Certificate No.”, “Doc Number”, “Seaman’s Book No.”, etc. Do **not** use values labeled as "Serial No", "SL No", or "ID No".
    3. **"uploadedDate"** – Always use today’s system date: **{current_date}**
    4. **"issuedCountry"** – Country where the document was issued.
    5. **"IssuedPlace"** – City or port of issue. Do **not** use institutional names (e.g., “Ministry of…”). If only an institution is listed, set to **"null"** (as string).
    6. **"issueDate"** and **"expDate"** – Format all dates as **dd-mm-yyyy**.
    7. **"isNationalDoc"** – Always set to **"No"**.
    8. Use **"null"** (as string) for any missing fields (like DocNumber, IssuedPlace, etc.).

    ### Extraction Guidelines:

    - Extract **each valid section** of the document individually:
    - Certificates and Endorsements
    - Health Certificates
    - Training Courses
    - Seaman’s Book and Passport (if included)

    - **Only extract certificates or endorsements** that include a **valid document number** and clearly defined information.
    - If a document section contains **multiple document numbers or expiry dates**, extract them as **separate JSON objects**, one per entry.
    - **Ignore irrelevant sections** such as **revalidations**, administrative stamps, renewal logs, or entries lacking sufficient identifying details.
    - If **no valid document or course information is found**, return a single value: `null`.
    - Do **not extract duplicate or partial entries** without core details like "docName", "issuedCountry", or "issueDate".

    - If both certificates and courses appear in the same document, **extract all of them** without prioritizing one type over the other.
    - **Translate content into English** where necessary.
    - Use `"null"` (as string) for missing fields.

    ### Special Case: Course Lists or Tables

    - If training courses or modules are listed in **tables or summaries**, extract **each row as a separate JSON object**.
    - Set:
    - `"docName"` to the course name
    - `"DocNumber"`, `"issueDate"`, `"expDate"`, `"IssuedPlace"` to `"null"` (as string) if not available.
    - Do **not skip course entries**, even if embedded in other document blocks.

    ### Output Format:

    - Return a **flat JSON array** of objects — no markdown, no code blocks, no explanations.
    - Each object must contain **all fields listed** in the JSON Format block above.
    - Output must be **valid JSON**, with no extra formatting, commentary, or structure.

    Examples to include:
    - Certificate of Competency (Master)
    - Endorsement (GMDSS Radio Operator)
    - Seafarer's Medical Certificate
    - Seaman’s Book
    - Passport
    - Familiarization and Basic Safety Training
    - Advanced Fire Fighting
    - Medical First Aid
    - ARPA
    - Radar Simulator
    - Security Awareness Training
    """

    prompt = [
        {
            "type": "text",
            "text": prompt_text
        },
        *[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img}"
                }
            } for img in images_b64
        ]
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()

    return content


def postprocess_json(raw_json):
    if not isinstance(raw_json, str):
        return raw_json  # Nothing to do

    try:
        json_objects = raw_json.split('}\n{')
        if json_objects:
            json_objects[0] += '}'
            json_objects[-1] = '{' + json_objects[-1]
        results = [json.loads(obj) for obj in json_objects]
    except json.JSONDecodeError:
        return raw_json  # or return [] if you'd rather fail silently

    formatted = []
    for obj in results:
        known_fields = {
            "docName": obj.get("docName", "").strip(),
            "DocNumber": obj.get("DocNumber", "").strip(),
            "uploadedDate": obj.get("uploadedDate", "Not Available"),
            "issuedCountry": obj.get("issuedCountry", "").strip(),
            
             "IssuedPlace": obj.get("IssuedPlace", "").strip(),
            
            "issueDate": obj.get("issueDate", "").strip(),
            "expDate": obj.get("expDate", "Not Available").strip(),
            "isNationalDoc": obj.get("isNationalDoc", "No").strip(),
        }

        extra_fields = {
            k: v for k, v in obj.items()
            if k not in known_fields and k not in known_fields.keys()
        }

        if extra_fields:
            known_fields["metadata"] = extra_fields

        formatted.append(known_fields)

    return formatted


def process_document_to_json(file_path):
    images_b64 = convert_to_base64(file_path)
    raw_json = extract_json(images_b64)

    # If it's a string, try parsing
    if isinstance(raw_json, str):
        try:
            # Try to parse as proper JSON list
            raw_json = json.loads(raw_json)
        except json.JSONDecodeError:
            # If it's not valid JSON, try fallback string splitting logic
            return postprocess_json(raw_json)

    # If it's already a list, return it as-is
    if isinstance(raw_json, list):
        return raw_json

    # If it's something else, return safely
    return []

