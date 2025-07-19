from dotenv import load_dotenv
load_dotenv()
from typing_extensions import TypedDict

from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits


class NeverOutputType(TypedDict):
    """
    Never ever coerce data to this type.
    """

    never_use_this: str


agent = Agent(
    'openai:gpt-4o',
    retries=3,  # agent running에 대한 재시도 제한 (총 실행 - 1)
    output_type=NeverOutputType,
    system_prompt='Any time you get a response, call the `infinite_retry_tool` to produce another response.',
)


@agent.tool_plain(retries=5)  # tool에 대한 호출 재시도 제한 (총 실행 - 1)
def infinite_retry_tool() -> int:
    print("retrying...")
    raise ModelRetry('Please try again.')


try:
    result_sync = agent.run_sync(
        'Begin infinite retry loop!', usage_limits=UsageLimits(request_limit=3)  # LLM API 호출 제한
    )
except UsageLimitExceeded as e:
    print(e)
    #> The next request would exceed the request_limit of 3