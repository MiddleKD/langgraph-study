from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass
from typing import override

import httpx

from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

    async def system_prompt_factory(self) -> str:
        response = await self.http_client.get('https://example.com')
        response.raise_for_status()
        return f"Prompt: {response.text}"

joke_agent = Agent("openai:gpt-4o", deps_type=MyDeps)

@joke_agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    return await ctx.deps.system_prompt_factory()

async def application_code(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        app_deps = MyDeps("foobar", client)
        result = await joke_agent.run(prompt, deps=app_deps)
    return result.output

class TestMyDeps(MyDeps):
    async def system_prompt_factory(self) -> str:
        return "test prompt"

async def test_application_code() -> str:
    app_deps = TestMyDeps("foobar", None)
    with joke_agent.override(deps=app_deps):
        joke = await application_code("Tell me a joke.")
    return joke

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(application_code("Tell me a joke.")))
    print(asyncio.run(test_application_code()))
    