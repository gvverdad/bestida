from configparser import ConfigParser
from fastapi import FastAPI

config = None


def include_me(app: FastAPI, in_config: ConfigParser) -> None:
    global config
    config = in_config
