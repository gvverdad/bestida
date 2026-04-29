from . import imageviewer
from . import spoolviewer


def include_me(app, config):
    app.include_router(imageviewer.router)
    app.include_router(spoolviewer.router)
