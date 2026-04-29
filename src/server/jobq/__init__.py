import multiprocessing, time, datetime
import logging, sys, traceback
from ...db import sqa, db_session, get_engine

from .tasks import task_runner

log = logging.getLogger(__name__)


class JobQProcess(multiprocessing.Process):
    def __init__(self, config, name):
        self.que_name = name
        self.config = config
        super(JobQProcess, self).__init__(name=f'{config["main"]["app"]}_JobQ_{name}')

        q_name = f"jobq_{name}"
        if 'interval' not in config[q_name]:
            self.interval = 10  # 10 seconds
        else:
            if "." in config[q_name]["interval"]:
                self.interval = float(config[q_name]["interval"])
            else:
                self.interval = int(config[q_name]["interval"])

        if 'poolsize' not in config[q_name] or int(config[q_name]["poolsize"]) < 1:
            self.poolsize = multiprocessing.cpu_count()
        else:
            self.poolsize = int(config[q_name]["poolsize"])

    # This function is called when the process is started, thus
    # creating a new child-process of the web-server that runs
    # the JobQ.
    def run(self):
        db_session.configure(bind=get_engine(self.config))

        log.info(f"{self.name} JobQProcess.run Started PoolSize: {self.poolsize}, Sleep: {self.interval}")
        pool = multiprocessing.Pool(processes=self.poolsize)
        try:
            while True:
                try:
                    time.sleep(self.interval)

                    jobs = (db_session.query(sqa.get_model("Tasks")).
                            filter(sqa.where(f"Tasks.Queue = '{self.que_name}' and Tasks.Status in ('Submitted','Waiting')")).
                            order_by(sqa.sort_asc("Tasks", "NextRunDateTime")).all())
                    for j in jobs:
                        if j.NextRunDateTime <= datetime.datetime.utcnow():
                            j.Status = "OnQueue"
                            db_session.add(j)
                            db_session.commit()
                        else:
                            if j.Status != "Waiting":
                                j.Status = "Waiting"
                                db_session.add(j)
                                db_session.commit()

                    jobs = (db_session.query(sqa.get_model("Tasks")).
                            filter(sqa.where(f"Tasks.Queue = '{self.que_name}' and Tasks.Status == 'OnQueue'")).
                            order_by(sqa.sort_asc("Tasks", "NextRunDateTime")).all())

                    for j in jobs:
                        j.Status = "Queued"
                        db_session.add(j)
                        db_session.commit()

                        log.info(f"{self.name} JobQProcess.run taskId: {j.Id}, Status: {j.Status}, RunScript: {j.RunScript}")
                        pool.apply_async(task_runner, (j.Id, self.config))

                except (KeyboardInterrupt, SystemExit):
                    log.info(f"{self.name} JobQProcess.run KeyboardInterrupt, SystemExit")
                    raise
                except EOFError:
                    log.info("{} JobQProcess.run EOFError".format(self.name))
                    break
                except:
                    log.info(f"{self.name} JobQProcess.run Generic Except - see traceback in sys.stderr")
                    traceback.print_exc(file=sys.stderr)
        finally:
            log.info(f"{self.name} JobQProcess.run Stopped")
            # return unprocessed Queued to Waiting
            queued = (db_session.query(sqa.get_model("Tasks")).
                      filter(sqa.where(f"Tasks.Queue = '{self.que_name}' and Tasks.Status == 'Queued'")).
                      all())
            for q in queued:
                q.Status = "Waiting"
                db_session.add(q)
                db_session.commit()

            pool.close()
            pool.terminate()
            pool.join()


def include_me(app, config):
    ques = list()
    for q in config["jobqs"]["keys"].split(","):
        name = q.strip()
        jobq = JobQProcess(config, name)
        if config.getboolean(f"jobq_{name}", "start"):
            jobq.start()
        ques.append(jobq)

    spooler = "/tmp"
    if "location" in config["spooler"]:
        spooler = config["spooler"]["location"]

    work_file = "/tmp"
    if "location" in config["workfile"]:
        work_file = config["workfile"]["location"]

    log.info("*" * 80)
    for q in ques:
        log.info(f"Initiated Jobq: {q}  pid: {q.pid}")
    log.info(f"Spooler in: {spooler}")
    log.info(f"Workfiles in: {work_file}")
