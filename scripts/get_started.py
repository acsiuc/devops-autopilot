import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_cpu",
        "description": "Get current state of the CPU based on service",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Either the web or the database can be checked",
                }
            },
            "required": ["service"],
        },
    }
]

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    tools=tools,
    messages=[{"role": "user", "content": "Check the state of the service."}],
)


def get_cpu(service):
    if service == "database":
        return 12
    elif service == "web":
        return 97


print(message)
