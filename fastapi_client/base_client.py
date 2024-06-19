import asyncio
import inspect
from abc import abstractmethod
from typing import List, Union
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable
from fastapi_client.exceptions import FastAPIClientError


class FastAPIClientBase:
    """Abstract class for holding configuration for the api
    client
    """

    __active_client_stack: List["FastAPIClientBase"] = []
    """The active client stack (Thread unsafe!)"""

    @classmethod
    def get_active_client(cls):
        """Returns the current active client when using with"""
        if len(cls.__active_client_stack) == 0:
            return None
        return cls.__active_client_stack[-1]

    @abstractmethod
    def send(
        route: APIRoute,
        params: List[inspect.Parameter],
        args: list,
        kwargs: dict,
    ):
        pass

    @abstractmethod
    async def send_async(
        route: APIRoute,
        params: List[inspect.Parameter],
        args: list,
        kwargs: dict,
    ):
        pass

    @classmethod
    def create_client_decorator(cls, func: DecoratedCallable, route: APIRoute):
        # Should be an ordered dictionary
        function_args = list(inspect.signature(func).parameters.values())

        if asyncio.iscoroutinefunction(func):

            async def async_client_wrapper(*args, **kwargs):
                client: "FastAPIClientBase" = FastAPIClientBase.get_active_client()
                if client:
                    return await client.send_async(
                        route,
                        function_args,
                        args,
                        kwargs,
                    )
                else:
                    return await func(*args, **kwargs)

            return async_client_wrapper
        else:

            def client_wrapper(*args, **kwargs):
                client: "FastAPIClientBase" = FastAPIClientBase.get_active_client()
                if client:
                    return client.send(
                        route,
                        function_args,
                        args,
                        kwargs,
                    )
                else:
                    return func(*args, **kwargs)

            return client_wrapper

    @classmethod
    def enable(cls, router: Union[FastAPI, APIRouter]):
        if isinstance(router, FastAPI):
            router = router.router

        # Bind and override
        api_route = router.api_route

        def api_route_override(*args, **kwargs):
            api_route_decorator = api_route(*args, **kwargs)

            def client_decorator(func: DecoratedCallable):
                # Invoke the internal route decorator, to add the route
                api_route_decorator(func)

                # Create the decorator, routes[-1] is the last route added
                return cls.create_client_decorator(func, router.routes[-1])

            return client_decorator

        router.api_route = api_route_override

    def __enter__(self):
        """Calls when enters with"""
        self.__active_client_stack.append(self)

    def __exit__(self, *args, **kwargs):
        """Called when exits with"""
        if len(self.__active_client_stack) != 1:
            raise FastAPIClientError(
                "Cannot find an active fast api, cannot properly exist 'with' call"
            )
        if self.__active_client_stack[-1] != self:
            raise FastAPIClientError(
                "Cannot __exit__ the current fast api client with call,"
                + " another client is already active (another 'with')"
            )
        try:
            self.__active_client_stack.pop(-1)
        except IndexError as ex:
            raise FastAPIClientError(
                "Failed to properly exit the fast api with call, failed to delete current from stack"
            ) from ex
