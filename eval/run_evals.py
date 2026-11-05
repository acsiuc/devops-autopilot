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

case_list = [postgres_stopped]


def run_case(case: EvalCase):
    try:
        case.inject()
        response = httpx.post(
            "http://localhost:8080/ask", json={"question": "What is CORS?"}
        )

        if response.status_code != 500:
            return "injection_failed"

        agent_response = agent_loop(question)
        if (
            agent_response.status == "done"
            and agent_response.diagnosis.container == case.expected_container
            and agent_response.diagnosis.fault_type == case.expected_fault
        ):
            return "passed"
        else:
            return "failed"

    finally:
        case.undo()

def run_all_cases(cases):

    succesful = 0

    for case in cases:

        case_result = run_case(case)
        print(f"{case.name}: {case_result}")

        if case_result== 'passed':
            succesful += 1

    print(f"passed: {succesful} / {len(cases)}")


if __name__ == "__main__":
    run_all_cases(case_list)
