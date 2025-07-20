from typing import Union

from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition


# 여기서는 tool_def 리스트를 받음
async def check_tools(ctx: RunContext[None], tool_defs: list[ToolDefinition]) -> list[ToolDefinition]: # 도구 등록 과정이 아닌 LLM이 사용되는 모든 콜링에서 실행됨. 가볍게 만들어야 함!
    print("check tools")
    # if ctx.deps == 42: # filter로도 구현 가능하겠죠?
    #     return [tool_def for tool_def in tool_defs if tool_def.name == '42']
    return tool_defs

agent = Agent('test', prepare_tools=check_tools) # tool마다 prepare를 검사한 후 Agent 자체에 대해 1회만 실시 (LLM이 사용되는 모든 콜링에서 실행됨) 
# ex: tool3개에 대해 prepare 3회 => Agent에 prepare 1회 => LLM 콜링 반복


async def only_if_42(
    ctx: RunContext[int], tool_def: ToolDefinition # 여기서는 단일 tool_def를 받음
) -> Union[ToolDefinition, None]:
    print("only if 42")
    if ctx.deps == 42:
        return tool_def


@agent.tool(prepare=only_if_42) # 도구 등록 과정이 아닌 LLM이 사용되는 모든 콜링에서 실행됨. 가볍게 만들어야 함!
def hitchhiker(ctx: RunContext[int], answer: str) -> str:
    return f'{ctx.deps} {answer}'


result = agent.run_sync('testing...', deps=41)
print(result.output)
#> success (no tool calls)
result = agent.run_sync('testing...', deps=42)
print(result.output)
#> {"hitchhiker":"42 a"}
