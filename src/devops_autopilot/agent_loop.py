import typing

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

from devops_autopilot.tool_dispatch import tool_results
from devops_autopilot.tools import tools

load_dotenv()

client = anthropic.Anthropic()

question = "My RAG app is returning errors"

class Diagnosis(BaseModel):
    container: typing.Literal["rag-api", "rag-postgres", "rag-frontend"] | None
    fault_type: (
        typing.Literal["stopped_container", "misconfiguration", "crashed"] | None
    )
    explanation: str

class AgentResult(BaseModel):
     status: typing.Literal['done', 'max_turns', 'stopped']
     diagnosis: Diagnosis | None = None


def agent_loop(question):
    message_history = [{"role": "user", "content": question}]

    for x in range(9):
        message = client.messages.parse(
            model="claude-opus-5-5",
            max_tokens=2000,
            tools=tools,
            messages=message_history,
            output_format=Diagnosis,
        )
        message_history.append({"role": "assistant", "content": message.content})
        if message.stop_reason == "tool_use":
            message_history.append({"role": "user", "content": tool_results(message)})
        elif message.stop_reason == "end_turn":
                return AgentResult(status = "done", diagnosis = message.parsed_output)
        else:
            return AgentResult(status = "stopped")

    return AgentResult(status = "max_turns")


if __name__ == "__main__":
    print(agent_loop(question))
