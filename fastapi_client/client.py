import requests
import json
import urllib
import urllib.parse
from inspect import Parameter
from typing import Any, Dict, List, Tuple
from fastapi.routing import APIRoute
from fastapi_client.base_client import FastAPIClientBase


class FastAPIClient(FastAPIClientBase):
    def __init__(self, host) -> None:
        super().__init__()
        self.host = host
        """The host (and port) where to find the api"""
        self.args_in_body = set(["PUT", "POST", "DELETE", "PATCH"])
        """A list of methods where the arg list will be sent as body"""

    def urlencode(self, params: Dict[str, Any]) -> str:
        return urllib.parse.urlencode(params)

    def bodyencode(self, params: Dict[str, Any]) -> str:
        return json.dumps(params)

    def send(
        self,
        route: APIRoute,
        params: List[Parameter],
        args: list,
        kwargs: dict,
    ):
        # Converting the args.
        pr_index = 0
        l_params = len(params)
        l_args = len(args)

        request_args = {}
        while pr_index < l_params:
            pr = params[pr_index]
            if pr_index < l_args:
                request_args[pr.name] = args[pr_index]
            elif pr.name in kwargs:
                request_args[pr.name] = kwargs[pr.name]

            pr_index += 1

        # got all the params.
        # GET,PUT,POST,DELETE,PATCH,OPTIONS,HEAD
        send_method = route.methods[0]
        send_args_in_body = send_method in self.args_in_body
        if not send_args_in_body and len(route.methods) > 1:
            for method in route.methods:
                if method in self.args_in_body:
                    send_method = method
                    send_args_in_body = True
                    break

        # Compose send url

    async def send_async(
        self,
        route: APIRoute,
        params: List[Tuple[str, Parameter]],
        args: list,
        kwargs: dict,
    ):
        pass
