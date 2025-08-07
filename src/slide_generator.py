import logging
from typing import Dict, List, Union
import pandas as pd
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Template library for industry-specific designs
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

class SlideGenerator:
    """
    A standalone module to generate slide data for boardroom presentations.
    Creates JSON structure with slides and Chart.js visualizations based on insights.
    Designed for integration with a FastAPI backend and Reveal.js frontend.
    """

    @staticmethod
    def generate_visualizations(insights: Dict, df: pd.DataFrame) -> List[Dict]:
        """
        Generate Chart.js configurations for visualizations.

        Args:
            insights (Dict): Insights from InsightsGenerator (metrics, summary, recommendations)
            df (pd.DataFrame): Original DataFrame for data access

        Returns:
            List[Dict]: Chart.js configurations for slides
        """
        try:
            logger.info("Generating visualizations")
            charts = []
            colors = ["#36A2EB", "#FF6384", "#FFCE56"]

            # Line Chart: Revenue Trends by Region
            if "revenue" in insights and "error" not in insights["revenue"]:
                revenue_data = insights["revenue"]["by_region"]
                regions = [r["Region"] for r in revenue_data]
                q2_revenues = [r["Revenue"] for r in revenue_data]
                q1_revenues = [
                    df[df["Quarter"] == "Q1 2025"][df["Region"] == r["Region"]]["Revenue"].iloc[0]
                    for r in revenue_data
                ]

                charts.append({
                    "type": "line",
                    "data": {
                        "labels": ["Q1 2025", "Q2 2025"],
                        "datasets": [
                            {
                                "label": region,
                                "data": [q1_revenues[i], q2_revenues[i]],
                                "borderColor": colors[i % len(colors)],
                                "fill": False
                            }
                            for i, region in enumerate(regions)
                        ]
                    },
                    "options": {
                        "plugins": {"title": {"display": True, "text": "Revenue Trends by Region"}}
                    }
                })

            # Bar Chart: Churn and NPS Comparison
            if "customer_metrics" in insights and "error" not in insights["customer_metrics"]:
                charts.append({
                    "type": "bar",
                    "data": {
                        "labels": ["Q1 2025", "Q2 2025"],
                        "datasets": [
                            {
                                "label": "Churn Rate (%)",
                                "data": [
                                    insights["customer_metrics"]["churn_q2"] + insights["customer_metrics"]["churn_change"],
                                    insights["customer_metrics"]["churn_q2"]
                                ],
                                "backgroundColor": "#FF6384"
                            },
                            {
                                "label": "NPS",
                                "data": [
                                    insights["customer_metrics"]["nps_q2"] - insights["customer_metrics"]["nps_change"],
                                    insights["customer_metrics"]["nps_q2"]
                                ],
                                "backgroundColor": "#36A2EB"
                            }
                        ]
                    },
                    "options": {
                        "plugins": {"title": {"display": True, "text": "Churn Rate and NPS Comparison"}}
                    }
                })

            logger.info(f"Generated {len(charts)} visualizations")
            return charts
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            raise Exception(f"Error generating visualizations: {str(e)}")

    @staticmethod
    def generate_slide_data(insights: Dict, charts: List[Dict], template_id: str = "saas") -> Dict:
        """
        Generate JSON structure for slides based on insights and visualizations.

        Args:
            insights (Dict): Insights from InsightsGenerator (metrics, summary, recommendations)
            charts (List[Dict]): Chart.js configurations
            template_id (str): Template ID (e.g., "saas", "finance", "retail")

        Returns:
            Dict: Slide data with template metadata
        """
        try:
            logger.info(f"Generating slide data with template: {template_id}")
            template = TEMPLATES.get(template_id, TEMPLATES["saas"])

            slides = [
                {
                    "title": "Q2 2025 Board Meeting",
                    "subtitle": "Financial & Customer Insights",
                    "type": "title"
                },
                {
                    "title": "Executive Summary",
                    "content": insights.get("summary", ["No summary available"]),
                    "type": "text"
                },
                {
                    "title": "Strategic Recommendations",
                    "content": insights.get("recommendations", ["No recommendations available"]),
                    "type": "text"
                }
            ]

            # Add chart slides
            if charts:
                slides.append({
                    "title": "Revenue Trends",
                    "chart": charts[0] if len(charts) > 0 else None,
                    "type": "chart"
                })
                if len(charts) > 1:
                    slides.append({
                        "title": "Customer Metrics",
                        "chart": charts[1],
                        "type": "chart"
                    })

            slide_data = {
                "slides": slides,
                "template": template
            }

            logger.info(f"Generated {len(slides)} slides")
            return slide_data
        except Exception as e:
            logger.error(f"Error generating slide data: {str(e)}")
            raise Exception(f"Error generating slide data: {str(e)}")

    @staticmethod
    def generate_slides(parsed_data: Dict, insights: Dict, template_id: str = "saas") -> Dict:
        """
        Generate complete slide data from parsed data and insights.

        Args:
            parsed_data (Dict): Output from FileParser.parse_files
            insights (Dict): Output from InsightsGenerator.generate_insights
            template_id (str): Template ID for styling

        Returns:
            Dict: Slide data with visualizations and template
        """
        try:
            logger.info("Generating complete slide data")
            df = parsed_data.get("spreadsheets", [{}])[0].get("data") if parsed_data.get("spreadsheets") else None
            
            if df is None or not isinstance(df, pd.DataFrame):
                logger.warning("No valid spreadsheet data provided for visualizations")
                charts = []
            else:
                charts = SlideGenerator.generate_visualizations(insights["metrics"], df)

            slide_data = SlideGenerator.generate_slide_data(insights, charts, template_id)
            logger.info("Successfully generated slide data")
            return slide_data
        except Exception as e:
            logger.error(f"Error generating slides: {str(e)}")
            raise Exception(f"Error generating slides: {str(e)}")

if __name__ == "__main__":
    from file_parser import FileParser
    from insights_generator import InsightsGenerator
    import asyncio

    async def test_slide_generator():
        # Parse sample data
        df = FileParser.parse_sample_data()
        parsed_data = {"spreadsheets": [{"filename": "q2_financials.csv", "data": df}], "pdfs": []}
        
        # Generate insights
        insights = InsightsGenerator.generate_insights(parsed_data)
        
        # Generate slides
        slide_data = SlideGenerator.generate_slides(parsed_data, insights, template_id="saas")
        print("Generated Slide Data:")
        print(json.dumps(slide_data, indent=2, default=str))

    asyncio.run(test_slide_generator())