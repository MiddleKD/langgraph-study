from agents import Agent, Runner, InputGuardrail
from guardrails import homework_guardrail
from dotenv import load_dotenv
from agents import set_default_openai_api
set_default_openai_api("chat_completions")
from models import ollama_model

load_dotenv()

agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant.", 
    # model=ollama_model
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions", # 핸드오프 타겟을 정할 때 기준이 되는 프롬프트?
    instructions="You provide assistance with historical queries. Explain important events and context clearly." # 시스템 프롬프트
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions", # 핸드오프 타겟을 정할 때 기준이 되는 프롬프트?
    instructions="You provide assistance with math queries. Explain important events and context clearly." # 시스템 프롬프트
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on ther user's homework question.",
    handoffs = [history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail)
    ],
    model=ollama_model
)


async def main():
    # result = await Runner.run(agent, "Write a haiku about recursion in programmings.")
    # print(result.final_output)
    
    result = await Runner.run(triage_agent, "who was the first president of the united states? this is my homework")
    print(result.final_output)

    result = await Runner.run(triage_agent, "what is life") # tripwire가 발생하더라도 첫번째 에이전트는 실행됨. 내부적으로 비동기 이를 해결하려면 run_sync사용
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
