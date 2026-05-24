# search_agent.py
import asyncio
from pathlib import Path
import os
import shutil
import subprocess
import time
import requests
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.model_settings import ModelSettings

# Initialize the search agent
search_agent = Agent(
    name="Assistant",
    instructions="Use the tools to answer the questions.",
    model_settings=ModelSettings(tool_choice="required"),
)

async def run(mcp_server, input_data):
    # For now, we'll use a simple HTTP client approach
    message = "Search on Yahoo Finance for financial data"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=search_agent, input=message)
    # Save result to a text file
    report_path = Path(__file__).resolve().parent.parent.parent / "financial_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(str(result))  # Ensure result is stringified
    return result

async def main():
    # Start the Flask server in a subprocess
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "search_agent_server.py")

        print("Starting Flask server at http://localhost:8000 ...")

        process = subprocess.Popen(["python", server_file])

        # Wait for server to start
        time.sleep(3)

        # Test the server
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("Flask server started successfully!")
            else:
                print(f"Server health check failed: {response.status_code}")
        except Exception as e:
            print(f"Could not connect to server: {e}")

        print("Running example...\n\n")
        
        trace_id = gen_trace_id()
        with trace(workflow_name="Flask Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(None, "test")
            
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        exit(1)
    finally:
        if process:
            process.terminate()

if __name__ == "__main__":
    if not shutil.which("python"):
        raise RuntimeError(
            "python is not installed or not in PATH."
        )

    asyncio.run(main())
