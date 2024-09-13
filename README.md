# DocIntel_GPT-4o_UI# Invoice Data Extraction

This project is a Streamlit application for extracting and transforming invoice data from PDF files. The application uses Azure OpenAI for OCR-like data extraction and JSON transformation according to a provided schema.

## Features

- Upload PDF files containing invoices.
- Extract invoice data from PDF images.
- Transform extracted data according to a JSON schema.
- Display extracted and transformed JSON data side by side.
- Display model completion usage statistics.

## Setup

### Prerequisites

- Python 3.7 or higher
- Streamlit
- Azure OpenAI API key
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/ddesonier/DocIntel_GPT-4o_UI.git
    cd DocIntel_GPT-4o_UI
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory of the project and add the following variables:

    ```env
    AZURE_OPENAI_KEY=your_azure_openai_key
    AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
    AZ_OPENAI_API_VERSION=your_azure_openai_api_version
    AZURE_OPENAI_CHATGPT_DEPLOYMENT=your_azure_openai_chatgpt_deployment
    ```

## Usage

1. Run the Streamlit application:

    ```sh
    streamlit run app.py
    ```

2. Open your web browser and go to `http://localhost:8501`.

3. Select a company from the dropdown menu.

4. Upload a PDF file containing invoices.

5. Click the "Begin Processing" button to extract and transform the invoice data.

6. View the extracted and transformed JSON data side by side.

## Project Structure

- `app.py`: Main application file.
- `requirements.txt`: List of required Python packages.
- `README.md`: Project documentation.
- `.env`: Environment variables (not included in the repository).

## Additional Information

- The application uses Azure OpenAI for OCR-like data extraction and JSON transformation.
- The extracted and transformed JSON data is displayed side by side for easy comparison.
- Model completion usage statistics are displayed in the left panel.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
