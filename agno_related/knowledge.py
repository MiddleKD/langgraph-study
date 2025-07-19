from agno.agent import Agent
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.storage.sqlite import SqliteStorage
from model import openai_model
from textwrap import dedent

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

knowledge = UrlKnowledge(
    urls=["https://docs.agno.com/introduction.md"],
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
    )
)

storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/agent.db")

agent = Agent(
    name="Agno Agent",
    model=openai_model,
    session_id="fixed_session_id",
    instructions=dedent("""
        Search your knowledge before answering the question.
        Only include the output in your response. No other text.
    """),
    storage=storage,
    knowledge=knowledge,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_runs=3,
    markdown=True,
)

if __name__ == "__main__":
    # Load the knowledge base, comment out after first run
    # Set recreate to True to recreate the knowledge base if needed
    agent.knowledge.load(recreate=False)
    agent.print_response("tool을 사용해서 지식을 찾아줘. multi agent가 뭐야?", stream=False)