import os
import time
import pytest
from typing import List
import requests
import zthreading
import zthreading.tasks
from fastapi_client import FastAPIClient
from integration_test.server import server_task
from integration_test.api import (
    my_func_get,
    my_func_post,
    my_func_put,
    my_func_delete,
    my_func_patch,
    my_func_path_prs,
    my_func_cookie_prs,
    my_func_body_prs,
    my_fun_async,
)


def is_socket_open(host):
    try:
        requests.get(host + "/echo")
        return True
    except Exception:
        return False


class TestClient:
    server: zthreading.tasks.Task = None
    client: FastAPIClient = None

    def setup_class(self):
        self.server = server_task()
        self.client = FastAPIClient(
            os.environ.get("FASTAPI_CLIENT_HOST", "localhost:8080")
        )
        # wait for server
        for i in range(10):
            if is_socket_open(self.client.host):
                return True
            print("Waiting for server")
            time.sleep(0.2)
        raise Exception("Failed to create local server")

    def teardown_class(self):
        self.server.stop()
        self.client = None

    def run_api_calls(self, calls: List[callable]):
        for i, f in enumerate(calls):
            print(f"Direct - {f.__name__}, i={i} -> {f(1,i)}")
        with self.client:
            for i, f in enumerate(calls):
                print(f"Api - {f.__name__}, i={i} -> {f(1,i)}")

    async def run_api_calls_async(self, calls: List[callable]):
        for i, f in enumerate(calls):
            print(f"Direct - {f.__name__}, i={i} -> {await f(1,i)}")
        with self.client:
            for i, f in enumerate(calls):
                print(f"Api - {f.__name__}, i={i} -> {await f(1,i)}")

    def test_norm_api_calls(self):
        self.run_api_calls(
            [
                my_func_get,
                my_func_post,
                my_func_put,
                my_func_delete,
                my_func_patch,
            ]
        )

    def test_custom_param_api_calls(self):
        self.run_api_calls(
            [
                my_func_path_prs,
                my_func_cookie_prs,
                my_func_body_prs,
            ]
        )

    @pytest.mark.asyncio
    async def test_async_api_calls(self):
        await self.run_api_calls_async([my_fun_async])


if __name__ == "__main__":

    pytest.main([__file__])
