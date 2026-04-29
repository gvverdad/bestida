import abc, logging, ast, os, tempfile
from uuid import uuid4
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from importlib import import_module
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

import pdfkit
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from sqlalchemy.orm.session import make_transient
from millify import millify
import pyexcel
from jinja2 import Environment, PackageLoader

from ...db import sqa, db_session
from ...utils.locales import locale_time_format, locale_datetime_format, locale_date_format
from ...utils.json import recursive_json_loads
from ...config import config

log = logging.getLogger(__name__)

def get_filename():
    return str(uuid4())

def get_image_filename(settings):
    spool_file = "/tmp"
    if "location" in settings["image"]:
        spool_file = settings["image"]["location"]
    return os.path.join(spool_file, f"img{get_filename()}")

def get_spool_filename(settings):
    spool_file = "/tmp"
    if "location" in settings["spooler"]:
        spool_file = settings["spooler"]["location"]
    return os.path.join(spool_file, f"spl{get_filename()}")

def get_work_filename(settings):
    work_file = "/tmp"
    if "location" in settings["workfile"]:
        work_file = settings["workfile"]["location"]
    return os.path.join(work_file, f"wrk{get_filename()}")

def task_runner(task_id, settings):
    task = db_session.query(sqa.get_model("Tasks")).get(task_id)

    user_id = task.CreateOpId.Id
    task_name = f"src.{task.RunScript}"

    task.Status = "Running"
    task.StartRunTime = datetime.utcnow()
    task.EndRunTime = None
    task.RunTime = None
    db_session.add(task)
    db_session.commit()

    log.info(f"Start taskId: {task_id}, runScript: {task_name}")
    try:
        mod, cls = task_name.rsplit(".", 1)
        # tasks.system.import.doimporttables.ImportTables
        # module = tasks.system.import.doimporttables
        # class = ImportTables
        job = getattr(import_module(mod), cls)(task_id, user_id, settings)
        spool_files, is_conditional = job.run()
        log.info(f"Done taskId: {task_id}, spool_files: {spool_files}, conditional: {is_conditional}")

        task = db_session.query(sqa.get_model("Tasks")).get(task_id)
        if task:
            task.Status = "Done"
            task.EndRunTime = datetime.utcnow()
            delta = task.EndRunTime - task.StartRunTime
            duration_in_s = delta.total_seconds()
            days = divmod(duration_in_s, 86400)  # Get days (without [0]!)
            hours = divmod(days[1], 3600)  # Use remainder of days to calc hours
            minutes = divmod(hours[1], 60)  # Use remainder of hours to calc minutes
            seconds = divmod(minutes[1], 1)  # Use remainder of minutes to calc seconds
            task.RunTime = "{:.0f}:{:.0f}:{:.0f}:{:.0f}".format(days[0], hours[0], minutes[0], seconds[0])
            db_session.add(task)

            notification = sqa.get_model("Notifications")()
            notification.User = task.User
            notification.Title = "JobQ Task Completion"
            notification.SpoolTitle = task.Title
            notification.SpoolFile = spool_files[0]
            notification.Text = f"Task {task.Title} of Company {task.Company.CompanyId} completed in {task.RunTime}"
            if is_conditional:
                notification.Text += " CONDITIONAL"
            db_session.add(notification)
            
            if task.Device.Type == "spooler":
                for spl in spool_files:
                    spool = sqa.get_model("Spoolers")()
                    spool.Company = task.Company
                    spool.Program = task.Program
                    spool.User = task.User
                    spool.RunScript = task.RunScript
                    spool.Title = task.Title
                    spool.File = spl
                    spool.Document = task.Document
                    spool.ExpiryDate = datetime.utcnow() + relativedelta(days=task.KeepDays)
                    db_session.add(spool)

            if task.Notify == "Always" or \
                    (task.Notify == "Conditional" and is_conditional):

                from_address = settings["email"]["default_sender"].strip()
                to_address = task.Email.strip()

                if not from_address or not to_address:
                    log.warning(f"Email NOT Sent taskId: {task_id}, Task {task.Title}, From Address: {from_address}, To Address: {to_address}")
                else:
                    message = job.get_notify_message()
                    if message is None:
                        message = MIMEMultipart()

                    message["From"] = from_address
                    message["To"] = to_address

                    # task.EmailCC is optional, catchall strip spaces
                    cc_address = task.EmailCC.strip()
                    if cc_address:
                        message["Cc"] = cc_address

                    # task.EmailBCC is optional, catchall strip spaces
                    bcc_address = task.EmailBCC.strip()
                    if bcc_address:
                        message["Bcc"] = bcc_address

                    subject = task.EmailSubject.strip()
                    if task.Params:
                        try:
                            params = recursive_json_loads(task.Params)  # convert string to dict
                        except:
                            params = ast.literal_eval(task.Params)  # convert string to dict
                        if params:
                            body = "<p>Parameters:</p><br/><ul>"
                            for k, v in params.items():
                                body += f"<li>{k}: {v}</li>"
                            body += "</ul>"
                        else:
                            body = "<p>No Parameters</p>"
                    else:
                        body = "<p>No Parameters</p>"
                    message.attach(MIMEText(body, 'html'))

                    if subject:
                        message["Subject"] = subject
                    else:
                        message["Subject"] = task.Title

                    receipt = cc_address.split(",") + bcc_address.split(",") + to_address.split(",")

                    email_server = smtplib.SMTP(host=settings["email"]["host"], port=settings["email"]["port"])
                    email_server.ehlo()
                    email_server.starttls()
                    email_server.login(settings["email"]["username"], settings["email"]["password"])
                    email_server.sendmail(from_address, receipt, message.as_string())
                    email_server.quit()

                    if task.Notify == "Conditional":
                        log.info(f"Email Sent Conditional taskId: {task_id}, Task {task.Title}: {message}")
                    else:
                        log.info(f"Email Sent taskId: {task_id}, Task {task.Title}: {message}")

            if task and task.ScheduleType != "Once":
                # make a copy of task
                make_transient(task)
                task.Id = None
                task.Status = "Submitted"
                task.StartRunTime = None
                task.EndRunTime = None
                task.RunTime = None
                # new schedule
                run_datetime = task.NextRunDateTime
                if task.ScheduleType == "Minute":
                    next_date = run_datetime + relativedelta(minutes=task.MinuteValue)
                    if task.StartTime is not None and task.EndTime is not None:
                        if next_date.time() < task.StartTime:
                            next_date = next_date.replace(hour=task.StartTime.hour,
                                                          minute=task.StartTime.minute,
                                                          second=task.StartTime.second)
                        elif next_date.time() > task.EndTime:
                            next_date = next_date + relativedelta(days=1)
                            next_date = next_date.replace(hour=task.StartTime.hour,
                                                          minute=task.StartTime.minute,
                                                          second=task.StartTime.second)
                    if task.WeekdaysOnly:
                        week_no = next_date.weekday()
                        if week_no < 5:  # 5 Sat, 6 Sun
                            task.NextRunDateTime = next_date
                        else:
                            task.NextRunDateTime = next_date + relativedelta(days=7-week_no)
                    else:
                        task.NextRunDateTime = next_date
                elif task.ScheduleType == "Hourly":
                    next_date = run_datetime + relativedelta(hours=task.HourlyValue)
                    if task.StartTime is not None and task.EndTime is not None:
                        if next_date.time() < task.StartTime:
                            next_date = next_date.replace(hour=task.StartTime.hour,
                                                          minute=task.StartTime.minute,
                                                          second=task.StartTime.second)
                        elif next_date.time() > task.EndTime:
                            next_date = next_date + relativedelta(days=1)
                            next_date = next_date.replace(hour=task.StartTime.hour,
                                                          minute=task.StartTime.minute,
                                                          second=task.StartTime.second)
                    if task.WeekdaysOnly:
                        week_no = next_date.weekday()
                        if week_no < 5:  # 5 Sat, 6 Sun
                            task.NextRunDateTime = next_date
                        else:
                            task.NextRunDateTime = next_date + relativedelta(days=7-week_no)
                    else:
                        task.NextRunDateTime = next_date
                elif task.ScheduleType == "Daily":
                    next_date = run_datetime + relativedelta(days=task.DailyValue)
                    if task.WeekdaysOnly:
                        week_no = next_date.weekday()
                        if week_no < 5:  # 5 Sat, 6 Sun
                            task.NextRunDateTime = next_date
                        else:
                            task.NextRunDateTime = next_date + relativedelta(days=7-week_no)
                    else:
                        task.NextRunDateTime = next_date
                elif task.ScheduleType == "Weekly":
                    task.NextRunDateTime = run_datetime + relativedelta(weeks=task.WeeklyValue)
                elif task.ScheduleType == "Monthly":
                    task.NextRunDateTime = run_datetime + relativedelta(months=int(task.MonthlyValue))
                elif task.ScheduleType == "Yearly":
                    task.NextRunDateTime = run_datetime + relativedelta(years=task.YearlyValue)
                elif task.ScheduleType == "Others":
                    if task.OtherValue == "Every Last Day of Month":
                        # https://gist.github.com/waynemoore/1109153
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1)
                    elif task.OtherValue == "Every First Monday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=MO)
                    elif task.OtherValue == "Every First Tuesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TU)
                    elif task.OtherValue == "Every First Wednesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=WE)
                    elif task.OtherValue == "Every First Thursday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TH)
                    elif task.OtherValue == "Every First Friday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=FR)
                    elif task.OtherValue == "Every First Saturday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SA)
                    elif task.OtherValue == "Every First Sunday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SU)
                    elif task.OtherValue == "Every Last Monday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=MO(-1))
                    elif task.OtherValue == "Every Last Tuesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=TU(-1))
                    elif task.OtherValue == "Every Last Wednesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=WE(-1))
                    elif task.OtherValue == "Every Last Thursday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=TH(-1))
                    elif task.OtherValue == "Every Last Friday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=FR(-1))
                    elif task.OtherValue == "Every Last Saturday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=SA(-1))
                    elif task.OtherValue == "Every Last Sunday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+2, days=-1, weekday=SU(-1))
                    elif task.OtherValue == "Every Second Monday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=MO(+2))
                    elif task.OtherValue == "Every Second Tuesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TU(+2))
                    elif task.OtherValue == "Every Second Wednesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=WE(+2))
                    elif task.OtherValue == "Every Second Thursday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TH(+2))
                    elif task.OtherValue == "Every Second Friday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=FR(+2))
                    elif task.OtherValue == "Every Second Saturday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SA(+2))
                    elif task.OtherValue == "Every Second Sunday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SU(+2))
                    elif task.OtherValue == "Every Third Monday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=MO(+3))
                    elif task.OtherValue == "Every Third Tuesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TU(+3))
                    elif task.OtherValue == "Every Third Wednesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=WE(+3))
                    elif task.OtherValue == "Every Third Thursday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TH(+3))
                    elif task.OtherValue == "Every Third Friday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=FR(+3))
                    elif task.OtherValue == "Every Third Saturday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SA(+3))
                    elif task.OtherValue == "Every Third Sunday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SU(+3))
                    elif task.OtherValue == "Every Fourth Monday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=MO(+4))
                    elif task.OtherValue == "Every Fourth Tuesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TU(+4))
                    elif task.OtherValue == "Every Fourth Wednesday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=WE(+4))
                    elif task.OtherValue == "Every Fourth Thursday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=TH(+4))
                    elif task.OtherValue == "Every Fourth Friday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=FR(+4))
                    elif task.OtherValue == "Every Fourth Saturday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SA(+4))
                    elif task.OtherValue == "Every Fourth Sunday of Month":
                        task.NextRunDateTime = run_datetime + relativedelta(day=1, months=+1, weekday=SU(+4))

                db_session.add(task)

            db_session.commit()

    except Exception as err:
        db_session.rollback()
        log.warning(f"Error taskId: {task_id}, runScript: {task_name}, server.jobq.tasks.task_runner Exception: {str(err)}")


class TaskRunner(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, task_id, user_id, settings):
        self.db_session = db_session
        self.jinja2Env = Environment(loader=PackageLoader("src", 'templates'))
        self.jinja2Env.filters['date_format'] = locale_date_format
        self.jinja2Env.filters['time_format'] = locale_time_format
        self.jinja2Env.filters['datetime_format'] = locale_datetime_format
        self.jinja2Env.filters['millify'] = millify

        self.user = db_session.query(sqa.get_model("Users")).get(user_id)
        self.jinja2Env.globals['USER'] = self.user
        self.jinja2Env.globals['TEMPLATE_LOCATION'] = config["templates"]["location"]

        self.output_files = []
        self.is_conditional = False

        self.settings = settings
        self.task = db_session.query(sqa.get_model("Tasks")).get(task_id)
        self.output_type = self.task.Document.Type

        # 3.8 json.loads cannot recursively convert string to native python datatype
        if self.task.Params:
            try:
                self.params = recursive_json_loads(self.task.Params)  # convert string to dict
            except:
                # literal_eval cannot convert json specific datatypes ie: null,true,false...
                self.params = ast.literal_eval(self.task.Params)  # convert string to dict
        else:
            self.params = None

        try:
            self.session = recursive_json_loads(self.task.Session)  # convert string to dict
        except:
            self.session = ast.literal_eval(self.task.Session)  # convert string to dict

        self.context = dict()
        self.context["company"] = self.task.Company.Name
        self.context["opId"] = self.task.CreateOpId.UserId
        self.context["runDateTime"] = datetime.utcnow()
        self.context["locale"] = self.session["locale"]
        self.context["timezone"] = self.session["timezone"]
        self.context["title"] = self.task.Title
        self.context["progId"] = self.__class__.__name__

        self.context["data_row"] = list()

    def render_template(self, template, context):
        return self.jinja2Env.get_template(template).render(context)

    @abc.abstractmethod
    def run(self):
        """
        task run method
        :return: (self.output_files, self.is_conditional)
        """
        return

    @abc.abstractmethod
    def get_notify_message(self, spool_filename, attach_filename):
        """
        this method should be run by child objects
        ie:
            def get_notify_message(self):
                return super(PurgeNotifications, self).get_notify_message(self.output_files[0], 'PurgeNotifications.pdf')

        :return:
        """
        message = MIMEMultipart()
        with open(spool_filename, 'rb') as attach_file:
            attachment = attach_file.read()
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload(attachment)
        # enconding the binary into base64
        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition', 'attachment', filename=attach_filename)
        message.attach(payload)

        return message

    def render_txt(self):
        raise Exception("render_txt - in TODO list")

    def render_pdf(self,
                   header_template="reports/pdf/header.jinja2",
                   body_template="reports/pdf/body.jinja2",
                   footer_template="reports/pdf/footer.jinja2",
                   orientation="Portrait",  # Landscape or Portrait
                   page_size="A4"
                   ):

        pdf_options = {"quiet": "",
                       # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2660
                       "enable-local-file-access": "",
                       "orientation": orientation,
                       "page-size": page_size
                       }

        try:
            with tempfile.NamedTemporaryFile(mode="w+", suffix='.html', delete=False) as header_html:
                pdf_options['header-html'] = header_html.name
                header_html.write(self.render_template(header_template, self.context))

            with tempfile.NamedTemporaryFile(mode="w+", suffix='.html', delete=False) as footer_html:
                pdf_options['footer-html'] = footer_html.name
                footer_html.write(self.render_template(footer_template, self.context))

            body = self.render_template(body_template, self.context)
            pdfkit.from_string(body, self.output_files[0], options=pdf_options)
        finally:
            # Ensure temporary file is deleted after finishing work
            os.remove(pdf_options['header-html'])
            os.remove(pdf_options['footer-html'])

    def render_csv(self):
        self._render_spreadsheet()

    def render_xls(self):
        self._render_spreadsheet()

    def render_xlsx(self):
        self._render_spreadsheet()

    def render_ods(self):
        # don't use ods - pyexcel_ods
        # getting AttributeError: 'decimal.Decimal' object has no attribute 'split'
        #self._render_spreadsheet()
        raise Exception("Don't use ods - pyexcel_ods AttributeError: 'decimal.Decimal' object has no attribute 'split'")

    def _render_spreadsheet(self):
        # self.context["data_row"] should be a list of OrderedDict
        # self.output_files[0] should have file extension of: csv or xls or xlsx or ods
        # don't use ods - pyexcel_ods getting AttributeError: 'decimal.Decimal' object has no attribute 'split'
        try:
            pyexcel.isave_as(records=self.context["data_row"],
                             dest_file_name=self.output_files[0])
        finally:
            pyexcel.free_resources()
        """
        pyexcel.free_resources()
        Close file handles opened by signature functions that starts with ‘i’ ie: isave
        for csv, csvz file formats, file handles will be left open. 
        for xls, ods file formats, the file is read all into memory and is close afterwards. 
        for xlsx, file handles will be left open in python 2.7 - 3.5 
            by pyexcel-xlsx(openpyxl). 
        In other words, pyexcel-xls, pyexcel-ods, pyexcel-ods3 won’t leak file handles.    
        """
