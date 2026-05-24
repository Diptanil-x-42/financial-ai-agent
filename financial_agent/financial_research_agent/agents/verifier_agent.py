from pydantic import BaseModel

from agents import Agent

# Agent to sanity-check a synthesized report for consistency and recall.
VERIFIER_PROMPT = (
    "You are a meticulous auditor. You have been handed a financial analysis report. "
    "Your job is to verify the report is internally consistent, clearly sourced, and makes "
    "no unsupported claims. Check whether the report includes a Sources section. Point out any "
    "missing citations, unsupported numbers, vague sourcing, or uncertainties."
)


class VerificationResult(BaseModel):
    verified: bool
    """Whether the report seems coherent and plausible."""

    issues: str
    """If not verified, describe the main issues or concerns."""


verifier_agent = Agent(
    name="VerificationAgent",
    instructions=VERIFIER_PROMPT,
    model="gpt-4o-mini",
    output_type=VerificationResult,
)
