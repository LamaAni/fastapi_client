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
    my_func_body_multi_prs,
    my_fun_async,
    my_fun_string,
    my_fun_dict,
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

    def run_api_calls(self, *calls: List[callable], args: list = []):
        def test_call(call):
            rslt_direct = call(*args)
            with self.client:
                rslt_remote = call(*args)
            if rslt_direct != rslt_remote:
                raise Exception(
                    "Invalid response, direct function call result != remote result."
                    + f" {rslt_direct} != {rslt_remote}"
                )

        for c in calls:
            test_call(c)

    async def run_api_calls_async(self, *calls: List[callable], args: list = []):
        async def test_call(call):
            rslt_direct = await call(*args)
            with self.client:
                rslt_remote = await call(*args)
            if rslt_direct != rslt_remote:
                raise Exception(
                    "Invalid response, direct function call result != remote result."
                    + f" {rslt_direct} != {rslt_remote}"
                )

        for c in calls:
            await test_call(c)

    def test_norm_api_calls(self):
        self.run_api_calls(
            my_func_get,
            my_func_post,
            my_func_put,
            my_func_delete,
            my_func_patch,
            args=[1, 2],
        )

    def test_custom_param_api_calls(self):
        self.run_api_calls(
            my_func_path_prs,
            my_func_cookie_prs,
            my_func_body_prs,
            my_func_body_multi_prs,
            args=[1, 2],
        )

    @pytest.mark.asyncio
    async def test_async_api_calls(self):
        await self.run_api_calls_async(
            my_fun_async,
            args=[1, 2],
        )

    @pytest.mark.asyncio
    async def test_async_special_type_calls(self):
        await self.run_api_calls_async(my_fun_string, args=["a", "b"])
        await self.run_api_calls_async(
            my_fun_dict, args=[{"a": "b"}, {"a": 1, "c": "d"}]
        )


if __name__ == "__main__":

    pytest.main([__file__])
