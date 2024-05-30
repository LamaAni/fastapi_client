import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable
from fastapi_client.base_client import FastAPIClientBase


class FastAPIClientTester(FastAPIClientBase):
    # Client parameters to be added here.
    # But this dose nothing, We could implement a default api client.
    def __init__(self, log: logging.Logger = logging) -> None:
        super().__init__()
        self.log = log

    def send(self, route: APIRoute, func: DecoratedCallable, args: list, kwargs: dict):
        # Send the request given the route.
        # Dummy just returns the route and input values
        self.log.info(route.path)
        return route, args, kwargs

    async def send_async(
        self, route: APIRoute, func: DecoratedCallable, args: list, kwargs: dict
    ):
        # Send the aysnc request given the route.
        # Dummy just returns the route and input values
        self.log.info(route.path)
        return route, args, kwargs


def test_basic_client():
    api = FastAPI()

    FastAPIClientBase.enable(api)

    @api.get(path="/my_func")
    def my_func(a, b):
        print(a, b, a + b)
        return a + b

    client = FastAPIClientTester()
    my_func("a", "b")
    with client:
        my_func("a", "b")


if __name__ == "__main__":
    import pytest

    pytest.main()
