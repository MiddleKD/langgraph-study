from agno.agent import Agent
from agno.memory.v2.memory import Memory
from model import openai_model
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.tools.yfinance import YFinanceTools
from knowledge import storage

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

memory_db = SqliteMemoryDb(table_name="user_memories", db_file="tmp/agent.db")
memory = Memory(
    model=openai_model,
    db=memory_db,
    delete_memories=True,
    clear_memories=True
)

agent = Agent(
    model = openai_model,
    # session_id="fixed_session_id",
    tools=[
        YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)
    ],
    user_id="ava",
    storage=storage,
    instructions=[
        "Use tables to display data.",
        "Include sources in your response.",
        "Only include the report in your response. No other text.",
    ],
    memory=memory,
    enable_agentic_memory=True,
    markdown=True,
    monitoring=True,
)

from agno.playground import Playground
playground_app = Playground(agents=[agent])
app = playground_app.get_app()

if __name__ == "__main__":
    # agent.print_response("My favorite stocks are NVIDIA and TSLA", stream=False, show_full_reasoning=True)
    # agent.print_response("Can you compare my favorite stocks?", stream=False, show_full_reasoning=True)

    playground_app.serve("user_memory:app", reload=True)
    # 플레이그라운드 endpoint 입력시 뒤에 /v1을 붙여야 함
    