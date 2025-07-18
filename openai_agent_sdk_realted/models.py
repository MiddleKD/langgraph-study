from agents.extensions.models.litellm_model import LitellmModel

ollama_model = LitellmModel(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
)