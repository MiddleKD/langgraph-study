"""
uv run src/04_human_feedback.py 
================================ Human Message =================================

인간 전문가 불러줘
tool call
================================== Ai Message ==================================
Tool Calls:
  human_assistance (call_2b8y18r28bjAKKJOgs3R8E7F)
 Call ID: call_2b8y18r28bjAKKJOgs3R8E7F
  Args:
    query: I need human assistance.
('tools',)
Human interrupt: 궁금한 점을 양식에 맞춰 작성하라고 전달해줘. 여기 양식이야 # 1. query # 2. your info
================================== Ai Message ==================================
Tool Calls:
  human_assistance (call_2b8y18r28bjAKKJOgs3R8E7F)
 Call ID: call_2b8y18r28bjAKKJOgs3R8E7F
  Args:
    query: I need human assistance.
================================= Tool Message =================================
Name: human_assistance

"궁금한 점을 양식에 맞춰 작성하라고 전달해줘. 여기 양식이야 # 1. query # 2. your info"
no tool call
================================== Ai Message ==================================

인간 전문가와의 대화를 위해 아래와 같이 정보를 제공해 주세요:
1. 물어보고 싶은 내용
2. 여러분의 정보 (선택 사항)
자세한 내용을 입력해 주세요.
"""

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

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_core.tools import tool

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def human_assistance(query: str):
    """Request assistance from a human."""
    human_response = interrupt({"query":query})
    return human_response["data"]

graph_builder = StateGraph(State)

model = ChatOpenAI(name="gpt-4o-mini")
tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
model = model.bind_tools(tools)

memory = MemorySaver() # SqliteSaver 또는 PostgreSaver로 변경 필요

def chatbot(state: State):
    message = model.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

class BasicToolNode:
    def __init__(self, tools: list):
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


def route_tools(state: State):
    if isinstance(state, list):
        ai_messages = state[-1]
    elif messages := state.get("messages", []):
        ai_messages = messages[-1]
    else:
        raise ValueError("No messages found in state")

    if hasattr(ai_messages, "tool_calls") and len(ai_messages.tool_calls) > 0:
        print("tool call")
        return "tools"
    print("no tool call")
    return END


tool_node = BasicToolNode(tools)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot", route_tools, {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)

user_input = "인간 전문가 불러줘"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
print(snapshot.next)

human_response = input("Human interrupt: ")

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
