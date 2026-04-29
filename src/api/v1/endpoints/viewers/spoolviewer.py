import logging, os

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from src.config import config
from src.db import sqa
from src.db.models.security.Users import User as DBUser
from src.services import templates
from src.security.policy import get_current_user

log = logging.getLogger(__name__)

router = APIRouter()

# FastAPI allows you to specify a path parameter that can include slashes by using the :path parameter type.
# ie: /spoolviewer/Purge%201%20Day%20Jobs/%2Fhome%2Fgvv%2FProjects%2Fgvv%2Fspool%2Fspl202407180300656187.pdf
@router.get("/spoolviewer/{title}/{file:path}", response_class=HTMLResponse, tags=["viewers"])
def spool_viewer_page(request: Request,
                      title: str,
                      file: str,
                      current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    _, ext = os.path.splitext(file)
    filename = os.path.basename(file)
    file = f"{config['spooler']['public']}/{filename}"
    context = dict(request=request, title=title, file=file,
                   filename=filename, fileext=ext)

    return templates.TemplateResponse("viewers/fileviewer.html", context)
