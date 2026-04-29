import datetime, logging
from dateutil.relativedelta import relativedelta

from ....db import sqa
from ....utils.locales import locale_datetime_format
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)


class PurgeSpool(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(PurgeSpool, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["title"] = "Purge Spools : " + self.task.Title
        self.context["progId"] = __name__

        number_of_days = int(self.params["days"])
        cut_off_date = datetime.datetime.utcnow() - relativedelta(days=number_of_days)

        records = self.db_session.query(sqa.get_model("Spoolers")).with_for_update(). \
            filter(sqa.where("ExpiryDate < {:%Y-%m-%d %H:%M:%S}".format(cut_off_date))).\
            all()

        number_of_records = 0
        if records:
            number_of_records = len(records)
            for r in records:
                self.db_session.delete(r)
            self.db_session.commit()

        self.context["data_row"] = [f"Retain Days: {number_of_days}",
                                    f"Cut-off Date: {locale_datetime_format(cut_off_date, self.session['locale'],self.session['timezone'])}",
                                    f"Number of records purged: {number_of_records}"]

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")

        self.render_pdf()

        return self.output_files, self.is_conditional

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(PurgeSpool, self).get_notify_message(self.output_files[0], 'PurgeJobs.pdf')
