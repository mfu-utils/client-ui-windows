from abc import ABC
from typing import List, Type, Optional, Dict, Any

from sqlalchemy import exists

from App.Core.DB import Model

from App.helpers import logger


class AbstractListService(ABC):
    __type__: Type[Model] = Model

    @classmethod
    def all(cls) -> List[__type__]:
        return cls.__type__.query().all()

    @classmethod
    def reversed(cls) -> List[__type__]:
        return cls.__type__.query().order_by(getattr(cls.__type__, cls.__type__.__primary_key__).desc()).all()

    @classmethod
    def for_select(cls, nullable: Optional[str] = None) -> dict:
        params: Dict[Optional[str], Any] = {}

        if nullable:
            params.update({None: nullable})

        params.update(dict(map(lambda x: (str(x.id), x.name), cls.all())))

        return params

    @classmethod
    def create(cls, name: str) -> Optional[__type__]:
        """ Create model. If model exist, return None. Otherwise, return Model. """

        # noinspection PyUnresolvedReferences
        if cls.__type__.exists(exists().where(cls.__type__.name == name)):
            logger().error("Cannot create '%s'. Already exists" % name, {'object': AbstractListService})
            return

        return cls.__type__.create(name=name)

    @classmethod
    def rename(cls, model: __type__, new_name: str) -> bool:
        """ Rename if models not exist with new name. If success return True. Otherwise, return False. """

        # noinspection PyUnresolvedReferences
        if cls.__type__.exists(exists().where(cls.__type__.name == new_name)):
            # noinspection PyUnresolvedReferences
            logger().error(
                "Cannot be updated (%s to %s). (%s) Already exists." % (model.name, new_name, new_name),
                {'object': AbstractListService}
            )

            return False

        model.update({"name": new_name})

        return True
