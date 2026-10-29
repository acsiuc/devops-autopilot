import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

question = "The website is slow, find out why"


def get_cpu(service):
    if service == "database":
        return "12"
    elif service == "web":
        return "97"


def get_logs(service):

    if service == "web":
        return "WARN 1000 users logged in at once"
    elif service == "database":
        return "Everything clear on the front, Claude!"


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
                    "enum": ["web", "database"],
                }
            },
            "required": ["service"],
        },
    },
    {
        "name": "get_logs",
        "description": "Check the logs to see what is going on in the database or the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "It checks the logs of the database or of the web",
                    "enum": ["web", "database"],
                }
            },
            "required": ["service"],
        },
    },
]


def tool_results(message):
    tool_results = []
    for block in message.content:
        if block.type == "tool_use":
            print(f"The tool in use is {block.name} for {block.input["service"]}")
            if block.name in dictionary_of_tools:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": dictionary_of_tools[block.name](block.input["service"]),
                    }
                )
            else:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "is_error": True,
                        "content": "The tool requested does not exist",
                    }
                )
    return tool_results


dictionary_of_tools = {"get_cpu": get_cpu, "get_logs": get_logs}


def agent_loop(question):
    list = [{"role": "user", "content": question}]

    for x in range(9):
        message = client.messages.create(
            model="claude-opus-5-5", max_tokens=1000, tools=tools, messages=list
        )
        list.append({"role": "assistant", "content": message.content})
        if message.stop_reason == "tool_use":
            tool_output = tool_results(message)
            list.append({"role": "user", "content": tool_output})
        elif message.stop_reason == "end_turn":
            for block in message.content:
                if block.type == "text":
                    return block.text

    return "Stopped after 9 turns without an answer."


print(agent_loop(question))
