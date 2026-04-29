from . import system


def include_me(app, config):
    app.include_router(system.router)
