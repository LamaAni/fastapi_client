import asyncio
import requests
import json
import urllib
import urllib.parse
from inspect import Parameter
from typing import Any, Dict, List, Tuple
from fastapi.routing import APIRoute
from fastapi_client.base_client import FastAPIClientBase
from fastapi._compat import ModelField


class FastAPIClient(FastAPIClientBase):
    def __init__(
        self,
        host,
        timeout: float = None,
    ) -> None:
        super().__init__()
        self.host = self.parse_partial_url(host)

        """The host (and port) where to find the api"""
        self.args_in_body = set(["PUT", "POST", "DELETE", "PATCH"])
        """A list of methods where the arg list will be sent as body"""
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

    def __compose_request_args(
        self,
        function_args: dict,
        param_names: List[ModelField],
        value_as_json: bool = False,
    ):
        args = {}
        for pr in param_names:
            if pr.name in function_args:
                val = pr.serialize(function_args[pr.name])
                if value_as_json and not isinstance(val, str):
                    val = json.dumps(val)
                args[pr.name] = val

        return args

    def __compose_request(
        self,
        route: APIRoute,
        query: List[Parameter],
        args: list,
        kwargs: dict,
        method: str = None,
    ):
        # Converting the args.
        pr_index = 0
        l_params = len(query)
        l_args = len(args)

        function_args = {}
        """Holds args for the function. These will be loaded into the request"""

        while pr_index < l_params:
            pr = query[pr_index]
            if pr_index < l_args:
                function_args[pr.name] = args[pr_index]
            elif pr.name in kwargs:
                function_args[pr.name] = kwargs[pr.name]

            pr_index += 1

        # got all the params.
        # GET,PUT,POST,DELETE,PATCH,OPTIONS,HEAD
        if not method:
            if "POST" in route.methods:
                method = "POST"
            else:
                method = next(iter(route.methods))

        query = self.__compose_request_args(function_args, route.dependant.query_params)
        body = self.__compose_request_args(function_args, route.dependant.body_params)

        # When body is single value, no use of json. The value is just loaded into the body.
        # TODO: Add support for embed.
        if len(body) == 1:
            body = next(iter(body.values()))

        headers = self.__compose_request_args(
            function_args, route.dependant.header_params
        )
        cookies = self.__compose_request_args(
            function_args, route.dependant.cookie_params, value_as_json=True
        )
        path_params = self.__compose_request_args(
            function_args, route.dependant.path_params
        )

        if len(path_params) > 0:
            url = route.url_path_for(route.name, **path_params)
        else:
            url = route.path

        url = urllib.parse.urljoin(self.host, url)

        return requests.Request(
            method,
            url,
            params=query,
            json=body,
            headers=headers,
            timeout=self.timeout,
            cookies=cookies,
        )

    def send(
        self,
        route: APIRoute,
        query: List[Parameter],
        args: list,
        kwargs: dict,
        method: str = None,
    ):
        # Converting the args.
        pr_index = 0
        l_params = len(query)
        l_args = len(args)

        function_args = {}
        """Holds args for the function. These will be loaded into the request"""

        while pr_index < l_params:
            pr = query[pr_index]
            if pr_index < l_args:
                function_args[pr.name] = args[pr_index]
            elif pr.name in kwargs:
                function_args[pr.name] = kwargs[pr.name]

            pr_index += 1

        # got all the params.
        # GET,PUT,POST,DELETE,PATCH,OPTIONS,HEAD
        if not method:
            if "POST" in route.methods:
                method = "POST"
            else:
                method = next(iter(route.methods))

        query = self.__compose_request_args(function_args, route.dependant.query_params)
        body = self.__compose_request_args(function_args, route.dependant.body_params)

        # When body is single value, no use of json. The value is just loaded into the body.
        # TODO: Add support for embed.
        if len(body) == 1:
            body = next(iter(body.values()))

        headers = self.__compose_request_args(
            function_args, route.dependant.header_params
        )
        cookies = self.__compose_request_args(
            function_args, route.dependant.cookie_params, value_as_json=True
        )
        path_params = self.__compose_request_args(
            function_args, route.dependant.path_params
        )

        if len(path_params) > 0:
            url = route.url_path_for(route.name, **path_params)
        else:
            url = route.path

        url = urllib.parse.urljoin(self.host, url)

        # generating the session request
        rsp = requests.request(
            method,
            url,
            params=query,
            json=body,
            headers=headers,
            timeout=self.timeout,
            cookies=cookies,
        )

        return rsp.json()

    async def send_async(
        self,
        route: APIRoute,
        query: List[Parameter],
        args: list,
        kwargs: dict,
        method: str = None,
    ):
        future = asyncio.get_event_loop().run_in_executor(
            None,
            self.send,
            route,
            query,
            args,
            kwargs,
            method,
        )

        return await future
