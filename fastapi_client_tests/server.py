import uvicorn
import zthreading
import zthreading.tasks
from fastapi_client_tests.api import api


def server(api=api, host="0.0.0.0", port=8080):
    uvicorn.run(api, host=host, port=port)


def server_thread(api=api, host="0.0.0.0", port=8080):
    return zthreading.tasks.Task(server).start()


if __name__ == "__main__":
    server()
