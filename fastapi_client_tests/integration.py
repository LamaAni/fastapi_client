from fastapi import FastAPI
import zthreading.tasks
from fastapi_client import FastAPIClient

api = FastAPI()
# This is required in order to allow the fast api
# client to activate.
FastAPIClient.enable(api)


@api.get("/my_func")
def my_func_get(a: int, b: int):
    return a + b


@api.post("/my_func")
def my_func_post(a: int, b: int):
    return a + b


if __name__ == "__main__":
    import uvicorn
    import zthreading
    import time

    uv_thread = zthreading.tasks.Task(
        lambda: uvicorn.run(api, host="0.0.0.0", port=8080)
    ).start()

    print("Waiting for uvcorn")
    time.sleep(2)

    # print(my_func_get(1, 22))
    with FastAPIClient("localhost:8080") as client:
        print(my_func_post(1, 22))

    uv_thread.stop()
