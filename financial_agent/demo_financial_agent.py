#!/usr/bin/env python3
"""
Demo Financial Research Agent
This shows how the agent would work without making actual API calls
"""

import asyncio
import time
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel

class DemoPrinter:
    """Demo printer that shows the workflow without making API calls"""
    
    def __init__(self):
        self.console = Console()
        self.items = {}
        
    def update_item(self, item_id: str, content: str, is_done: bool = False):
        self.items[item_id] = (content, is_done)
        self._print_status()
        
    def mark_item_done(self, item_id: str):
        self.items[item_id] = (self.items[item_id][0], True)
        self._print_status()
        
    def _print_status(self):
        self.console.clear()
        for item_id, (content, is_done) in self.items.items():
            status = "[OK]" if is_done else "[WAIT]"
            self.console.print(f"{status} {content}")
            
    def end(self):
        self.console.print("\nDone: Demo completed!")

async def demo_financial_research(query: str):
    """Demo the financial research workflow"""
    
    printer = DemoPrinter()
    
    # Step 1: Planning
    printer.update_item("planning", "Planning searches...")
    await asyncio.sleep(2)
    printer.update_item("planning", "Will perform 8 searches", is_done=True)
    
    # Step 2: Searching
    printer.update_item("searching", "Searching...")
    await asyncio.sleep(1)
    printer.update_item("searching", "Searching... 1/8 completed")
    await asyncio.sleep(0.5)
    printer.update_item("searching", "Searching... 4/8 completed")
    await asyncio.sleep(0.5)
    printer.update_item("searching", "Searching... 8/8 completed", is_done=True)
    
    # Step 3: Writing
    printer.update_item("writing", "Thinking about report...")
    await asyncio.sleep(1)
    printer.update_item("writing", "Planning report structure...")
    await asyncio.sleep(1)
    printer.update_item("writing", "Writing sections...")
    await asyncio.sleep(1)
    printer.update_item("writing", "Finalizing report...", is_done=True)
    
    # Step 4: Verification
    printer.update_item("verifying", "Verifying report...")
    await asyncio.sleep(1)
    printer.mark_item_done("verifying")
    
    # Final report
    printer.update_item("final_report", "Report summary\n\nApple Inc. showed strong Q4 performance with revenue growth of 8% year-over-year, driven by iPhone sales and services revenue.", is_done=True)
    
    printer.end()
    
    # Show what the actual report would look like
    console = Console()
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold blue]DEMO FINANCIAL REPORT[/bold blue]\n\n"
        f"[bold]Query:[/bold] {query}\n\n"
        f"[bold]Executive Summary:[/bold]\n"
        f"Apple Inc. demonstrated strong financial performance in their most recent quarter, "
        f"with revenue growth of 8% year-over-year. The company's iPhone segment continues "
        f"to be the primary driver of revenue, while services revenue showed impressive growth.\n\n"
        f"[bold]Key Findings:[/bold]\n"
        f"- Revenue: $89.5 billion (8% YoY growth)\n"
        f"- iPhone sales: $43.8 billion\n"
        f"- Services revenue: $22.3 billion (16% YoY growth)\n"
        f"- Net income: $22.9 billion\n\n"
        f"[bold]Follow-up Questions:[/bold]\n"
        f"- How does Apple's performance compare to competitors?\n"
        f"- What are the growth prospects for Apple's services business?\n"
        f"- How might supply chain issues affect future performance?",
        title="Financial Analysis Report",
        border_style="green"
    ))
    console.print("="*60)

async def main():
    """Main demo function"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold red]DEMO MODE[/bold red]\n\n"
        "This is a demo of the Financial Research Agent.\n"
        "Your OpenAI API quota has been exceeded.\n"
        "To use the real agent, please add payment method to your OpenAI account.",
        title="Financial Research Agent Demo",
        border_style="red"
    ))
    
    query = input("\nEnter a financial research query (or press Enter for demo): ")
    if not query:
        query = "Write up an analysis of Apple Inc.'s most recent quarter"
    
    await demo_financial_research(query)

if __name__ == "__main__":
    asyncio.run(main())
