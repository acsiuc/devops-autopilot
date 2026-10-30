import docker

client = docker.from_env()


for container in client.containers.list():
    print(container.name)


ragapi = client.containers.get("rag-api")
# print(ragapi.logs(tail=10).decode(encoding='utf-8'))

def get_logs(container, lines = 50):

    try:
        current_container = client.containers.get(container)
    except docker.errors.NotFound:
        return f"The container {container} does not exist"

    maximum_lines = 500

    lines = min(lines, maximum_lines)

    return current_container.logs(tail = lines).decode(encoding='utf-8')


def get_status(container):
    try:
        current_container = client.containers.get(container)
    except docker.errors.NotFound:
        return f"The container {container} does not exist"
    
    status = current_container.status

    return status

print(get_status('rag-redis'))