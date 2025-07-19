from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

import logfire

# logfire.configure()
# logfire.instrument_asyncpg()

class DatabaseConn:
    """This is a fake database for example purposes.

    In reality, you'd be connecting to an external database
    (e.g. PostgreSQL) to get information about customers.
    """

    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123:
            if include_pending:
                return 123.45
            else:
                return 100.00
        else:
            raise ValueError('Customer not found')

@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn

class SupportOutput(BaseModel):
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description='Whether to block the customer card')
    risk: int = Field(description='Risk level of query', ge=0, le=10)

support_agent = Agent(
    "openai:gpt-4.1-nano",
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=(  
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query.'
    ),
    instrument=True,
)

@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"Customer name: {customer_name}"

@support_agent.tool
async def customer_balance(ctx: RunContext[SupportDependencies], include_pending: bool = False) -> float:
    """Returns the customer's current account balance."""
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )

async def main():
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())
    result = await support_agent.run("What's my balance?", deps=deps)
    print(result.output)

    result = await support_agent.run("I just lost my card!", deps=deps)
    print(result.output)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    