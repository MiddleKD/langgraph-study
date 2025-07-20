from dotenv import load_dotenv
load_dotenv()
from pydantic_core import to_jsonable_python

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter  

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
history_step_1 = result1.all_messages()
print(history_step_1)
as_python_objects = to_jsonable_python(history_step_1)
print(as_python_objects)
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_python(as_python_objects)
print(same_history_as_step_1)
result2 = agent.run_sync(  
    'Tell me a different joke.', message_history=same_history_as_step_1
)
print(result2.all_messages())