

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

dictionary_of_tools = {"get_cpu": get_cpu, "get_logs": get_logs}

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

