import os
import subprocess
import time
from collections.abc import Callable

import docker
import httpx
from pydantic import BaseModel

from devops_autopilot.agent_loop import ContainerType, FaultType, agent_loop

client = docker.from_env()

question = "My RAG app is showing errors"

rag_directory = "/home/axiuc-fedor/rag-model-fastapi"


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

def break_api_key():
    fake_env = os.environ.copy()
    fake_env['ANTHROPIC_API_KEY'] = 'fake_key'
    subprocess.run(['docker', 'compose', 'up', '-d', '--force-recreate', 'rag-api'], cwd=rag_directory, env = fake_env, check=False)


def restore_api_key():
    restore_env = os.environ.copy()
    restore_env.pop('ANTHROPIC_API_KEY', None)
    subprocess.run(['docker', 'compose', 'up', '-d','--force-recreate', 'rag-api'], cwd=rag_directory, check = False, env=restore_env)


break_claude_api_key = EvalCase(
    name = "break_claude_api_key",
    expected_container='rag-api',
    expected_fault='misconfiguration',
    inject=break_api_key,
    undo=restore_api_key,
)


postgres_stopped = EvalCase(
    name="postgres_stopped",
    expected_container="rag-postgres",
    expected_fault="stopped_container",
    inject=stop_postgres,
    undo=start_postgres,
)

case_list = [postgres_stopped, break_claude_api_key]


def run_case(case: EvalCase):
    try:

        if case.name == "postgres_stopped":
            for x in range(3):
                response = httpx.post(
                    "http://localhost:8080/ask", json={"question": "What is CORS?"}, timeout = 20.0)
                if response.status_code == 200:
                    break
                time.sleep(20)
            if response.status_code != 200:
                return "not_ready"

        case.inject()

        for x in range(5):
            response = httpx.post(
                        "http://localhost:8080/ask", json={"question": "What is CORS?",}, timeout = 20.0
                    )
            print(f"try {x}: {response.status_code}")
            if response.status_code == 500:
                break
            time.sleep(20)

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
