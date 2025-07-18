from agents import GuardrailFunctionOutput, Agent, Runner
from pydantic import BaseModel
from models import ollama_model

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoining: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
    model=ollama_model
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )
