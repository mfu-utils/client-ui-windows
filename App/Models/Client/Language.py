from App.Core.DB import Model
from App.Core.DB.Columns import Varchar, Auto
from App.helpers import lc


class Language(Model):
    __titles__: dict = lc("convertorLangs")
    __tablename__ = 'languages'

    id = Auto().col

    name = Varchar(31, unique=True, nullable=False).col

    @property
    def title(self) -> str:
        return self.__titles__[str(self.name)]
