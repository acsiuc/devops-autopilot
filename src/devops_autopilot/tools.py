import docker

client = docker.from_env()

def get_logs(container, lines = 50):
    try:
        current_container = client.containers.get(container)
    except docker.errors.NotFound:
        return f"The {container} container does not exist"

    maximum_lines = 500

    lines = min(lines,maximum_lines)

    return current_container.logs(tail=lines).decode(encoding='utf-8')


def get_status(container):
    try:
        current_container = client.containers.get(container)
    except docker.errors.NotFound:
        return f"The {container} container does not exist"
    status = current_container.status

    return status

dictionary_of_tools = {"get_status": get_status, "get_logs": get_logs}

tools = [
    {
        "name": "get_status",
        "description": "Get the current state of a current container, check if it is running, exited, or restarting",
        "input_schema": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "string",
                    "description": "The 3 docker containers can be checked for status: rag-frontend, rag-postgres, rag-api",
                    "enum": ["rag-frontend", "rag-postgres", "rag-api"],
                }
            },
            "required": ["container"],
        },
    },
    {
        "name": "get_logs",
        "description": "Check the logs of any of the three containers: rag-api, rag-frontend, rag-postgres",
        "input_schema": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "string",
                    "description": "It checks the logs of one of the three containers: rag-api, rag-frontend, rag-postgres",
                    "enum": ["rag-api", "rag-frontend", "rag-postgres"],
                },
                "lines":{
                    "type": "integer",
                    "description": "The number of lines of text to be shown from the logs. If Claude needs more or less lines, it will specifiy that."
                    " It's also optional, Default 50, maximum 500. Ask for more only if needed",
                    "minimum": 1,
                    "maximum": 500,
                }
            },
            "required": ["container"],
        },
    },
]

