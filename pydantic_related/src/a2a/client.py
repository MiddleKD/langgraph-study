from fasta2a.client import A2AClient
from fasta2a.schema import Message
from fasta2a.schema import TextPart

client = A2AClient(
    base_url="http://localhost:8000",
    )

async def send_message():
    send_message_payload = Message(
        role="user",
        parts = [TextPart(text="Tell me a joke.", kind="text")], # kind 필수
        kind="message", # 필수
        message_id="1", # 필수
    )

    response = await client.send_message(message=send_message_payload)
    
    print("Unique ID from Client: ", response["id"])
    print("Task ID = Unique ID from Agent: ", response["result"]["id"])
    print("Context ID: ", response["result"]["context_id"])
    print("Task State: ", response["result"]["status"]["state"])

    while True:
        task = await client.get_task(task_id=response["result"]["id"])
        print("Task State: ", task["result"]["status"]["state"])
        if task["result"]["status"]["state"] == "completed":
            break
        await asyncio.sleep(1)

    print(task["result"]["artifacts"])
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(send_message())