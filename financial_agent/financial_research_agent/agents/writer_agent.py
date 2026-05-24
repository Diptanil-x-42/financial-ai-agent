from pydantic import BaseModel

from agents import Agent

# Writer agent brings together raw search results and optional specialist analysis,
# then returns a cohesive markdown report.
WRITER_PROMPT = (
    "You are a senior financial analyst. You will be provided with the original query and "
    "a set of raw search summaries. Your task is to synthesize these into a long-form markdown "
    "report (at least several paragraphs) including a short executive summary and follow-up "
    "questions. If needed, you can call the available analysis tools (e.g. fundamentals_analysis, "
    "risk_analysis) to get short specialist write-ups to incorporate. Include a Sources section "
    "that names the data sources you used, such as Yahoo Finance, Reddit, or LLM search fallback. "
    "Do not invent citations, URLs, or exact figures that are not present in the provided summaries."
)


class FinancialReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence executive summary."""

    markdown_report: str
    """The full markdown report."""

    follow_up_questions: list[str]
    """Suggested follow-up questions for further research."""


writer_agent = Agent(
    name="FinancialWriterAgent",
    instructions=WRITER_PROMPT,
    model="gpt-4o",
    output_type=FinancialReportData,
)
