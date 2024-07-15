from typing import Annotated
from fastapi import FastAPI, Cookie, Body

API_HOST = "0.0.0.0"
API_PORT = 8180

api = FastAPI()


@api.get("/echo")
def echo(a: int, b: int):
    return a + b


@api.get("/my_func_get")
def my_func_get(a: int, b: int):
    return a + b


@api.post("/my_func_post")
def my_func_post(a: int, b: int):
    return a + b


@api.put("/my_func_put")
def my_func_put(a: int, b: int):
    return a + b


@api.delete("/my_func_delete")
def my_func_delete(a: int, b: int):
    return a + b


@api.patch("/my_func_patch")
def my_func_patch(a: int, b: int):
    return a + b


@api.get("/my_func_path_prs/{a}")
def my_func_path_prs(a: int, b: int):
    return a + b


@api.get("/my_func_cookie_prs")
def my_func_cookie_prs(a: Annotated[int, Cookie()], b: int):
    return a + b


@api.get("/my_func_body_prs")
def my_func_body_prs(a: Annotated[int, Body()], b: int):
    return a + b


@api.get("/my_func_body_multi_prs")
def my_func_body_multi_prs(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a + b


@api.get("/my_fun_async")
async def my_fun_async(a: int, b: int):
    return a + b


@api.get("/my_fun_string")
async def my_fun_string(a: str, b: str):
    return a + b


@api.get("/my_fun_dict")
async def my_fun_dict(a: dict, b: dict):
    c = a.copy()
    c.update(b)
    return b
