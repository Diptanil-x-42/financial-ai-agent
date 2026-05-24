from financial_research_agent.agents.verifier_agent import VERIFIER_PROMPT
from financial_research_agent.agents.writer_agent import WRITER_PROMPT


def test_writer_prompt_requires_sources():
    assert "Sources section" in WRITER_PROMPT
    assert "Do not invent citations" in WRITER_PROMPT


def test_verifier_prompt_checks_sources():
    assert "Sources section" in VERIFIER_PROMPT
    assert "unsupported numbers" in VERIFIER_PROMPT
