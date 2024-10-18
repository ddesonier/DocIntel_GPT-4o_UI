import openai
import fitz  # PyMuPDF
import io
import os
from PIL import Image
import base64
import json
from dotenv import load_dotenv
from datetime import datetime
from azure.cosmos import CosmosClient
import azure.cosmos.exceptions as exceptions
import streamlit as st
import shutil
import time
# Import functions from generate_json_schema.py
from generate_json_schema import generate_schema, validate_json



load_dotenv()

api_key = os.getenv("AZURE_OPENAI_KEY")
# Set up the Open AI Client
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_key = api_key
model = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
cosmosapi = os.getenv("AZURE_COSMOS_API")
cosmosEndpoint = os.getenv("AZURE_COSMOS_ENDPOINT")

print("Endpoint: " + openai.api_base)
print("API Version: " + openai.api_version)
print("API Key: " + api_key)
print("Model: " + model)

@staticmethod
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def delete_files_in_directory(directory_path):
    """
    Deletes all files and subdirectories in the specified directory.

    Args:
        directory_path (str): The path to the directory to be cleaned.
    """
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed")
            #print(f'Failed to delete {file_path}. Reason: {e}')

def pdf_to_base64_images(pdf_path):
    print("PDF Path: " + pdf_path)
    #Handles PDFs with multiple pages
    pdf_document = fitz.open(pdf_path)
    base64_images = []
    temp_image_paths = []

    total_pages = len(pdf_document)

    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        temp_image_path = f"temp_page_{page_num}.png"
        img.save(temp_image_path, format="PNG")
        temp_image_paths.append(temp_image_path)
        base64_image = encode_image(temp_image_path)
        base64_images.append(base64_image)

    for temp_image_path in temp_image_paths:
        os.remove(temp_image_path)

    return base64_images

def extract_invoice_data(base64_image):
    system_prompt = f"""
    You are an OCR-like data extraction tool that extracts invoice data from images.
   
    1. Please extract the data in this invoice, grouping data according to theme/sub groups, and then output into JSON.

    2. Please keep the keys and values of the JSON in the original language. 

    3. The type of data you might encounter in the invoice includes but is not limited to: company information, customer information, invoice information,
    unit price, invoice date, part numbers, taxes, each line item may rows embedded showing qurntity and unit proces based on quantity, 
    and total invoice total etc.  For each row that has embedded rows, keep them in the same row. 

    4. If the page contains no charge data, please output an empty JSON object and don't make up any data.

    5. If there are blank data fields in the invoice, please include them as "null" values in the JSON object.
    
    6. If there are tables in the invoice, capture all of the rows and columns in the JSON object. 
    Even if a column is blank, include it as a key in the JSON object with a null value.
    
    7. If a row is blank denote missing fields with "null" values. 
    
    8. Don't interpolate or make up data.

    9. Please maintain the table structure of the items, i.e. capture all of the rows and columns in the JSON object.

    """
    
    response = openai.chat.completions.create(
        #model="gpt-4o",
        model = model,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "extract the data in this invoice and output into JSON "},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    print("Extract Invoice Data Call Info:")
    #print(response.choices[0].message.content)
    print(response.model)
    print(response.usage)
    with st.sidebar.container():
        st.sidebar.title("Model Completion Usage to Extract Invoice Data")
        st.sidebar.write(f"Usage: {response.usage}")

    print("JSON: " + response.choices[0].message.content)
    return response.choices[0].message.content




def extract_from_multiple_pages(base64_images, original_filename, output_directory):
    entire_invoice = []

    for base64_image in base64_images:
        invoice_json = extract_invoice_data(base64_image)
        invoice_data = json.loads(invoice_json)
        entire_invoice.append(invoice_data)

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    original_filename = original_filename.lower()

    # Construct the output file path
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    output_filename = os.path.join(output_directory, original_filename.replace('.pdf', '_extracted_' + timestamp + '.json'))

    # Save the entire_invoice list as a JSON file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(entire_invoice, f, ensure_ascii=False, indent=4)
    print("Extract From Multiple Pages Call Info:")
    print("PDF file: " + original_filename + " has been extracted to file: " + output_filename)
    with col1:
        st.title("Extracted JSON Content")
        st.json(entire_invoice)
    return output_filename


def main_extract(read_path, write_path):
    for filename in os.listdir(read_path):
        file_path = os.path.join(read_path, filename)
        if os.path.isfile(file_path):
            base64_images = pdf_to_base64_images(file_path)
            extract_from_multiple_pages(base64_images, filename, write_path)




def transform_invoice_data(json_raw, json_schema):
    system_prompt = f"""
    You are a data transformation tool that takes in JSON data and a reference JSON schema, and outputs JSON data according to the schema.
    Not all of the data in the input JSON will fit the schema, so you may need to omit some data or add null values to the output JSON.
    Translate all data into English if not already in English. 
    Ensure values are formatted as specified in the schema (e.g. dates as YYYY-MM-DD).
    Here is the schema:
    {json_schema}
    """
    userprompt = f"""
    Transform the following raw JSON data according to the provided schema. Ensure all data is in English and formatted as specified by values in the schema. 
    Keep JSON strucutre the same for purposes of inserting into a COMOS DB. 
    Here is the raw JSON: 
    {json_raw}
    """

    response = openai.chat.completions.create(
        model = model,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": userprompt
            }
        ],
        temperature=0.0,
        top_p=0.0,
        max_tokens=16000,
    )
    print("Transform Invoice Data Call Info:")
    print(response.model)
    print(response.usage)
    json_content = json.loads(response.choices[0].message.content)
    with st.sidebar.container():
        st.sidebar.title("Model Completion Usage to Transform Invoice")
        st.sidebar.write(f"Usage: {response.usage}")
    # st.sidebar.write(f"Total Tokens: {response.usage['total_tokens']}")
    # st.sidebar.write(f"Prompt Tokens: {response.usage['prompt_tokens']}")
    # st.sidebar.write(f"Completion Tokens: {response.usage['completion_tokens']}")
    return json_content

def main_transform(extracted_invoice_json_path, myjson_schema, save_path, company):
    # Load the JSON schema
    with open(myjson_schema, 'r', encoding='utf-8') as f:
        json_schema = json.load(f)

    # Ensure the save directory exists
    os.makedirs(save_path, exist_ok=True)

    # Process each JSON file in the extracted invoices directory
    for filename in os.listdir(extracted_invoice_json_path):
        if filename.endswith(".json"):
            file_path = os.path.join(extracted_invoice_json_path, filename)
            print("Main_Transform")
            print("filename: " + filename)
            # Load the extracted JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_raw = json.load(f)
            # Transform the JSON data
            transformed_json = transform_invoice_data(json_raw, json_schema)
            transformed_filename = filename.replace('extracted', 'transformed')
            transformed_file_path = os.path.join(save_path, transformed_filename)
            with open(transformed_file_path, 'w', encoding='utf-8') as f:
                json.dump(transformed_json, f, ensure_ascii=False, indent=2)
            with col2:
                st.title("Transformed JSON Content")
                st.json(transformed_json)
                # Ensure the output directory exists



            print("Main_Transform")
            print("JSON Extraction file: " + filename + " has been transformed to file: " + transformed_filename)
            # cosmodDB_upsert_item(transformed_file_path, company)


def main_create_json_schema(extracted_invoice_json_path, json_schema_file):

    for filename in os.listdir(extracted_invoice_json_path):
        file_path = os.path.join(extracted_invoice_json_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                json_data = json.load(file)
            json_schema = generate_schema(json_data)
            #json_schema = generate_schema_from_json(json_data)

            with open(json_schema_file, 'w', encoding='utf-8') as f:
                json.dump(json_schema, f, ensure_ascii=False, indent=4)
            print("Main_Create_JSON_Schema")
            print(json_schema_file)

def generate_schema_from_json(data, key=None):
    """
    Recursively generate a JSON schema from the given JSON data.
    """
    if isinstance(data, dict):
        properties = {k: generate_schema_from_json(v, k) for k, v in data.items()}
        return {"type": "object", "properties": properties}
    elif isinstance(data, list):
        if data:  # Non-empty list
            return {"type": "array", "items": generate_schema_from_json(data[0])}
        else:  # Empty list
            return {"type": "array"}
    elif isinstance(data, str):
        # Special handling for date-like strings, adjust the pattern as needed
        if key and key.lower().replace(" ", "_") == "date_quoted":
            return {"type": "string", "pattern": "^[A-Z]{3} [0-9]{2}, [0-9]{4}$"}
        return {"type": "string"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    else:
        return {}

def progress_bar(text, size):
    st.write(text)
    print("size: ", size)
    my_bar = st.progress(0)
    gap = 100 / size
    for percent_complete in range(size):
        time.sleep(gap)
        print("percent_complete: ", percent_complete)
        print("gap: ", gap)
        step = max(percent_complete + gap, 100)
        print("step: ", step)
        if step <= 100:
            my_bar.progress(step)
    


def cosmodDB_upsert_item(jsondata, database):
# Read the JSON file
    # Initialize the Cosmos client
    container = database # For converneince, we are passing the container name as the database name
    jsondata = jsondata.replace("json{" , "{")
    client = CosmosClient(cosmosEndpoint, cosmosapi)

    # Read the JSON file
    with open(jsondata, 'r') as file:
        jsondata = json.load(file)

    # Get a reference to the database
    database = client.get_database_client(database)

    # Get a reference to the container
    container = database.get_container_client(container)

    container.create_item(body=jsondata,
        enable_automatic_id_generation=True)


st.title("Invoice Data Extraction")

# Select company
companys = ["arrow", "euc", "abc", "max"]
company = st.sidebar.selectbox("Select Company", companys)

uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
st.sidebar.title("Uploaded PDF File")


if uploaded_file is not None:
    
    # Save the uploaded file to a local directory called 'temp'
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        print("Temp file path: " + temp_file_path)
    #progress_bar("Uploading and scanning PDF file...", os.path.getsize(temp_file_path))
    # Display the uploaded PDF file
    #st.sidebar.title("Uploaded PDF")
    st.sidebar.write(uploaded_file.name)
    
    with open("temp_uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with open("temp_uploaded_file.pdf", "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        

    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    if st.button("Begin Processing"):
        base64_images = pdf_to_base64_images(temp_file_path)
        print("Base64 Images Count: " + str(len(base64_images)))
        # extracted_data = []
        # for image in base64_images:
        #     extracted_data.append(extract_invoice_data(image))
        # extracted_data = extract_invoice_data(base64_pdf)
        
        # # Display the extracted JSON content on the right
        # st.title("Extracted JSON Content")
        # st.json(extracted_data)
        
        os.remove("temp_uploaded_file.pdf")

        # Display extracted and transformed JSON side by side with custom width
        col1, col2 = st.columns(2)

        print("Processing company: " + company)
        #read_path = "./data/" + company + "invoices"
        read_path = "./temp"
        write_path = "./data/" + company + "invoices" + "/" + "extracted_invoice_json"
        extracted_invoice_json_path = write_path
        json_schema_path = "./data/" + company + "invoices" + "/" + "schema"
        save_path = "./data/" + company + "invoices" + "/" + "transformed_invoice_json"
        json_schema = json_schema_path + "/" + "json_schema_" + company + "_extracted.json"

        print("Read Path: " + read_path)
        print("Write Path: " + write_path)
        print("Extracted Invoice JSON Path: " + extracted_invoice_json_path)
        print("JSON Schema Path: " + json_schema_path)
        print("Save Path: " + save_path)
        print("JSON Schema: " + json_schema)

        main_extract(read_path, extracted_invoice_json_path)

        if os.path.exists(json_schema):
            print("Schema file already exists, using: " + json_schema)
        else:
            print("Schema file does not exist, creating: " + json_schema)
            main_create_json_schema(extracted_invoice_json_path, json_schema)

        main_transform(extracted_invoice_json_path, json_schema, save_path, company)

        # Delete files in the extracted_invoice_json folder after processing
        #delete_files_in_directory(extracted_invoice_json_path)
        #delete_files_in_directory(save_path)
        delete_files_in_directory("./temp")

