from configparser import ConfigParser
from fastapi import FastAPI


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include("src.server.jobq")
