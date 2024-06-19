import requests
import json
import urllib
import urllib.parse
import urllib3
import urllib3.util
from inspect import Parameter
from typing import Any, Dict, List, Tuple
from fastapi.routing import APIRoute
from fastapi_client.base_client import FastAPIClientBase


class FastAPIClient(FastAPIClientBase):
    def __init__(
        self,
        host,
        send_args_in_query_string: bool = False,
        timeout: float = None,
    ) -> None:
        super().__init__()
        self.host = self.parse_partial_url(host)

        """The host (and port) where to find the api"""
        self.args_in_body = set(["PUT", "POST", "DELETE", "PATCH"])
        """A list of methods where the arg list will be sent as body"""
        self.send_args_in_query_string = send_args_in_query_string
        """If true send all function args as part of the query string"""
        self.timeout = timeout
        """The timeout in seconds for the request"""

    @classmethod
    def parse_partial_url(cls, url: str):
        parts = urllib.parse.urlparse(url, "http")
        if not parts.netloc:
            parts = urllib.parse.urlparse("//" + url, "http")
        return parts.geturl()

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
        method: str = None,
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
        if not method:
            if "POST" in route.methods:
                method = "POST"
            else:
                method = next(iter(route.methods))

        # Compose send url
        # Only works for normal routes
        # no complex or combined routes.
        url = urllib.parse.urljoin(self.host, route.path)

        request_params = None
        body_params = None
        if self.send_args_in_query_string:
            request_params = request_args
        else:
            body_params = request_args

        # generating the session request
        rsp = requests.request(
            method,
            url,
            params=request_params,
            json=body_params,
            timeout=self.timeout,
        )

        return rsp.json()

    async def send_async(
        self,
        route: APIRoute,
        params: List[Tuple[str, Parameter]],
        args: list,
        kwargs: dict,
    ):
        pass
