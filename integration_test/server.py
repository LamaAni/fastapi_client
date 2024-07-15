import uvicorn
import zthreading
import zthreading.tasks
from integration_test.api import api, API_PORT, API_HOST


def server(api=api, host=API_HOST, port=API_PORT):
    uvicorn.run(api, host=host, port=port)


def server_task(api=api, host=API_HOST, port=API_PORT):
    return zthreading.tasks.Task(server).start()


if __name__ == "__main__":
    server()
