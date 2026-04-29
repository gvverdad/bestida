from sqlalchemy import Column, ForeignKey, String, Integer, Text
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import (get_locale_choices, get_timezone_choices,
                         get_theme_choices, get_default_timezone,
                         get_default_locale)


class UserSetting(Model):
    __tablename__ = "UserSettings"
    __table_args__ = dict(info=dict(label="User Settings", desc="Settings"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
                
    Theme = Column(String(16), nullable=False, default="dark",
                   info=dict(label="Theme",
                             choices=get_theme_choices))        # client getter

    Locale = Column(String(8), nullable=False, default=get_default_locale,
                    info=dict(label="Locale",
                              choices=get_locale_choices))      # client getter

    Timezone = Column(String(32), nullable=False, default=get_default_timezone,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices))

    SidebarState = Column(String(16), nullable=False, default="hide",
                          info=dict(label="Sidebar State"))

    MenuState = Column(Text, info=dict(label="Menu State"))

    NavState = Column(Text, info=dict(label="Navigation State"))

    ActivePage = Column(String(256), info=dict(label="Active Page"))

    HomeActivePage = Column(String(256), info=dict(label="Home Active Page"))

    # OneToOne side of User
    ItemUser_Id = Column(Integer, ForeignKey("Users.Id"),
                         info=dict(hidden=True))
    ItemUser = relationship("User", back_populates="Settings",
                            primaryjoin="User.Id==UserSetting.ItemUser_Id")
