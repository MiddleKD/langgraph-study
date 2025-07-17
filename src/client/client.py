from langgraph_sdk import get_client
from langgraph_sdk.schema import Command
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    result = await client.runs.wait(
        thread_id,
        "feedback", # Name of assistant. Defined in langgraph.json.
        input={
        "messages": [{
            "role": "user",
            "content": "Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review.",
            }],
        },
    )
    print(result["messages"][-1])

    result = await client.runs.wait(
        thread_id,
        "feedback", # Name of assistant. Defined in langgraph.json.
        command=Command(resume={
            "name": "LangGraph",
            "birthday": "Jan 17, 2024",
            # "correct": "yes"
        },)   
    )
    print(result["messages"][-1])

asyncio.run(main()) 