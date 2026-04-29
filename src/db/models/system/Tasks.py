from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, Boolean,
                        DateTime, Time, Enum, Text, Index)
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import get_queue_choices
from ....security.policy import get_current_uid
from ..functions import get_spool_keep_days

class Task(Model):
    __tablename__ = "Tasks"
    __table_args__ = dict(info=dict(label="Tasks", companyField="Company_Id"))

    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", selectId="Id",
                                  selectKey="Name",
                                  selectGetter="/getCompaniesList"))
    Company = relationship("Company", primaryjoin="Company.Id==Task.Company_Id")

    # Many2One
    Role_Id = Column(Integer, ForeignKey("Roles.Id"), nullable=False,
                     info=dict(label="Role", selectId="Id", selectKey="Role"))
    Role = relationship("Role", primaryjoin="Role.Id==Task.Role_Id")

    # Many2One
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id",
                                  selectKey="Name"))
    Program = relationship("Program", primaryjoin="Program.Id==Task.Program_Id")

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                     info=dict(label="User", selectId="Id", selectKey="UserId"))
    User = relationship("User", primaryjoin="User.Id==Task.User_Id")

    RunScript = Column(String(4096), nullable=False, info=dict(label="Run Script"))

    Title = Column(String(128), nullable=False, info=dict(label="Title"))

    Params = Column(Text, info=dict(label="Params"))

    Queue = Column(String(16), nullable=False,
                   info=dict(label="Queue",
                             choices=get_queue_choices,        # server getter
                             choices_getter="getQueuesList"))  # client getter

    # Many2One
    Device_Id = Column(Integer, ForeignKey("Devices.Id"), nullable=False,
                       info=dict(label="Send to Device",
                                 selectId="Id", selectKey="Device"))
    Device = relationship("Device", primaryjoin="Device.Id==Task.Device_Id")

    KeepDays = Column(Integer, nullable=False, default=get_spool_keep_days,
                      info=dict(label="Spool Keep Days"))

    # Many2One
    Document_Id = Column(Integer, ForeignKey("Documents.Id"), nullable=False,
                         info=dict(label="Document Type",
                                   selectId="Id", selectKey="Document"))
    Document = relationship("Document",
                            primaryjoin="Document.Id==Task.Document_Id")

    NextRunDateTime = Column(DateTime, nullable=False,
                             info=dict(label="Run DateTime"))

    ScheduleType = Column(Enum("Once", "Minute", "Hourly", "Daily", "Weekly", "Monthly", "Yearly", "Others",
                               name="Tasks_ScheduleType"),
                          nullable=False, default="Once",
                          info=dict(label="Run Type",
                                    actionOn="{" +
                                             "\"baseFieldName\": \"ScheduleType\"," +
                                             "\"Once\": {\"onFields\":[]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"DailyValue\",\"WeeklyValue\",\"MonthlyValue\",\"YearlyValue\",\"OtherValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]}," +
                                             "\"Minute\": {\"onFields\":[\"MinuteValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]," +
                                             "\"offFields\":[\"HourlyValue\",\"DailyValue\",\"WeeklyValue\",\"MonthlyValue\",\"YearlyValue\",\"OtherValue\"]}," +
                                             "\"Hourly\": {\"onFields\":[\"HourlyValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]," +
                                             "\"offFields\":[\"MinuteValue\",\"DailyValue\",\"WeeklyValue\",\"MonthlyValue\",\"YearlyValue\",\"OtherValue\"]}," +
                                             "\"Daily\": {\"onFields\":[\"DailyValue\",\"WeekdaysOnly\"]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"WeeklyValue\",\"MonthlyValue\",\"YearlyValue\",\"OtherValue\",\"StartTime\",\"EndTime\"]}," +
                                             "\"Weekly\": {\"onFields\":[\"WeeklyValue\"]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"DailyValue\",\"MonthlyValue\",\"YearlyValue\",\"OtherValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]}," +
                                             "\"Monthly\": {\"onFields\":[\"MonthlyValue\",]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"DailyValue\",\"WeeklyValue\",\"YearlyValue\",\"OtherValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]}," +
                                             "\"Yearly\": {\"onFields\":[\"YearlyValue\"]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"DailyValue\",\"WeeklyValue\",\"MonthlyValue\",\"OtherValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]}," +
                                             "\"Others\": {\"onFields\":[\"OtherValue\"]," +
                                             "\"offFields\":[\"MinuteValue\",\"HourlyValue\",\"DailyValue\",\"WeeklyValue\",\"MonthlyValue\",\"YearlyValue\",\"StartTime\",\"EndTime\",\"WeekdaysOnly\"]}" +
                                             "}"
                                    ))
    MinuteValue = Column(Integer, info=dict(label="Minute Frequency",
                                            requiredIf="ScheduleType == \"Minute\""))
    HourlyValue = Column(Integer, info=dict(label="Hourly Frequency",
                                            requiredIf="ScheduleType == \"Hourly\""))
    DailyValue = Column(Integer, info=dict(label="Daily Frequency",
                                           requiredIf="ScheduleType == \"Daily\""))
    WeeklyValue = Column(Integer, info=dict(label="Weekly Frequency",
                                            requiredIf="ScheduleType == \"Weekly\""))
    MonthlyValue = Column(Integer, info=dict(label="Monthly Frequency",
                                             requiredIf="ScheduleType == \"Monthly\""))
    YearlyValue = Column(Integer, info=dict(label="Yearly Frequency",
                                            requiredIf="ScheduleType == \"Yearly\""))
    StartTime = Column(Time, default=None,
                       info=dict(label="Start Time",
                                 requiredIf="ScheduleType in (\"Minute\",\"Hourly\")"))
    EndTime = Column(Time, default=None,
                     info=dict(label="End Time",
                               requiredIf="ScheduleType in (\"Minute\",\"Hourly\")"))
    WeekdaysOnly = Column(Boolean, default=False,
                          info=dict(label="Run Weekdays Only"))
    OtherValue = Column(Enum("Every Last Day of Month",
                             "Every First Monday of Month",
                             "Every First Tuesday of Month",
                             "Every First Wednesday of Month",
                             "Every First Thursday of Month",
                             "Every First Friday of Month",
                             "Every First Saturday of Month",
                             "Every First Sunday of Month",
                             "Every Last Monday of Month",
                             "Every Last Tuesday of Month",
                             "Every Last Wednesday of Month",
                             "Every Last Thursday of Month",
                             "Every Last Friday of Month",
                             "Every Last Saturday of Month",
                             "Every Last Sunday of Month",
                             "Every Second Monday of Month",
                             "Every Second Tuesday of Month",
                             "Every Second Wednesday of Month",
                             "Every Second Thursday of Month",
                             "Every Second Friday of Month",
                             "Every Second Saturday of Month",
                             "Every Second Sunday of Month",
                             "Every Third Monday of Month",
                             "Every Third Tuesday of Month",
                             "Every Third Wednesday of Month",
                             "Every Third Thursday of Month",
                             "Every Third Friday of Month",
                             "Every Third Saturday of Month",
                             "Every Third Sunday of Month",
                             "Every Fourth Monday of Month",
                             "Every Fourth Tuesday of Month",
                             "Every Fourth Wednesday of Month",
                             "Every Fourth Thursday of Month",
                             "Every Fourth Friday of Month",
                             "Every Fourth Saturday of Month",
                             "Every Fourth Sunday of Month",
                             name="Tasks_OtherValue"),
                        nullable=False, default="Every Last Day of Month",
                        info=dict(label="Other Frequency",
                                  requiredIf="ScheduleType == \"Others\""))

    Notify = Column(Enum("Never", "Always", "Conditional",
                         name="Tasks_Notify"),
                    nullable=False, default="Never",
                    info=dict(label="Email When Done",
                              actionOn="{" +
                                       "\"baseFieldName\": \"Notify\"," +
                                       "\"Never\": {\"onFields\":[],\"offFields\":[\"Email\",\"EmailCC\",\"EmailBCC\",\"EmailSubject\"]}," +
                                       "\"Always\": {\"onFields\": [\"Email\",\"EmailCC\",\"EmailBCC\",\"EmailSubject\"], \"offFields\": []}," +
                                       "\"Conditional\": {\"onFields\": [\"Email\",\"EmailCC\",\"EmailBCC\",\"EmailSubject\"], \"offFields\": []}" +
                                       "}"
                              ))
    Email = Column(Text, nullable=False,
                   info=dict(label="List of Emails",
                             requiredIf="Notify in (\"Always\",\"Conditional\")",
                             validator=["Email"]))
    EmailCC = Column(Text, info=dict(label="List of CC Emails",
                                     validator=["Email"]))
    EmailBCC = Column(Text, info=dict(label="List of BCC Emails",
                                      validator=["Email"]))

    # RFC 2822 - max of 78 characters
    EmailSubject = Column(String(78), info=dict(label="Email Subject",
                                                requiredIf="Notify in (\"Always\",\"Conditional\")",
                                                ))

    Status = Column(Enum("Submitted", "Waiting", "OnQueue", "Queued", "Running",
                         "Done", name="Tasks_Status"),
                    nullable=False, default="Submitted",
                    info=dict(label="Status"))

    Session = Column(Text, info=dict(label="Session"))

    StartRunTime = Column(DateTime, info=dict(label="Start RunTime",
                                              modifiable=False))

    EndRunTime = Column(DateTime, info=dict(label="End RunTime",
                                            modifiable=False))

    RunTime = Column(String(24), info=dict(label="RunTime", modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Task.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Task.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))


Index("Task_Index1", Task.Company_Id, Task.Role_Id, Task.Program_Id,
      Task.User_Id, unique=False)
Index("Task_Index2", Task.Company_Id, Task.User_Id, Task.NextRunDateTime,
      Task.Status, unique=False)
Index("Task_Index3", Task.Status, Task.NextRunDateTime, unique=False)
Index("Task_Index5", Task.Company_Id, Task.Role_Id, unique=False)
Index("Task_Index6", Task.NextRunDateTime, unique=False)
Index("Task_Index7", Task.Queue, unique=False)
