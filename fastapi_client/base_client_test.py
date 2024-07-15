import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable
from fastapi_client.base_client import FastAPIClientBase, enable_fastapi_client


class FastAPIClientTester(FastAPIClientBase):
    # Client parameters to be added here.
    # But this dose nothing, We could implement a default api client.
    def __init__(
        self,
        log: logging.Logger = logging,
        callback: callable = None,
    ) -> None:
        super().__init__()
        self.log = log
        self.callback = callback

    def send(self, route: APIRoute, func: DecoratedCallable, args: list, kwargs: dict):
        # Send the request given the route.
        # Dummy just returns the route and input values
        self.log.info(route.path)
        if self.callback:
            self.callback()
        return route, args, kwargs

    async def send_async(
        self, route: APIRoute, func: DecoratedCallable, args: list, kwargs: dict
    ):
        # Send the aysnc request given the route.
        # Dummy just returns the route and input values
        self.log.info(route.path)
        if self.callback:
            self.callback()
        return route, args, kwargs


def do_run_basic_client_test(api: FastAPI):
    call_seq = []

    @api.get(path="/my_func")
    def my_func(a, b):
        call_seq.append("local")
        print(a, b, a + b)
        return a + b

    client = FastAPIClientTester(callback=lambda: call_seq.append("remote"))
    my_func("a", "b")
    assert call_seq[-1] == "local", Exception("Invalid execution, expected local exec")
    with client:
        my_func("a", "b")
        assert call_seq[-1] == "remote", Exception(
            "Invalid execution, expected remote exec"
        )


def test_basic_client_on_router():
    api = FastAPI()
    FastAPIClientBase.enable(api)
    do_run_basic_client_test(api)


def test_basic_client():
    api = FastAPI()
    enable_fastapi_client()
    do_run_basic_client_test(api)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
