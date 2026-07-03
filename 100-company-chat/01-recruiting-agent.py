import asyncio
import os
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient, ResultMessage

toolName = "hired_employees"

@tool(toolName, "Get data of applications and hired employees", {
    "type": "object",
    "properties": {
        "year": {
            "type": "string",
            "description": "The calendar year in 4-digit format, e.g. 2024"
        },
        "quarter_of_year": {
            "type": "string",
            "description": "quarter to filter by. One of: Q1, Q2, Q3, Q4",
            "enum": ["Q1", "Q2", "Q3", "Q4"]
        }
    },
    "required": ["year", "quarter_of_year"]
})
async def hired_employees(args: dict[str, Any]) -> dict[str, Any]:
    file_path = os.path.join(os.path.dirname(__file__), "data", "recruiting", f"{args['year']}-{args['quarter_of_year']}.md")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return {"content": [{"type": "text", "text": f.read()}]}
    return {"content": [{"type": "text", "text": f"No data available for {args['year']} {args['quarter_of_year']}."}]}

# Create an SDK MCP server
server = create_sdk_mcp_server(
    name="recruiting-data",
    version="1.0.0",
    tools=[hired_employees]
)

# Use it with Claude. allowed_tools pre-approves the tool so it runs
# without a permission prompt; it does not control tool availability.
mcpServerName = "recruiting"

options = ClaudeAgentOptions(
    model="claude-haiku-4-5",
    system_prompt="""You are a recruiting data assistant for our company. You answer questions about hiring pipelines, new hires, and recruiting trends based on the quarterly reports provided below.

# Available data

You have the tool 'hired_employees' to get data for applications

## Data Format

Each quarterly report contains two tables:

**Hiring Pipeline** — candidates moving through the stages in that quarter:
- Applications Received
- In Process
- Recruiting Interview
- Technical Interview
- Test Day

**New Hires by Department** — employees who joined that quarter across:
- Strategy & Management
- IT & Technology Consulting
- Digital Transformation
- Finance & Risk Consulting
- HR Consulting
- Operations Consulting

### Example Report

# Q1 2024 – Recruiting Report
January – March 2024

## Hiring Pipeline

| Stage                   | Candidates |
|-------------------------|-----------|
| Applications Received   | 782       |
| In Process              | 107       |
| Recruiting Interview    | 86        |
| Technical Interview     | 59        |
| Test Day                | 25        |

## New Hires by Department

| Department                  | New Hires |
|-----------------------------|-----------|
| Strategy & Management       | 3         |
| IT & Technology Consulting  | 4         |
| Digital Transformation      | 3         |
| Finance & Risk Consulting   | 2         |
| HR Consulting               | 1         |
| Operations Consulting       | 2         |
| **Total**                   | **15**    |

---

## Instructions

- Answer only from the data provided above. Do not invent numbers or extrapolate beyond what is in the reports.
- For questions spanning multiple quarters (totals, averages, trends), calculate the answer from the relevant reports and show your work.
- When asked about a specific quarter, reference it by name (e.g. "Q3 2024").
- If the requested data is not covered by the available reports, say so clearly.
- Keep answers concise. Use tables or bullet points when comparing multiple quarters or departments.""",
    mcp_servers={mcpServerName: server},
    allowed_tools=[f"mcp__{mcpServerName}__{toolName}"]
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        year = "2024"
        # year = "2023"
        await client.query(f"I want to know how many percentage of application was accepted in {year}.")

        # Extract and print response
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                if message.stop_reason == "end_turn":
                    print(message.result)


asyncio.run(main())