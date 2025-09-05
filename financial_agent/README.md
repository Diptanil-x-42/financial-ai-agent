# Financial Research Agent

This project allows you to generate financial reports and interact with them through voice chat.

## Prerequisites

Ensure you have Python 10+ installed. It is recommended to create and activate a virtual environment before proceeding.

Then unsure to set up you python environement:

   `python -m venv .venv`<br>
   `source .venv/bin/activate`

## Installation

1. **Install requirements:**
   To install the necessary dependencies, use the following command:

   ```bash
   pip install -r requirements.txt

2. **Install dependencies:**
Install dependencies: After installing the requirements, run the following command to synchronize the project dependencies:

   ```bash
   make sync

3. **Install OpenAI agents:**
To install the openai-agents package, run:
    ```bash
    pip install openai-agents

4- **Generate the financial report:**
Set your OpenAI key first:
   
      $env:OPENAI_API_KEY="your_api_key_here"
Then use the following command:

    python -m financial_research_agent.main

5- **Chat with voice to interact with the report:**
To interact with the financial report via voice, run:

    python -m financial_research_agent.mainvoice

