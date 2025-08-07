import pandas as pd
import PyPDF2
from fastapi import UploadFile, HTTPException
import io
import logging
from typing import Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for testing
SAMPLE_DATA = """
Quarter,Region,Revenue,Churn_Rate,NPS,New_Customers,CAC,Operating_Expenses,Marketing_Spend
Q1 2025,APAC,4400000,7.4,55,1100,492,7730000,1650000
Q1 2025,North America,4570000,7.4,55,1100,492,7730000,1650000
Q1 2025,Europe,2380000,7.4,55,1100,492,7730000,1650000
Q2 2025,APAC,5200000,5.1,62,1200,450,8200000,1500000
Q2 2025,North America,4800000,5.1,62,1200,450,8200000,1500000
Q2 2025,Europe,2500000,5.1,62,1200,450,8200000,1500000
"""

class FileParser:
    """
    A standalone module to parse Excel, CSV, and PDF files into structured data.
    Returns DataFrames for spreadsheets and dictionaries for PDFs.
    Designed for integration with a FastAPI backend for slide generation.
    """

    @staticmethod
    async def parse_spreadsheet(file: UploadFile) -> pd.DataFrame:
        """
        Parse CSV or Excel files into a Pandas DataFrame.

        Args:
            file (UploadFile): Uploaded file (CSV, .xlsx, .xls)

        Returns:
            pd.DataFrame: Parsed data

        Raises:
            HTTPException: If file format is unsupported or parsing fails
        """
        try:
            logger.info(f"Parsing spreadsheet: {file.filename}")
            file_content = await file.read()
            file_io = io.BytesIO(file_content)

            if file.filename.endswith(".csv"):
                df = pd.read_csv(file_io)
            elif file.filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_io)
            else:
                raise ValueError("Unsupported file format. Use CSV, .xlsx, or .xls")

            # Validate DataFrame
            if df.empty:
                raise ValueError("Empty spreadsheet")

            logger.info(f"Successfully parsed spreadsheet: {file.filename}, shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error parsing spreadsheet {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error parsing spreadsheet: {str(e)}")

    @staticmethod
    async def parse_pdf(file: UploadFile) -> Dict[str, Union[str, Dict]]:
        """
        Parse PDF files to extract text and simulate table metrics.

        Args:
            file (UploadFile): Uploaded PDF file

        Returns:
            Dict: Contains extracted text and mocked metrics (e.g., customer feedback)

        Raises:
            HTTPException: If parsing fails
        """
        try:
            logger.info(f"Parsing PDF: {file.filename}")
            file_content = await file.read()
            file_io = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(file_io)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

            # Simulate table extraction (mocked for demo; use tabula-py for real tables)
            mock_metrics = {
                "customer_feedback": "NPS improved to 62",
                "sentiment": "Positive feedback on product features"
            }

            logger.info(f"Successfully parsed PDF: {file.filename}, text length: {len(text)}")
            return {"text": text, "metrics": mock_metrics}
        except Exception as e:
            logger.error(f"Error parsing PDF {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")

    @staticmethod
    def parse_sample_data() -> pd.DataFrame:
        """
        Parse sample CSV data for testing purposes.

        Returns:
            pd.DataFrame: Parsed sample data
        """
        try:
            logger.info("Parsing sample data")
            with open("q2_financials.csv", "w") as f:
                f.write(SAMPLE_DATA)
            df = pd.read_csv("q2_financials.csv")
            logger.info(f"Successfully parsed sample data, shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error parsing sample data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error parsing sample data: {str(e)}")

    @staticmethod
    async def parse_files(files: List[UploadFile]) -> Dict[str, Union[List[Dict], List[Dict]]]:
        """
        Parse multiple files (CSV, Excel, PDF) and return structured data.

        Args:
            files (List[UploadFile]): List of uploaded files

        Returns:
            Dict: Contains DataFrames (spreadsheets) and dictionaries (PDFs)

        Raises:
            HTTPException: If any file parsing fails
        """
        result = {"spreadsheets": [], "pdfs": []}
        try:
            for file in files:
                if file.filename.endswith((".csv", ".xlsx", ".xls")):
                    df = await FileParser.parse_spreadsheet(file)
                    result["spreadsheets"].append({"filename": file.filename, "data": df})
                elif file.filename.endswith(".pdf"):
                    pdf_data = await FileParser.parse_pdf(file)
                    result["pdfs"].append({"filename": file.filename, "data": pdf_data})
                else:
                    logger.warning(f"Skipping unsupported file: {file.filename}")
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
            logger.info(f"Parsed {len(result['spreadsheets'])} spreadsheets and {len(result['pdfs'])} PDFs")
            return result
        except Exception as e:
            logger.error(f"Error parsing files: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error parsing files: {str(e)}")

if __name__ == "__main__":
    import asyncio

    async def test_parser():
        # Test sample data
        df = FileParser.parse_sample_data()
        print("Sample Data DataFrame:")
        print(df.head())

    asyncio.run(test_parser())