from configparser import ConfigParser
from fastapi import FastAPI


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.include("src.api.v1.endpoints.pages.bookmarks")
    app.include("src.api.v1.endpoints.pages.changecompany")
    app.include("src.api.v1.endpoints.pages.changepassword")
    app.include("src.api.v1.endpoints.pages.copycompanydata")
    app.include("src.api.v1.endpoints.pages.database")
    app.include("src.api.v1.endpoints.pages.home")
    app.include("src.api.v1.endpoints.pages.jobqueue")
    app.include("src.api.v1.endpoints.pages.launcher")
    app.include("src.api.v1.endpoints.pages.locale")
    app.include("src.api.v1.endpoints.pages.notifications")
    app.include("src.api.v1.endpoints.pages.profile")
    app.include("src.api.v1.endpoints.pages.purge")
    app.include("src.api.v1.endpoints.pages.release")
    app.include("src.api.v1.endpoints.pages.spooler")
    app.include("src.api.v1.endpoints.pages.timezone")
