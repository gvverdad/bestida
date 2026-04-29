import datetime, logging, os
from dateutil.relativedelta import relativedelta

from ....config import config
from ....utils.locales import locale_datetime_format
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)


class PurgeWorkfile(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(PurgeWorkfile, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["title"] = "Purge Workfiles : " + self.task.Title
        self.context["progId"] = __name__

        number_of_days = int(self.params["days"])
        cut_off_date = datetime.datetime.utcnow() - relativedelta(days=number_of_days)

        number_of_deleted_files = 0
        for filename in os.listdir(config["workfile"]["location"]):
            if filename == ".empty":
                # ignore dummy .empty file
                continue

            f = os.path.join(config["workfile"]["location"], filename)
            if os.path.isfile(f):
                if os.path.getmtime(f) < cut_off_date.timestamp():
                    number_of_deleted_files += 1
                    os.remove(f)

        self.context["data_row"] = [f"Retain Days: {number_of_days}",
                                    f"Cut-off Date: {locale_datetime_format(cut_off_date,self.session['locale'],self.session['timezone'])}",
                                    f"Location: {config['workfile']['location']}",
                                    f"Number of files purged: {number_of_deleted_files}"]

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")

        self.render_pdf()

        return self.output_files, self.is_conditional

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(PurgeWorkfile, self).get_notify_message(self.output_files[0], 'PurgeJobs.pdf')
