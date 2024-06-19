import asyncio
import requests
import json
import urllib
import urllib.parse
from inspect import Parameter
from typing import List
from fastapi.routing import APIRoute
from fastapi_client.base_client import FastAPIClientBase
from fastapi._compat import ModelField


class FastAPIClient(FastAPIClientBase):
    def __init__(
        self,
        host,
        timeout: float = None,
        headers: dict = None,
        cookies: dict = None,
    ) -> None:
        super().__init__()
        self.host = self.parse_partial_url(host)
        """The host (schema, port, etc..) where to find the api"""
        self.args_in_body = set(["PUT", "POST", "DELETE", "PATCH"])
        """A list of methods where the arg list will be sent as body"""
        self.timeout = timeout
        """The timeout in seconds for the request"""
        self.headers = headers
        """Override/add to the headers as sent to the api"""
        self.cookies = cookies
        """Override/add to the cookies sent to the api"""

    @classmethod
    def parse_partial_url(cls, url: str):
        """Convert a partial url ('localhost') to one that has
        a schema and validity

        Args:
            url (str): The partial url

        Returns:
            str: The parsed url
        """
        parts = urllib.parse.urlparse(url, "http")
        if not parts.netloc:
            parts = urllib.parse.urlparse("//" + url, "http")
        return parts.geturl()

    def serialize_cookie(self, o) -> str:
        """Converts an object to string. Used to encode cookies (defaults to json)"""
        return json.dumps(o)

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
                    val = self.serialize_cookie(val)
                args[pr.name] = val

        return args

    def parse_function_input_arguments(
        self,
        function_args: List[Parameter],
        args: list,
        kwargs: dict,
    ):
        """Converts the arguments that were sent to the function into
        function arguments which are to be sent to the server.

        Args:
            function_args (List[Parameter]): A list of all function arguments as defined in the function.
            args (list): The list of arguments sent (list *args)
            kwargs (dict): The dictionary of arguments sent (dict **kwargs)

        Returns:
            dict: Mapping of argument name -> argument value
        """
        len_function_args = len(function_args)
        len_args = len(args)
        args_map = {}

        idx = 0
        while idx < len_function_args:
            pr = function_args[idx]
            if idx < len_args:
                args_map[pr.name] = args[idx]
            elif pr.name in kwargs:
                args_map[pr.name] = kwargs[pr.name]

            idx += 1

        return args_map

    def parse_response(self, res: requests.Response):
        """Parse the response as sent from the server

        Args:
            res (requests.Response): The response to be parsed.

        Returns:
            Any: The response value.
        """
        return res.json()

    def send(
        self,
        route: APIRoute,
        function_args: List[Parameter],
        args: list,
        kwargs: dict,
        method: str = None,
    ):
        """Send a request to the fast api server.

        Args:
            route (APIRoute): The route to use.
            function_args (List[Parameter]): The full set of function argument definitions, that

            args (list): The arguments sent to the function
            kwargs (dict): The argument dict (**kwargs) send to the function
            method (str, optional): Override the request method. Defaults to None.

        Returns:
            Any: The result of the request loaded from json.
        """
        args_map = self.parse_function_input_arguments(
            function_args=function_args,
            args=args,
            kwargs=kwargs,
        )

        # got all the params.
        # GET,PUT,POST,DELETE,PATCH,OPTIONS,HEAD
        if not method:
            if "POST" in route.methods:
                method = "POST"
            else:
                method = next(iter(route.methods))

        # Resolve request arg dictionaries
        query_args = self.__compose_request_args(args_map, route.dependant.query_params)
        headers = self.__compose_request_args(args_map, route.dependant.header_params)
        cookies = self.__compose_request_args(
            args_map, route.dependant.cookie_params, value_as_json=True
        )
        path_params = self.__compose_request_args(args_map, route.dependant.path_params)
        body = self.__compose_request_args(args_map, route.dependant.body_params)

        # When body is single value, no use of json. The value is just loaded into the body.
        # TODO: Add support for embed.
        if len(body) == 1:
            body = next(iter(body.values()))

        # When using path params, we need to update the url
        # to match these path params.
        if len(path_params) > 0:
            url = route.url_path_for(route.name, **path_params)
        else:
            # Just use the path.
            url = route.path

        # Join with host.
        url = urllib.parse.urljoin(self.host, url)

        # Update the headers and cookies.
        if self.headers:
            headers.update(self.headers)
        if self.cookies:
            cookies.update(self.cookies)

        return self.parse_response(
            requests.request(
                method,
                url,
                params=query_args,
                json=body,
                headers=headers,
                timeout=self.timeout,
                cookies=cookies,
            )
        )

    async def send_async(
        self,
        route: APIRoute,
        query: List[Parameter],
        args: list,
        kwargs: dict,
        method: str = None,
    ):
        """Send a request to the fast api server.

        Args:
            route (APIRoute): The route to use.
            function_args (List[Parameter]): The full set of function argument definitions, that

            args (list): The arguments sent to the function
            kwargs (dict): The argument dict (**kwargs) send to the function
            method (str, optional): Override the request method. Defaults to None.

        Returns:
            Any: The result of the request loaded from json.
        """
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
