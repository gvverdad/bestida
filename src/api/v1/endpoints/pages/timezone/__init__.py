from configparser import ConfigParser
from fastapi import FastAPI

from .timezone import router


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include_router(router)

