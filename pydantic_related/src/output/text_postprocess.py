from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent, TextOutput


def split_into_words(text: str) -> list[str]:
    return text.split()


agent = Agent(
    'openai:gpt-4o',
    output_type=TextOutput(split_into_words), # LLM보고 여기에 맞추라고 요청하는 것이 아니라, 단순히 로직을 돌리는 것. 쓸모없는 API호출 감소
)
result = agent.run_sync('Who was Albert Einstein?')
print(result.all_messages())
print(result.output)
#> ['Albert', 'Einstein', 'was', 'a', 'German-born', 'theoretical', 'physicist.']