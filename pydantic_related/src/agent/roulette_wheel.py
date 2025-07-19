from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent, RunContext

roulette_agent = Agent(
    "openai:gpt-4.1-nano",
    deps_type=int,
    output_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)

@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return "winner" if square == ctx.deps else "loser"

success_number = 18

result = roulette_agent.run_sync("put my money on square eighteen", deps=success_number)
print(result.output)

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.new_messages(output_tool_return_content="temp"))
print(result.new_messages(output_tool_return_content="false"))
print(result.output)

async def main():
    nodes = []
    # Begin an AgentRun, which is an async-iterable over the nodes of the agent's graph
    async with roulette_agent.iter('put my money on square eighteen', deps=success_number) as agent_run:
        async for node in agent_run:
            # Each node represents a step in the agent's execution
            nodes.append(node)
    print(nodes)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())