# main.py
import asyncio

from financial_research_agent.manager import FinancialResearchManager


# Entrypoint for the financial bot example.
# Run this as `python -m financial_research_agent.main` and enter a
# financial research query, for example:
# "Write up an analysis of Apple Inc.'s most recent quarter."
async def main() -> None:
    query = input("Enter a financial research query: ")

    mgr = FinancialResearchManager()

    # The manager starts the local data server automatically when needed.
    print("Starting financial research...")

    try:
        await mgr.run(query, None)
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            print("\n" + "="*60)
            print("[ERROR] OPENAI API QUOTA EXCEEDED")
            print("="*60)
            print("Your OpenAI API account has exceeded its usage limit.")
            print("\nSolutions:")
            print("1. Add payment method: https://platform.openai.com/account/billing")
            print("2. Use demo version: python demo_financial_agent.py")
            print("3. Wait for quota reset (if on free tier)")
            print("\nTip: The project is working correctly - this is a billing issue.")
            print("="*60)
        else:
            print(f"\n[ERROR] Unexpected error: {e}")
            print("Please check your configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())
