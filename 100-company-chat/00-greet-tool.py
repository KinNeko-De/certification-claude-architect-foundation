import asyncio
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

# Define a tool using the @tool decorator
@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hallo, {args['name']}!"}
        ]
    }

# Create an SDK MCP server
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

# Use it with Claude. allowed_tools pre-approves the tool so it runs
# without a permission prompt; it does not control tool availability.
options = ClaudeAgentOptions(
    model="claude-haiku-4-5",
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Greet Alice")

        # Extract and print response
        async for message in client.receive_response():
            # print(message)
            if hasattr(message, "stop_reason"):
                if message.stop_reason == "end_turn":
                    print(message.result)


asyncio.run(main())