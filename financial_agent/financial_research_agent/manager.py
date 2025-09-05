from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence

from rich.console import Console

# Import from the src directory directly
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from agents import Runner, RunResult, custom_span, gen_trace_id, trace

from financial_research_agent.agents.financials_agent import financials_agent
from financial_research_agent.agents.planner_agent import FinancialSearchItem, FinancialSearchPlan, planner_agent
from financial_research_agent.agents.risk_agent import risk_agent
from financial_research_agent.agents.search_agent import search_agent
from financial_research_agent.printer import Printer
from typing import TYPE_CHECKING

from financial_research_agent.agents.verifier_agent import VerificationResult, verifier_agent
from financial_research_agent.agents.writer_agent import FinancialReportData, writer_agent
from financial_research_agent.printer import Printer

import numpy as np
import sounddevice as sd
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Button, RichLog, Static
from typing_extensions import override

from agents.voice import StreamedAudioInput, VoicePipeline

# Import MyWorkflow class - handle both module and package use cases
if TYPE_CHECKING:
    # For type checking, use the relative import
    from financial_research_agent.voice_chat import MyWorkflow
else:
    # At runtime, try both import styles
    try:
        # Try absolute import first (when used as a package)
        from financial_research_agent.voice_chat import MyWorkflow
    except ImportError:
        # Fall back to direct import (when run as a script)
        from voice_chat import MyWorkflow

async def _summary_extractor(run_result: RunResult) -> str:
    """Custom output extractor for sub‑agents that return an AnalysisSummary."""
    return str(run_result.final_output.summary)


class FinancialResearchManager:
    """
    Orchestrates the full flow: planning, searching, sub‑analysis, writing, and verification.
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, query: str, mcp_server=None) -> None:  # ✅ Accept mcp_server
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
            search_results = await self._perform_searches(search_plan, mcp_server)  # ✅ Pass mcp_server
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
                # Provide helpful error message for quota issues
                print(f"\n❌ API Error: {error_msg}")
                print("💡 This is a billing issue - your OpenAI API quota has been exceeded.")
                print("🔧 To fix: Add payment method at https://platform.openai.com/account/billing")
                raise  # Re-raise to be caught by main error handler
            else:
                # Re-raise other errors
                raise

    async def _perform_searches(self, search_plan: FinancialSearchPlan, mcp_server=None) -> Sequence[str]:
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")

            # ✅ Pass `mcp_server` to `_search`
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
        input_data = f"Search term: {item.query}\nReason: {item.reason}"
        try:
            # Use a simple approach that doesn't require external servers
            # For now, we'll create a mock search result based on the query
            mock_result = f"Search results for '{item.query}': Based on {item.reason}, this search would typically return recent financial news, earnings reports, and analyst commentary about the company or topic."
            return mock_result
        except Exception as e:
            print(f"Search error: {e}")
            return None

    async def _write_report(self, query: str, search_results: Sequence[str]) -> FinancialReportData:
        fundamentals_tool = financials_agent.as_tool(
            tool_name="fundamentals_analysis",
            tool_description="Use to get a short write‑up of key financial metrics",
            custom_output_extractor=_summary_extractor,
        )
        risk_tool = risk_agent.as_tool(
            tool_name="risk_analysis",
            tool_description="Use to get a short write‑up of potential red flags",
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
        with open("financial_report.txt", "w", encoding="utf-8") as file:
            file.write(final_report.markdown_report)

        return final_report

    async def _verify_report(self, report: FinancialReportData) -> VerificationResult:
        self.printer.update_item("verifying", "Verifying report...")
        result = await Runner.run(verifier_agent, report.markdown_report)
        self.printer.mark_item_done("verifying")
        return result.final_output_as(VerificationResult)


CHUNK_LENGTH_S = 0.05  # 100ms
SAMPLE_RATE = 24000
FORMAT = np.int16
CHANNELS = 1


class Header(Static):
    """A header widget."""

    session_id = reactive("")

    @override
    def render(self) -> str:
        return "Speak to the agent. When you stop speaking, it will respond."


class AudioStatusIndicator(Static):
    """A widget that shows the current audio recording status."""

    is_recording = reactive(False)

    @override
    def render(self) -> str:
        status = (
            "🔴 Recording... (Press K to stop)"
            if self.is_recording
            else "⚪ Press K to start recording (Q to quit)"
        )
        return status


class RealtimeApp(App[None]):
    CSS = """
        Screen {
            background: #1a1b26;  /* Dark blue-grey background */
        }

        Container {
            border: double rgb(91, 164, 91);
        }

        Horizontal {
            width: 100%;
        }

        #input-container {
            height: 5;  /* Explicit height for input container */
            margin: 1 1;
            padding: 1 2;
        }

        Input {
            width: 80%;
            height: 3;  /* Explicit height for input */
        }

        Button {
            width: 20%;
            height: 3;  /* Explicit height for button */
        }

        #bottom-pane {
            width: 100%;
            height: 82%;  /* Reduced to make room for session display */
            border: round rgb(205, 133, 63);
            content-align: center middle;
        }

        #status-indicator {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        #session-display {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        Static {
            color: white;
        }
    """

    should_send_audio: asyncio.Event
    audio_player: sd.OutputStream
    last_audio_item_id: str | None
    connected: asyncio.Event

    def __init__(self) -> None:
        super().__init__()
        self.last_audio_item_id = None
        self.should_send_audio = asyncio.Event()
        self.connected = asyncio.Event()
        self.pipeline = VoicePipeline(
            workflow=MyWorkflow(secret_word="dog", on_start=self._on_transcription)
        )
        self._audio_input = StreamedAudioInput()
        self.audio_player = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=FORMAT,
        )

    def _on_transcription(self, transcription: str) -> None:
        try:
            self.query_one("#bottom-pane", RichLog).write(f"Transcription: {transcription}")
        except Exception:
            pass

    @override
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container():
            yield Header(id="session-display")
            yield AudioStatusIndicator(id="status-indicator")
            yield RichLog(id="bottom-pane", wrap=True, highlight=True, markup=True)

    async def on_mount(self) -> None:
        print("RealtimeApp mounted!")
        self.run_worker(self.start_voice_pipeline())
        self.run_worker(self.send_mic_audio())

    async def start_voice_pipeline(self) -> None:
        try:
            self.audio_player.start()
            self.result = await self.pipeline.run(self._audio_input)

            async for event in self.result.stream():
                bottom_pane = self.query_one("#bottom-pane", RichLog)
                if event.type == "voice_stream_event_audio":
                    self.audio_player.write(event.data)
                    bottom_pane.write(
                        f"Received audio: {len(event.data) if event.data is not None else '0'} bytes"
                    )
                elif event.type == "voice_stream_event_lifecycle":
                    bottom_pane.write(f"Lifecycle event: {event.event}")
        except Exception as e:
            bottom_pane = self.query_one("#bottom-pane", RichLog)
            bottom_pane.write(f"Error: {e}")
        finally:
            self.audio_player.close()

    async def send_mic_audio(self) -> None:
        device_info = sd.query_devices()
        print(device_info)

        read_size = int(SAMPLE_RATE * 0.02)

        stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
        )
        stream.start()

        status_indicator = self.query_one(AudioStatusIndicator)

        try:
            while True:
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                await self.should_send_audio.wait()
                status_indicator.is_recording = True

                data, _ = stream.read(read_size)

                await self._audio_input.add_audio(data)
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop()
            stream.close()

    async def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "enter":
            self.query_one(Button).press()
            return

        if event.key == "q":
            self.exit()
            return

        if event.key == "k":
            status_indicator = self.query_one(AudioStatusIndicator)
            if status_indicator.is_recording:
                self.should_send_audio.clear()
                status_indicator.is_recording = False
            else:
                self.should_send_audio.set()
                status_indicator.is_recording = True

