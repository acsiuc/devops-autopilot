import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

question = "Check the state of the DB"

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
                    "enum":["web", "database"]
                }
            },
            "required": ["service"],
        },
    }
]

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


def agent_loop(question):
    list = [{"role":"user", "content":question}]

    for x in range(9):

        message = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=1000,
            tools=tools,
            messages = list
        )
        list.append({"role":"assistant", "content":message.content})
        if message.stop_reason == "tool_use":
            tool_output = tool_results(message)
            list.append({"role":"user", "content": tool_output})
        elif message.stop_reason == "end_turn":
            for block in message.content:
                if block.type == 'text':
                    return block.text

    return "Stopped after 9 turns without an answer."


print(agent_loop(question))

