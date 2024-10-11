from typing import Type, List, Union, Tuple, Any, Dict

from sqlalchemy import func, Column, text
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Exists

from App.Core.Abstract import AbstractDbDriver
from App.Core.DB import Model
from App.Core.Logger import Log
from App.Core.Utils.Models import Models


class Connection:
    def __init__(self, driver: AbstractDbDriver, log: Log):
        self.__log = log
        self.__driver = driver
        self.__session = Session(self.__driver.engine())
        self.__session.execute(text("PRAGMA foreign_keys=ON;"))

        Models.load_models()

    def driver(self) -> AbstractDbDriver:
        return self.__driver

    def session(self) -> Session:
        return self.__session

    def query(self, model: Type[Model], *entities) -> Query:
        return self.__session.query(model, *entities)

    def save(self, models: List[Model]):
        for model in models:
            self.__session.add(model)

        self.__session.commit()
        self.__session.flush()

    def select(self, model: Type[Model], columns: Tuple[Union[str, Column], ...]) -> Query:
        if columns:
            if isinstance(columns[0], str):
                return self.__session.query(*list(map(lambda x: getattr(model, x), columns)))

        return self.__session.query(*columns)

    def count(self, model: Type[Model], field: Union[str, Column]) -> int:
        if isinstance(field, str):
            field = getattr(model, field)

        return self.__session.query(func.count(field)).scalar()

    @staticmethod
    def update(model: Model, data: dict) -> bool:
        for key, value in data.items():
            setattr(model, key, value)

        model.save()

        return True

    @staticmethod
    def create(model: Type[Model], **kwargs) -> Model:
        if hasattr(model, "id") and (kwargs.get('id') or 0) == 0:
            c_model = model.mro()[0]
            # noinspection PyUnresolvedReferences
            obj = c_model.select("id").order_by(c_model.id.desc()).limit(1).one_or_none()
            kwargs.update({'id': obj.id + 1 if obj else 1})

        obj = model(**kwargs)
        obj.save()

        return obj

    def exists(self, _exists: Exists) -> bool:
        return self.__session.query(_exists).scalar()

    def delete_by(self, model: Type[Model], by: Union[str, Dict[str, Any]], value: Any = None):
        try:
            q = self.__session.query(model)

            if isinstance(by, str):
                by = {by: value}

            for k, v in by.items():
                # noinspection PyTypeChecker
                q = q.filter(getattr(model, k) == v)

            q.delete()

            self.__session.commit()
        except (IntegrityError, DataError) as e:
            self.__log.error(f"Cannot delete by val. {str(e)}")
            return False

    def delete(self, model: Model) -> bool:
        try:
            l_model = model.__class__
            pk = l_model.__primary_key__

            if hasattr(model, pk):
                # noinspection PyTypeChecker
                self.__session.query(l_model).filter(getattr(l_model, pk) == model.__getattribute__(pk)).delete()
            else:
                self.__session.delete(model)

            self.__session.commit()

            return True

        except (IntegrityError, DataError) as e:
            self.__log.error(f"Cannot delete model. {str(e)}")
            return False
