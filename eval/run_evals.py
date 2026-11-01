import docker
import httpx

from devops_autopilot.agent_loop import agent_loop

client = docker.from_env()

question = "My RAG app is showing errors"

def check_container_stoppage():

    try:
        container = client.containers.get("rag-postgres")
        container.stop()
        response = httpx.post("http://localhost:8080/ask", json= {"question": "What is CORS?"})
        if response.status_code != 500:
            return "injection_failed"
        
        agent_response = agent_loop(question)
        if (agent_response.status == "done" and 
        agent_response.diagnosis.container =="rag-postgres" and 
        agent_response.diagnosis.fault_type == "stopped_container"):
            return "passed"
        else:
            return "failed"
            
            
    finally:
        container.start()

if __name__ == "__main__":
    print(check_container_stoppage())