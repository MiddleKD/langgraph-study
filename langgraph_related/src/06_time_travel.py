from typing import Annotated

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearch(max_results=2)
tools = [tool]

llm = ChatOpenAI(name="gpt-4o-mini")
llm = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot", tools_condition
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


if __name__ == "__main__":
    for event in graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I'm learning LangGraph. Could you do some research on it for me?"
                }
            ]
        },
        config,
        stream_mode="values",
    ):
        if "messages" in event:
            event["messages"][-1].pretty_print()

    to_replay = None

    time_tavel_message_stamp = 3 # 이 시점으로 돌아간 후 다음 노드를 실행함. (이 시점의 노드가 아니라 다음 노드)
    for state in graph.get_state_history(config):
        print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
        print("-" * 80)
        if len(state.values["messages"]) == time_tavel_message_stamp:
            # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
            to_replay = state

    print(to_replay.next)
    print(to_replay.config)
    
    # Time Travel
    print(f"Time Travel to {time_tavel_message_stamp} messages")
    for event in graph.stream(None, to_replay.config, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()