from configparser import ConfigParser
from fastapi import FastAPI


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include("src.api.v1.endpoints.pages.purge.jobqueue")
    app.include("src.api.v1.endpoints.pages.purge.notification")
    app.include("src.api.v1.endpoints.pages.purge.spooler")
    app.include("src.api.v1.endpoints.pages.purge.workfiles")
