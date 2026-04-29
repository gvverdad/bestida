from configparser import ConfigParser
from fastapi import FastAPI

from .security import router


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include_router(router)

