from dotenv import load_dotenv
load_dotenv()

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits

joke_selection_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt=(
        'Use the `joke_factory` to generate some jokes, then choose the best. '
        'You must return just a single joke.'
    ),
)

joke_generation_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=list[str]
)

@joke_selection_agent.tool
async def joke_factory(ctx:RunContext[None], count: int) -> list[str]:
    r = await joke_generation_agent.run(
        f'Please generate {count} jokes.',
        usage=ctx.usage
    )
    return r.output

app = joke_selection_agent.to_a2a(url="http://localhost:8004") # 해당 url은 서버에 영향을 주는 게 아니라 Agent card만 영향을 줌
