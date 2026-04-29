import hashlib
from pathlib import Path
from configparser import ConfigParser
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from millify import millify

from ..utils.locales import locale_time_format, locale_datetime_format, locale_date_format
from ..db import sqa, db_session

templates = None


class SecureJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str):
        super().__init__(directory)

        self.directory = directory

    def TemplateResponse(self, name: str, *args, **kwargs):
        template_path = Path(self.directory) / name

        with open(template_path, "r", encoding="utf-8") as template_file:
            raw_content = template_file.read()
        checksum = hashlib.sha256(raw_content.encode()).hexdigest()

        template = (db_session.query(sqa.get_model("Templates")).
                    filter(sqa.where(f"File = '{name}'")).
                    first())
        if template is None:
            template = sqa.get_model("Templates")()
            template.File = name
            template.Checksum = checksum
            db_session.add(template)
            db_session.commit()
        elif checksum != template.Checksum:
            raise HTTPException(status_code=500,
                                detail=f"Template checksum verification failed: {name}")

        return super().TemplateResponse(name, *args, **kwargs)


def include_me(app: FastAPI, config: ConfigParser) -> None:
    global templates

    templates = SecureJinja2Templates(directory=f'{config["templates"]["location"]}/frontend')
    templates.env.filters['date_format'] = locale_date_format
    templates.env.filters['time_format'] = locale_time_format
    templates.env.filters['datetime_format'] = locale_datetime_format
    templates.env.filters['millify'] = millify

    templates.env.globals["APP_TITLE"] = config["main"]["title"]
    templates.env.globals["APP_HOMEPAGE"] = config["main"]["app_homepage"]
