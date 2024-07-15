# FastAPIClient

An easy to use, integrated client for FastApi,

1. Uses the same decorators as FastApi
1. Dose not require you to redefine the api.
1. Allows defining the client "host" via the `with` command.
1. Works with async as well.
1. Dose not affect the operation of the api in any way.
1. Can be applied either globally or for a specific api (if predefined - see below).

## BETA

This repo is in beta mode, some bugs may still exist and test coverage is not complete.
PR's welcome.

# TL;DR

To use the client, you must enable it **before** defining/importing the api methods

If we are using the api `api_module` defined below,

```python
from fastapi import FastAPI

api = FastAPI()

@api.get("/echo")
def echo(a: int, b: int):
    rslt = a + b
    print(rslt)
    return rslt

```

We can use the client

```python
from fastapi_client import FastAPIClient, enable_fastapi_client

# This is REQUIRED in order to allow the fast api client to wrap around any function calls.
# NOTE: The client DOSE NOT AFFECT the operation of the API, and dose not slow it down
# in any way.
enable_fastapi_client()

from api_module import {
    echo
}

# Call the function locally
echo(1,2)

# Call the function on the server running in localhost
with FastAPIClient("localhost:8080"):
    print(echo(1, 2))
```

### Non global configuration

To define an api client that works only on a specific api/router, you must
enable the api client on the api object before defining the api functions,

```python
from fastapi import FastAPI

api = FastAPI()

# This is REQUIRED in order to allow the fast api client to wrap around any function calls.
# NOTE: The client DOSE NOT AFFECT the operation of the API, and dose not slow it down
# in any way.
FastAPIClient.enable(api)

@api.get("/echo")
def echo(a: int, b: int):
    rslt = a + b
    print(rslt)
    return rslt
```

# Install

```shell
pip install fastapi_client
```

# Contribution

Feel free to ping me for issues or submit a PR to contribute.

# License

Copyright © `Zav Shotan` and other [contributors](graphs/contributors).
It is free software, released under the MIT licence, and may be redistributed under the terms specified in [LICENSE](LICENSE).
