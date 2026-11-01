import typing
from collections.abc import Callable

import docker
import httpx
from pydantic import BaseModel

from devops_autopilot.agent_loop import ContainerType, FaultType, agent_loop

client = docker.from_env()

question = "My RAG app is showing errors"


class EvalCase(BaseModel):
    name: str
    expected_container: ContainerType
    expected_fault: FaultType
    inject: Callable[[], None]
    undo: Callable[[], None]


def stop_postgres():
    container = client.containers.get("rag-postgres")
    container.stop()


def start_postgres():
    container = client.containers.get("rag-postgres")
    container.start()


postgres_stopped = EvalCase(
    name="postgres_stopped",
    expected_container="rag-postgres",
    expected_fault="stopped_container",
    inject=stop_postgres,
    undo=start_postgres,
)


def check_container_stoppage():
    try:
        stop_postgres()
        response = httpx.post(
            "http://localhost:8080/ask", json={"question": "What is CORS?"}
        )

        if response.status_code != 500:
            return "injection_failed"

        agent_response = agent_loop(question)
        if (
            agent_response.status == "done"
            and agent_response.diagnosis.container == "rag-postgres"
            and agent_response.diagnosis.fault_type == "stopped_container"
        ):
            return "passed"
        else:
            return "failed"

    finally:
        start_postgres()


if __name__ == "__main__":
    print(check_container_stoppage())
