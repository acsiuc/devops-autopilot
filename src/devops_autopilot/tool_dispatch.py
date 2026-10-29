from devops_autopilot.tools import dictionary_of_tools


def tool_results(message):
    tool_results = []
    for block in message.content:
        if block.type == "tool_use":
            print(f"The tool in use is {block.name} for {block.input}")
            if block.name in dictionary_of_tools:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": dictionary_of_tools[block.name](**block.input)
                    }
                )
            else:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "is_error": True,
                        "content": "The tool requested does not exist"
                    }
                )
    return tool_results