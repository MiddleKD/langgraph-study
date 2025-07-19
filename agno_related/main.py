from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from model import openai_model
from dotenv import load_dotenv

from agno.playground import Playground

load_dotenv()

agent = Agent(
    model=openai_model,
    tools=[YFinanceTools(stock_price=True)],
    introduction="Use tables to display data. Don't include any other text.",
    markdown=True,
    monitoring=True,
)

# agent.print_response("What is the stock price of Apple?", stream=False)

playground_app = Playground(agents=[agent])
app = playground_app.get_app()

if __name__ == "__main__":
    playground_app.serve("main:app", reload=True)
    # 플레이그라운드 endpoint 입력시 뒤에 /v1을 붙여야 함
