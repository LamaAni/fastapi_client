from fastapi_client import FastAPIClient, enable_fastapi_client

# Enable the client before loading the api.
enable_fastapi_client()

from integration_test.api import (  # noqa E402
    API_CLIENT_URL,
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


if __name__ == "__main__":
    import time
    import asyncio
    from integration_test.server import server_task

    server = server_task()

    print("Waiting for uvicorn")
    time.sleep(1)

    async def main():
        # print(my_func_get(1, 22))
        with FastAPIClient(API_CLIENT_URL):
            for i, f in enumerate(
                [
                    my_func_get,
                    my_func_post,
                    my_func_put,
                    my_func_delete,
                    my_func_patch,
                    my_func_path_prs,
                    my_func_cookie_prs,
                    my_func_body_prs,
                ]
            ):
                print(f"{f.__name__}, i={i} -> {f(1,i)}")

            print(
                "Async: ",
                await my_fun_async(10, 10),
            )

    asyncio.run(main())
    server.stop()
    print("server stopped")
