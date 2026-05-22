import asyncio
import json
import os
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

MAINTENANCE_MODE = False

toolName = "hired_employees"

@tool(toolName, """Get data of applications and hired employees. 
Returns a structured output in the JSON format 

Examples:
      
# Data is avaiable
    {
        "recruitingData": "# Q1 2024 – Recruiting Report
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
| **Total**                   | **15**    |",
        "isError": "false",
        "errorCategory": "",
        "isRetriable": "false"
    }
      
# Data not found
    {
        "recruitingData": "",
        "isError": "false",
        "errorCategory": "",
        "isRetriable": "false"
    }
      
# Data source is under maintenance
    {
        "recruitingData": "",
        "isError": "true",
        "errorCategory": "MAINTENANCE",
        "isRetriable": "true"
    }
""", {
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
    "required": ["year", "quarter_of_year"],
}, 
)
async def hired_employees(args):
    
    if MAINTENANCE_MODE:
        result = {
            "recruitingData": "",
            "isError": "true",
            "errorCategory": "MAINTENANCE",
            "isRetriable": "true"
            }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}

    file_path = os.path.join(os.path.dirname(__file__), "data", "recruiting", f"{args['year']}-{args['quarter_of_year']}.md")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            result = {
            "recruitingData": f.read(),
            "isError": "false",
            "errorCategory": "",
            "isRetriable": "false"
            }
    else:
        result = {
            "recruitingData": "",
            "isError": "false",
            "errorCategory": "",
            "isRetriable": "false"
            }
    return {"content": [{"type": "text", "text": json.dumps(result)}]}

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
    mcp_servers={mcpServerName: server},
    allowed_tools=[f"mcp__{mcpServerName}__{toolName}"]
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        year = "2024"
        # year = "2023"
        await client.query(f"I want to know how many percentage of application was accepted in {year} ")

        # Extract and print response
        async for message in client.receive_response():
            # print(message)
            if hasattr(message, "stop_reason"):
                if message.stop_reason == "end_turn":
                    print(message.result)


asyncio.run(main())