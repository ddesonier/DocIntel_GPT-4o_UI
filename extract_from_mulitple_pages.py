import os
import argparse
import fitz  # PyMuPDF
from PIL import Image
import io

def pdf_to_jpg(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    output_directory = os.path.dirname(pdf_path)
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    # Convert each page to an image and save as JPG
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        output_filename = os.path.join(output_directory, f"{base_filename}_page_{page_num + 1}.jpg")
        img.save(output_filename, format="JPEG")
        print(f"Page {page_num + 1} saved as {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Convert PDF pages to JPG images.")
    parser.add_argument("pdf_file", help="Path to the input PDF file")
    args = parser.parse_args()

    pdf_to_jpg(args.pdf_file)
    print(args.pdf_file)

if __name__ == "__main__":
    main()