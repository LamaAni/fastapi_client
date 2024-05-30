from fastapi import FastAPI
from fastapi_client import FastAPIClient

api = FastAPI()
# This is required in order to allow the fast api
# client to activate.
FastAPIClient.enable(api)


@api.get("/my_func")
def my_func(a, b):
    pass


if __name__ == "__main__":
    with FastAPIClient("localhost") as client:
        my_func("a", 22)
