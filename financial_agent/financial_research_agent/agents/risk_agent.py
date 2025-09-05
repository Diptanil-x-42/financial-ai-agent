from pydantic import BaseModel

# Import from the src directory directly
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from agents import Agent

# A sub‑agent specializing in identifying risk factors or concerns.
RISK_PROMPT = (
    "You are a risk analyst looking for potential red flags in a company's outlook. "
    "Given background research, produce a short analysis of risks such as competitive threats, "
    "regulatory issues, supply chain problems, or slowing growth. Keep it under 2 paragraphs."
)


class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""


risk_agent = Agent(
    name="RiskAnalystAgent",
    instructions=RISK_PROMPT,
    output_type=AnalysisSummary,
)
