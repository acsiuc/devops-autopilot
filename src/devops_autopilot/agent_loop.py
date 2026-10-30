import anthropic
from dotenv import load_dotenv

from devops_autopilot.tool_dispatch import tool_results
from devops_autopilot.tools import tools

load_dotenv()

client = anthropic.Anthropic()

question = "Check the health of my RAG system"

def agent_loop(question):
    message_history = [{"role": "user", "content": question}]

    for x in range(9):
        message = client.messages.create(
            model = "claude-opus-5-5", max_tokens = 2000, tools=tools, messages=message_history)
        message_history.append({"role": "assistant", "content": message.content})
        if message.stop_reason == "tool_use":
            message_history.append({"role": "user", "content": tool_results(message)})
        elif message.stop_reason == "end_turn":
            for block in message.content:
                if block.type == "text":
                    return block.text
        else:
            return f"The agent loop stopped because the stop_reason was {message.stop_reason}"

    return "Stopped after 9 turns without an answer."


if __name__ == "__main__":
    print(agent_loop(question))