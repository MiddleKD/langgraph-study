import json
from typing import Annotated

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_core.tools import InjectedToolCallId, tool

class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

@tool
def human_assistance(name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        }
    )

    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"
    
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)]
    }
    
    return Command(update=state_update)

graph_builder = StateGraph(State)

model = ChatOpenAI(name="gpt-4o-mini")
tools = [human_assistance]
model = model.bind_tools(tools)

memory = MemorySaver() # SqliteSaver 또는 PostgreSaver로 변경 필요

def chatbot(state: State):
    message = model.invoke(state["messages"])
    return {"messages": [message]}

tool_node = ToolNode(tools=tools)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot", tools_condition
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)


graph = graph_builder.compile(checkpointer=memory)


def print_important_state(graph, config):
    snapshot = graph.get_state(config)
    if snapshot.interrupts:
        print("Interrupts:", snapshot.interrupts[-1].value)
    print("Values:", {k: v for k, v in snapshot.values.items() if k in ("name", "birthday")})

# RUN
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}

    user_input = (
        "Can you look up when LangGraph was released? "
        "When you have the answer, use the human_assistance tool for review."
    )
    

    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    ):
        if "messages" in event:
            event["messages"][-1].pretty_print()

    print_important_state(graph, config) # 값 없음

    input("Human interrupt Press Enter to continue")
    human_command = Command(
        resume={
            "name": "LangGraph",
            "birthday": "Jan 17, 2024",
            # "correct": "yes"
        },
    )

    for event in graph.stream(human_command, config, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()

    print_important_state(graph, config) # 값 생김

    graph.update_state(config, {"name": "LangGraph (library)"})  # 상태 수동 업데이트
    
    print_important_state(graph, config) # 값 생김
