import pandas as pd
from typing import Dict, List, Union
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightsGenerator:
    """
    A standalone module to generate GPT-like insights from parsed business data.
    Analyzes spreadsheets and PDF metrics to produce executive summaries and recommendations.
    Designed for integration with a FastAPI backend for slide generation.
    """

    @staticmethod
    def analyze_spreadsheet(df: pd.DataFrame) -> Dict[str, Union[float, List, Dict]]:
        """
        Analyze spreadsheet data to extract key metrics and trends.

        Args:
            df (pd.DataFrame): Parsed spreadsheet data (e.g., revenue, churn, NPS)

        Returns:
            Dict: Metrics, trends, and anomalies
        """
        try:
            logger.info("Analyzing spreadsheet data")
            insights = {}

            # Revenue Analysis
            quarters = df["Quarter"].unique()
            if len(quarters) >= 2:
                q2_revenue = df[df["Quarter"] == quarters[-1]]["Revenue"].sum()
                q1_revenue = df[df["Quarter"] == quarters[-2]]["Revenue"].sum()
                revenue_growth = ((q2_revenue - q1_revenue) / q1_revenue) * 100 if q1_revenue > 0 else 0
                top_region = df[df["Quarter"] == quarters[-1]].groupby("Region")["Revenue"].sum().idxmax()
                insights["revenue"] = {
                    "total_q2": q2_revenue,
                    "growth_qoq": round(revenue_growth, 1),
                    "top_region": top_region,
                    "by_region": df[df["Quarter"] == quarters[-1]][["Region", "Revenue"]].to_dict(orient="records")
                }
            else:
                insights["revenue"] = {"error": "Insufficient quarters for revenue analysis"}

            # Customer Metrics
            if "Churn_Rate" in df.columns and "NPS" in df.columns:
                q2_churn = df[df["Quarter"] == quarters[-1]]["Churn_Rate"].iloc[0]
                q1_churn = df[df["Quarter"] == quarters[-2]]["Churn_Rate"].iloc[0]
                q2_nps = df[df["Quarter"] == quarters[-1]]["NPS"].iloc[0]
                insights["customer_metrics"] = {
                    "churn_q2": q2_churn,
                    "churn_change": q1_churn - q2_churn,
                    "nps_q2": q2_nps,
                    "nps_change": q2_nps - df[df["Quarter"] == quarters[-2]]["NPS"].iloc[0]
                }
            else:
                insights["customer_metrics"] = {"error": "Missing churn or NPS data"}

            # Cost Analysis
            if "CAC" in df.columns and "Marketing_Spend" in df.columns:
                q2_cac = df[df["Quarter"] == quarters[-1]]["CAC"].iloc[0]
                q1_cac = df[df["Quarter"] == quarters[-2]]["CAC"].iloc[0]
                cac_reduction = ((q1_cac - q2_cac) / q1_cac) * 100 if q1_cac > 0 else 0
                insights["costs"] = {
                    "cac_q2": q2_cac,
                    "cac_reduction": round(cac_reduction, 1),
                    "marketing_spend": df[df["Quarter"] == quarters[-1]]["Marketing_Spend"].iloc[0]
                }
            else:
                insights["costs"] = {"error": "Missing CAC or marketing spend data"}

            logger.info("Successfully extracted spreadsheet insights")
            return insights
        except Exception as e:
            logger.error(f"Error analyzing spreadsheet: {str(e)}")
            raise Exception(f"Error analyzing spreadsheet: {str(e)}")

    @staticmethod
    def analyze_pdf_metrics(pdf_data: Dict[str, Union[str, Dict]]) -> Dict[str, str]:
        """
        Analyze PDF metrics (e.g., customer feedback).

        Args:
            pdf_data (Dict): Parsed PDF data with text and metrics

        Returns:
            Dict: Extracted insights from PDF
        """
        try:
            logger.info("Analyzing PDF metrics")
            insights = {}
            metrics = pdf_data.get("metrics", {})
            insights["customer_feedback"] = metrics.get("customer_feedback", "No feedback available")
            insights["sentiment"] = metrics.get("sentiment", "Neutral sentiment")
            logger.info("Successfully extracted PDF insights")
            return insights
        except Exception as e:
            logger.error(f"Error analyzing PDF metrics: {str(e)}")
            raise Exception(f"Error analyzing PDF metrics: {str(e)}")

    @staticmethod
    def generate_executive_summary(insights: Dict) -> List[str]:
        """
        Generate an executive summary from insights.

        Args:
            insights (Dict): Combined insights from spreadsheets and PDFs

        Returns:
            List[str]: Summary points
        """
        try:
            logger.info("Generating executive summary")
            summary = []

            # Revenue Summary
            if "revenue" in insights and "error" not in insights["revenue"]:
                summary.append(
                    f"Revenue: ${insights['revenue']['total_q2'] / 1e6:.1f}M, "
                    f"up {insights['revenue']['growth_qoq']}% QoQ, driven by {insights['revenue']['top_region']}"
                )
            else:
                summary.append("Revenue: Insufficient data for analysis")

            # Customer Metrics Summary
            if "customer_metrics" in insights and "error" not in insights["customer_metrics"]:
                churn_status = "stabilized" if insights["customer_metrics"]["churn_change"] > 0 else "increased"
                summary.append(
                    f"Churn: {churn_status} at {insights['customer_metrics']['churn_q2']}%, "
                    f"{'down' if insights['customer_metrics']['churn_change'] > 0 else 'up'} "
                    f"{abs(insights['customer_metrics']['churn_change'])}% QoQ"
                )
                summary.append(f"NPS: Improved to {insights['customer_metrics']['nps_q2']}")
            else:
                summary.append("Customer Metrics: Insufficient data for analysis")

            # Cost Summary
            if "costs" in insights and "error" not in insights["costs"]:
                summary.append(
                    f"CAC: Reduced by {insights['costs']['cac_reduction']}% to ${insights['costs']['cac_q2']}"
                )
            else:
                summary.append("Costs: Insufficient data for analysis")

            # PDF Feedback
            if "pdf_feedback" in insights:
                summary.append(f"Customer Feedback: {insights['pdf_feedback']['customer_feedback']}")

            logger.info("Successfully generated executive summary")
            return summary
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise Exception(f"Error generating executive summary: {str(e)}")

    @staticmethod
    def generate_recommendations(insights: Dict) -> List[str]:
        """
        Generate actionable recommendations based on insights.

        Args:
            insights (Dict): Combined insights from spreadsheets and PDFs

        Returns:
            List[str]: Actionable recommendations
        """
        try:
            logger.info("Generating recommendations")
            recommendations = []

            # Revenue-Based Recommendations
            if "revenue" in insights and "error" not in insights["revenue"]:
                if insights["revenue"]["growth_qoq"] > 5:
                    recommendations.append(
                        f"Increase investment in {insights['revenue']['top_region']} "
                        "to capitalize on strong growth"
                    )
                else:
                    recommendations.append("Review underperforming regions for optimization")

            # Customer Metrics-Based Recommendations
            if "customer_metrics" in insights and "error" not in insights["customer_metrics"]:
                if insights["customer_metrics"]["churn_change"] < 0:
                    recommendations.append("Launch targeted retention campaigns to address rising churn")
                else:
                    recommendations.append("Maintain retention strategies to sustain low churn")

                if insights["customer_metrics"]["nps_change"] > 0:
                    recommendations.append("Leverage positive NPS feedback in marketing campaigns")
                else:
                    recommendations.append("Investigate NPS decline and enhance customer experience")

            # Cost-Based Recommendations
            if "costs" in insights and "error" not in insights["costs"]:
                if insights["costs"]["cac_reduction"] > 5:
                    recommendations.append("Continue optimizing marketing channels to sustain CAC reduction")
                else:
                    recommendations.append("Reassess marketing spend efficiency to reduce CAC")

            logger.info("Successfully generated recommendations")
            return recommendations if recommendations else ["No actionable recommendations based on available data"]
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise Exception(f"Error generating recommendations: {str(e)}")

    @staticmethod
    def generate_insights(parsed_data: Dict[str, Union[List[Dict], List[Dict]]]) -> Dict:
        """
        Generate combined insights from parsed spreadsheet and PDF data.

        Args:
            parsed_data (Dict): Output from FileParser.parse_files (spreadsheets and PDFs)

        Returns:
            Dict: Combined insights, summary, and recommendations
        """
        try:
            logger.info("Generating combined insights")
            insights = {}

            # Analyze spreadsheets
            for spreadsheet in parsed_data.get("spreadsheets", []):
                df = spreadsheet["data"]
                insights.update(InsightsGenerator.analyze_spreadsheet(df))

            # Analyze PDFs
            for pdf in parsed_data.get("pdfs", []):
                insights["pdf_feedback"] = InsightsGenerator.analyze_pdf_metrics(pdf["data"])

            # Generate summary and recommendations
            summary = InsightsGenerator.generate_executive_summary(insights)
            recommendations = InsightsGenerator.generate_recommendations(insights)

            return {
                "metrics": insights,
                "summary": summary,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise Exception(f"Error generating insights: {str(e)}")

if __name__ == "__main__":
    try:
        from file_parser import FileParser
        import asyncio

        async def test_insights_generator():
            # Parse sample data
            df = FileParser.parse_sample_data()
            parsed_data = {"spreadsheets": [{"filename": "q2_financials.csv", "data": df}], "pdfs": []}
            
            # Generate insights
            insights = InsightsGenerator.generate_insights(parsed_data)
            print("Generated Insights:")
            print(json.dumps(insights, indent=2, default=str))

        asyncio.run(test_insights_generator())
    except ImportError as e:
        logger.error(f"Import error: {str(e)}. Ensure file_parser.py is in the same directory.")
        print(f"Import error: {str(e)}. Ensure file_parser.py is in the same directory.")
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        print(f"Error running test: {str(e)}")