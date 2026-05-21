# Using the agent sdk
# Using the credential from the claude code plugin, no api key needed
# I run this from vs code. If it does not work, then use the chat interface to login again
# Is a task
# https://code.claude.com/docs/en/agent-sdk/overview#python
# pip install claude-agent-sdk

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Help me plan a trip to Paris departing May 15, 2026?",
        options=ClaudeAgentOptions(
            # model="claude-haiku-4-5",
            allowed_tools=["Bash", "Glob"],
            output_format= {
                    "type": "json_schema", 
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "next_steps": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["summary", "next_steps"],
                        "additionalProperties": False,
                    },
            }
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
            print(message.structured_output)


asyncio.run(main())