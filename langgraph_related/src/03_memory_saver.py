# 컨텍스트 길이 길어지면 자동으로 줄이거나 그러지는 않음
# openai.BadRequestError: Error code: 400 - {'error': {'message': "This model's maximum context length is 16385 tokens. However, your messages resulted in 17062 tokens (16237 in the messages, 825 in the functions). Please reduce the length of the messages or functions.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}
# During task with name 'chatbot' and id '3a0a676c-0253-0692-22df-f90abd745823'

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

model = ChatOpenAI(name="gpt-4o-mini")
tool = TavilySearch(max_results=2)
tools = [tool]
model = model.bind_tools(tools)

memory = MemorySaver() # SqliteSaver 또는 PostgreSaver로 변경 필요

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}


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

config = {"configurable": {"thread_id": "1"}}

# For visualization
def stream_graph_update(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print(event)
            print("Assistant:", value["messages"][-1].content)


if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_update(user_input)
