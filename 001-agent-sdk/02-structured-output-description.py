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
        prompt="What is the capital of france?",
        options=ClaudeAgentOptions(
            # model="claude-haiku-4-5", # Outputs in the result, that he outputed structured output..
            allowed_tools=["Bash", "Glob"],
            output_format= {
                    "type": "json_schema", 
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string", "description": "1 sentence that answers the question directly. DO NOT provide more context"}, # description leads to better unterstanding for haiku, for Sonnet it affects that the result field is filled with summary, context and question also
                            "result" : {"type" : "string", "description": "text response to the user. provide 1-2 additional context or facts related to the question"},  # description leads to better unterstanding for haiku, for Sonnet it affects that the result field is filled with summary, context and question also
                            "questions_to_user": {"type": "array", "items": {"type": "string"},  "description": "Ask the user 1-3 questions related to the user input"},
                        },
                        "required": ["summary", "questions_to_user"],
                        "additionalProperties": False,
                    },
            }
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
            print(message.structured_output)


asyncio.run(main())