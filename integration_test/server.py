import uvicorn
import zthreading
import zthreading.tasks
from integration_test.api import api


def server(api=api, host="0.0.0.0", port=8080):
    uvicorn.run(api, host=host, port=port)


def server_task(api=api, host="0.0.0.0", port=8080):
    return zthreading.tasks.Task(server).start()


if __name__ == "__main__":
    server()
