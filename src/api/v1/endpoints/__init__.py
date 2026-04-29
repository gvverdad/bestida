from configparser import ConfigParser
from fastapi import FastAPI


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include("src.api.v1.endpoints.app")
    app.include("src.api.v1.endpoints.companies")
    app.include("src.api.v1.endpoints.datasource")
    app.include("src.api.v1.endpoints.form")
    app.include("src.api.v1.endpoints.grid")
    app.include("src.api.v1.endpoints.menu")
    app.include("src.api.v1.endpoints.model")
    app.include("src.api.v1.endpoints.pages")
    app.include("src.api.v1.endpoints.script")
    app.include("src.api.v1.endpoints.security")
    app.include("src.api.v1.endpoints.system")
    app.include("src.api.v1.endpoints.viewers")
