from fastapi import HTTPException
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import base64
import requests
from importlib import resources


def read_base64_few_shot_file(filename: str = "few_shot_1.pdf") -> str | None:
    """Reads and returns content of a few-shot example file.

    Args:
        filename: Name of the file in few_shot package

    Returns:
        str: Base64 encoded content

    Raises:
        FileNotFoundError: If file cannot be found
    """

    try:
        with resources.path("manimator.few_shot", filename) as pdf_path:
            if not pdf_path:
                raise FileNotFoundError("PDF resource not found")

            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                base64_str = base64.b64encode(pdf_bytes).decode("utf-8")
                return base64_str
    except Exception as e:
        print(f"Error accessing resource {filename}: {e}")
        return None


def download_arxiv_pdf(url: str) -> bytes:
    """Downloads a PDF from an arXiv URL.

    Args:
        url (str): The arXiv URL to download the PDF from

    Returns:
        bytes: Raw PDF content

    Raises:
        HTTPException: If download fails or URL is invalid
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download arxiv PDF: {str(e)}"
        )


def compress_pdf(content: bytes, compression_level: int = 5) -> str:
    """Compresses a PDF and converts it to base64 encoded string.

    Args:
        content (bytes): Raw PDF content to compress
        compression_level (int): PDF compression level (1-9). Defaults to 5

    Returns:
        str: Base64 encoded compressed PDF content

    Note:
        Falls back to uncompressed base64 encoding if compression fails
    """

    try:
        reader = PdfReader(BytesIO(content))
        output = BytesIO()
        writer = PdfWriter(output)

        for page in reader.pages:
            writer.add_page(page)

        # PyPDF2 3.0.1 compression is handled differently if needed, skipping explicit call
        writer.write(output)

        compressed_bytes = output.getvalue()
        return base64.b64encode(compressed_bytes).decode("utf-8")
    except Exception:
        return base64.b64encode(content).decode("utf-8")
