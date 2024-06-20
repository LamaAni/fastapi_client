# FastAPIClient

An easy to use, integrated client for FastApi,

1. Uses the same decorators as FastApi
2. Dose not require one to "recreate" clients and works out of the box.
3. Allows defining the client "host" via the `with` command.
4. Works with async as well.

## BETA

This repo is in beta mode, some bugs may still exist and test coverage is not complete.
PR's welcome.

# TL;DR

To use the client you must call define the api,

```python

from typing import Annotated
from fastapi import FastAPI, Cookie, Body
from fastapi_client import FastAPIClient

api = FastAPI()

# This is required in order to allow the fast api
# client to wrap around any function calls.
# NOTE: It DOSE NOT AFFECT the operation of the API, and it dose not slow it down
# in any way.
FastAPIClient.enable(api)

@api.get("/echo")
def echo(a: int, b: int):
    rslt = a + b
    print(rslt)
    return rslt

```

We then can (async methods, just add async),

```python
from test_module import echo
from fastapi_client import FastAPIClient

# Call the function locally
echo(1,2)

# Call the function on the server running in localhost
with FastAPIClient("localhost:8080"):
    print(echo(1, 2))
```

## Install

```shell
pip install fastapi_client
```

# Contribution

Feel free to ping me in issues or directly on LinkedIn to contribute.

# Future implementation

We plan to support multiple python version per environment.

Looking for help on this subject.

# License

Copyright ©
`Zav Shotan` and other [contributors](graphs/contributors).
It is free software, released under the MIT licence, and may be redistributed under the terms specified in [LICENSE](LICENSE).
