from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import requests
from rich.console import Console

from agents import Runner, RunResult, custom_span, gen_trace_id, trace

from financial_research_agent.agents.financials_agent import financials_agent
from financial_research_agent.agents.planner_agent import FinancialSearchItem, FinancialSearchPlan, planner_agent
from financial_research_agent.agents.risk_agent import risk_agent
from financial_research_agent.agents.search_agent import search_agent
from financial_research_agent.agents.ticker_utils import resolve_ticker
from financial_research_agent.agents.verifier_agent import VerificationResult, verifier_agent
from financial_research_agent.agents.writer_agent import FinancialReportData, writer_agent
from financial_research_agent.printer import Printer

# Directory where reports are saved (next to this file)
_REPORT_DIR = Path(__file__).resolve().parent.parent
_REPORT_PATH = _REPORT_DIR / "financial_report.txt"

# Address of the Flask data server (search_agent_server.py)
_DATA_SERVER_URL = "http://localhost:8000"
_SERVER_FILE = Path(__file__).resolve().parent / "agents" / "search_agent_server.py"


async def _summary_extractor(run_result: RunResult) -> str:
    """Custom output extractor for sub-agents that return an AnalysisSummary."""
    return str(run_result.final_output.summary)


class FinancialResearchManager:
    """
    Orchestrates the full flow: planning, searching, sub-analysis, writing, and verification.
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)
        self._server_process: subprocess.Popen[str] | None = None

    async def run(self, query: str, mcp_server=None) -> None:
        trace_id = gen_trace_id()
        with trace("Financial research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item("start", "Starting financial research...", is_done=True)

            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan, mcp_server)
            report = await self._write_report(query, search_results)
            verification = await self._verify_report(report)

            final_report = f"Report summary\n\n{report.short_summary}"
            self.printer.update_item("final_report", final_report, is_done=True)

            self.printer.end()

        # Print to stdout
        print("\n\n=====REPORT=====\n\n")
        print(f"Report:\n{report.markdown_report}")
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        print("\n".join(report.follow_up_questions))
        print("\n\n=====VERIFICATION=====\n\n")
        print(verification)

    async def _plan_searches(self, query: str) -> FinancialSearchPlan:
        self.printer.update_item("planning", "Planning searches...")
        try:
            result = await Runner.run(planner_agent, f"Query: {query}")
            self.printer.update_item(
                "planning",
                f"Will perform {len(result.final_output.searches)} searches",
                is_done=True,
            )
            return result.final_output_as(FinancialSearchPlan)
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"\n[ERROR] API Error: {error_msg}")
                print("Tip: This is a billing issue - your OpenAI API quota has been exceeded.")
                print("Fix: Add a payment method at https://platform.openai.com/account/billing")
                raise
            else:
                raise

    async def _perform_searches(self, search_plan: FinancialSearchPlan, mcp_server=None) -> Sequence[str]:
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            self._ensure_data_server()

            tasks = [asyncio.create_task(self._search(item, mcp_server)) for item in search_plan.searches]

            results: list[str] = []
            num_completed = 0

            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
                self.printer.update_item(
                    "searching", f"Searching... {num_completed}/{len(tasks)} completed"
                )

            self.printer.mark_item_done("searching")
            return results

    async def _search(self, item: FinancialSearchItem, mcp_server=None) -> str | None:
        """Search for financial data using the Flask data server, with graceful fallback."""
        ticker = resolve_ticker(item.query)
        try:
            # Try Yahoo Finance via the Flask data server
            response = requests.post(
                f"{_DATA_SERVER_URL}/get_yahoo_data",
                json={"stock_data": item.query, "ticker": ticker},
                timeout=10,
            )
            if response.ok:
                data = response.json()
                if data.get("success"):
                    return (
                        f"Source: {data.get('source', 'Yahoo Finance')}\n"
                        f"Query: {item.query}\n"
                        f"Ticker: {data.get('ticker', ticker)}\n"
                        f"Data: {data['data']}"
                    )

            # Try Reddit via the Flask data server
            response = requests.post(
                f"{_DATA_SERVER_URL}/get_reddit_data",
                json={"stock_data": item.query},
                timeout=10,
            )
            if response.ok:
                data = response.json()
                if data.get("success"):
                    return (
                        f"Source: {data.get('source', 'Reddit')}\n"
                        f"Query: {item.query}\n"
                        f"URL: {data.get('source_url', 'N/A')}\n"
                        f"Data: {data['data']}"
                    )

            return f"Search results for '{item.query}': No data returned from server."

        except requests.ConnectionError:
            # Server not running - use the LLM agent as fallback
            try:
                input_data = f"Search term: {item.query}\nReason: {item.reason}"
                result = await Runner.run(search_agent, input_data)
                return f"Source: LLM search fallback\nQuery: {item.query}\nData: {result.final_output}"
            except Exception:
                return f"Search results for '{item.query}': Server unavailable and agent fallback failed."
        except Exception as e:
            print(f"Search error for '{item.query}': {e}")
            return None

    async def _write_report(self, query: str, search_results: Sequence[str]) -> FinancialReportData:
        fundamentals_tool = financials_agent.as_tool(
            tool_name="fundamentals_analysis",
            tool_description="Use to get a short write-up of key financial metrics",
            custom_output_extractor=_summary_extractor,
        )
        risk_tool = risk_agent.as_tool(
            tool_name="risk_analysis",
            tool_description="Use to get a short write-up of potential red flags",
            custom_output_extractor=_summary_extractor,
        )
        writer_with_tools = writer_agent.clone(tools=[fundamentals_tool, risk_tool])
        self.printer.update_item("writing", "Thinking about report...")
        input_data = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(writer_with_tools, input_data)
        update_messages = [
            "Planning report structure...",
            "Writing sections...",
            "Finalizing report...",
        ]
        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                self.printer.update_item("writing", update_messages[next_message])
                next_message += 1
                last_update = time.time()
        self.printer.mark_item_done("writing")
        final_report = result.final_output_as(FinancialReportData)

        # Save to a file
        with open(_REPORT_PATH, "w", encoding="utf-8") as file:
            file.write(final_report.markdown_report)

        return final_report

    async def _verify_report(self, report: FinancialReportData) -> VerificationResult:
        self.printer.update_item("verifying", "Verifying report...")
        result = await Runner.run(verifier_agent, report.markdown_report)
        self.printer.mark_item_done("verifying")
        return result.final_output_as(VerificationResult)

    def _ensure_data_server(self) -> None:
        """Start the local data server when it is not already running."""
        try:
            response = requests.get(f"{_DATA_SERVER_URL}/health", timeout=2)
            if response.ok:
                return
        except requests.RequestException:
            pass

        if self._server_process and self._server_process.poll() is None:
            return

        try:
            self._server_process = subprocess.Popen(
                [sys.executable, str(_SERVER_FILE)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            time.sleep(2)
        except Exception as exc:
            print(f"Could not start local financial data server: {exc}")
