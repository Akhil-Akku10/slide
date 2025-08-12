import pandas as pd
import PyPDF2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import io
import logging
from typing import List, Dict
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Slide Generator Backend")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Template library
TEMPLATES = {
    "saas": {
        "font": "Roboto",
        "color_scheme": {"primary": "#0052cc", "background": "#ffffff", "accent": "#36A2EB"},
        "title_font_size": "2.5em",
        "body_font_size": "1.2em"
    },
    "finance": {
        "font": "Lato",
        "color_scheme": {"primary": "#1a3c34", "background": "#f5f6f5", "accent": "#2e7d32"},
        "title_font_size": "2.5em",
        "body_font_size": "1.2em"
    },
    "retail": {
        "font": "Open Sans",
        "color_scheme": {"primary": "#d81b60", "background": "#ffffff", "accent": "#f06292"},
        "title_font_size": "2.5em",
        "body_font_size": "1.2em"
    }
}

# Pydantic model for template selection
class TemplateSelection(BaseModel):
    template_id: str

# Helper: Parse CSV/Excel file
def parse_spreadsheet(file: UploadFile) -> pd.DataFrame:
    try:
        logger.info(f"Parsing spreadsheet: {file.filename}")
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file.file)
        else:
            raise ValueError("Unsupported file format")
        return df
    except Exception as e:
        logger.error(f"Error parsing spreadsheet {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing spreadsheet: {str(e)}")

# Helper: Parse PDF file
def parse_pdf(file: UploadFile) -> Dict:
    try:
        logger.info(f"Parsing PDF: {file.filename}")
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        # Simulate table extraction (mocked metrics for demo)
        mock_metrics = {
            "customer_feedback": "NPS improved to 62",
            "sentiment": "Positive feedback on product features"
        }
        return {"text": text, "metrics": mock_metrics}
    except Exception as e:
        logger.error(f"Error parsing PDF {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")

# Helper: Extract insights from DataFrame
def extract_insights(df: pd.DataFrame) -> Dict:
    try:
        logger.info("Extracting insights from DataFrame")
        insights = {}
        
        # Revenue Analysis
        q2_revenue = df[df["Quarter"] == "Q2 2025"]["Revenue"].sum()
        q1_revenue = df[df["Quarter"] == "Q1 2025"]["Revenue"].sum()
        revenue_growth = ((q2_revenue - q1_revenue) / q1_revenue) * 100 if q1_revenue > 0 else 0
        insights["revenue"] = {
            "total_q2": q2_revenue,
            "growth_qoq": round(revenue_growth, 1),
            "by_region": df[df["Quarter"] == "Q2 2025"][["Region", "Revenue"]].to_dict(orient="records")
        }
        
        # Churn and NPS
        q2_churn = df[df["Quarter"] == "Q2 2025"]["Churn_Rate"].iloc[0]
        q1_churn = df[df["Quarter"] == "Q1 2025"]["Churn_Rate"].iloc[0]
        q2_nps = df[df["Quarter"] == "Q2 2025"]["NPS"].iloc[0]
        insights["customer_metrics"] = {
            "churn_q2": q2_churn,
            "churn_change": q1_churn - q2_churn,
            "nps_q2": q2_nps
        }
        
        # Costs
        q2_cac = df[df["Quarter"] == "Q2 2025"]["CAC"].iloc[0]
        q1_cac = df[df["Quarter"] == "Q1 2025"]["CAC"].iloc[0]
        cac_reduction = ((q1_cac - q2_cac) / q1_cac) * 100 if q1_cac > 0 else 0
        insights["costs"] = {
            "cac_q2": q2_cac,
            "cac_reduction": round(cac_reduction, 1),
            "marketing_spend": df[df["Quarter"] == "Q2 2025"]["Marketing_Spend"].iloc[0]
        }
        
        return insights
    except Exception as e:
        logger.error(f"Error extracting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting insights: {str(e)}")

# Helper: Generate Chart.js visualizations
def generate_visualizations(insights: Dict) -> List[Dict]:
    try:
        logger.info("Generating visualizations")
        charts = []
        colors = ["#36A2EB", "#FF6384", "#FFCE56"]
        
        # Line Chart: Revenue Trends by Region
        revenue_data = insights["revenue"]["by_region"]
        regions = [r["Region"] for r in revenue_data]
        q2_revenues = [r["Revenue"] for r in revenue_data]
        q1_revenues = [df[df["Quarter"] == "Q1 2025"][df["Region"] == r["Region"]]["Revenue"].iloc[0] for r in revenue_data]
        
        charts.append({
            "type": "line",
            "data": {
                "labels": ["Q1 2025", "Q2 2025"],
                "datasets": [
                    {"label": region, "data": [q1_revenues[i], q2_revenues[i]], "borderColor": colors[i], "fill": False}
                    for i, region in enumerate(regions)
                ]
            },
            "options": {
                "plugins": {"title": {"display": True, "text": "Revenue Trends by Region"}}
            }
        })
        
        # Bar Chart: Churn and NPS Comparison
        charts.append({
            "type": "bar",
            "data": {
                "labels": ["Q1 2025", "Q2 2025"],
                "datasets": [
                    {"label": "Churn Rate (%)", "data": [insights["customer_metrics"]["churn_q2"] + insights["customer_metrics"]["churn_change"], insights["customer_metrics"]["churn_q2"]], "backgroundColor": "#FF6384"},
                    {"label": "NPS", "data": [55, insights["customer_metrics"]["nps_q2"]], "backgroundColor": "#36A2EB"}
                ]
            },
            "options": {
                "plugins": {"title": {"display": True, "text": "Churn Rate and NPS Comparison"}}
            }
        })
        
        return charts
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating visualizations: {str(e)}")

# Helper: Generate slide data
def generate_slide_data(insights: Dict, charts: List[Dict], template_id: str) -> Dict:
    try:
        logger.info(f"Generating slide data with template: {template_id}")
        template = TEMPLATES.get(template_id, TEMPLATES["saas"])
        
        # Mock AI-generated summary (replace with GPT integration in production)
        summary = [
            f"Revenue: ${insights['revenue']['total_q2'] / 1e6:.1f}M, up {insights['revenue']['growth_qoq']}% QoQ",
            f"Churn: Stabilized at {insights['customer_metrics']['churn_q2']}%, down {insights['customer_metrics']['churn_change']}%",
            f"CAC: Reduced by {insights['costs']['cac_reduction']}% to ${insights['costs']['cac_q2']}",
            "Recommendation: Increase APAC investment, launch US SMB retention campaign."
        ]
        
        if "pdf_feedback" in insights:
            summary.append(f"Customer Feedback: {insights['pdf_feedback']['metrics']['customer_feedback']}")
        
        return {
            "slides": [
                {
                    "title": "Q2 2025 Board Meeting",
                    "subtitle": "Financial & Customer Insights",
                    "type": "title"
                },
                {
                    "title": "Executive Summary",
                    "content": summary,
                    "type": "text"
                },
                {
                    "title": "Revenue Trends",
                    "chart": charts[0],
                    "type": "chart"
                },
                {
                    "title": "Customer Metrics",
                    "chart": charts[1],
                    "type": "chart"
                }
            ],
            "template": template
        }
    except Exception as e:
        logger.error(f"Error generating slide data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating slide data: {str(e)}")

# API Endpoint: List available templates
@app.get("/templates")
async def get_templates():
    return JSONResponse(content={"templates": list(TEMPLATES.keys())})

# API Endpoint: Upload and process filesfrom file_parser import FileParser
from Insight_generator import InsightsGenerator

# Update the upload endpoint
from file_parser import FileParser
from Insight_generator import InsightsGenerator
from slide_generator import SlideGenerator

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), template_id: str = "saas"):
    try:
        logger.info(f"Processing {len(files)} files with template: {template_id}")
        # Parse files
        parsed_data = await FileParser.parse_files(files)
        
        # Generate insights
        insights = InsightsGenerator.generate_insights(parsed_data)
        
        # Generate slides
        slide_data = SlideGenerator.generate_slides(parsed_data, insights, template_id)
        
        return JSONResponse(content=slide_data)
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.get("/test")
async def test_endpoint(template_id: str = "saas"):
    try:
        logger.info(f"Running test endpoint with template: {template_id}")
        parsed_data = {"spreadsheets": [{"filename": "q2_financials.csv", "data": FileParser.parse_sample_data()}], "pdfs": []}
        insights = InsightsGenerator.generate_insights(parsed_data)
        slide_data = SlideGenerator.generate_slides(parsed_data, insights, template_id)
        return JSONResponse(content=slide_data)
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in test endpoint: {str(e)}")
# API Endpoint: Test with sample data
@app.get("/test")
async def test_endpoint(template_id: str = "saas"):
    try:
        logger.info(f"Running test endpoint with template: {template_id}")
        with open("q2_financials.csv", "w") as f:
            f.write(SAMPLE_DATA)
        global df
        df = pd.read_csv("q2_financials.csv")
        insights = extract_insights(df)
        charts = generate_visualizations(insights)
        slide_data = generate_slide_data(insights, charts, template_id)
        return JSONResponse(content=slide_data)
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in test endpoint: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)