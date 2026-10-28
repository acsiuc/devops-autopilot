import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


def get_cpu(service):
    if service == "database":
        return "12"
    elif service == "web":
        return "97"


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


def tool_results(message):
    tool_results = []
    for block in message.content:
        if block.type == "tool_use":
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": get_cpu(block.input['service']),
                }
            )
    return tool_results


second_message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [{"type": "text", "text": "Check the state of the service"}],
        },
        {"role": "assistant", "content": message.content},
        {"role": "user", "content": tool_results(message)}
    ],
)

print(second_message.model_dump_json(indent=2))

