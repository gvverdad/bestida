from configparser import ConfigParser
from fastapi import FastAPI


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include("src.api.v1.endpoints.app.stocks.products.stocks")
