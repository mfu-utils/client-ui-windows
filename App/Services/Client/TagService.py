from typing import List

from App.Models.Client.Tag import Tag
from App.Services.Client.AbstractListService import AbstractListService


class TagService(AbstractListService):
    __type__ = Tag

    @staticmethod
    def save_list(tags: List[str]) -> List[Tag]:
        tag_models = []

        if type(tags) is not list:
            tags = [tags]

        for tag in tags:
            tag: str

            model = Tag.query().where(Tag.id == int(tag)).one_or_none() if tag.isnumeric() else None

            if not model:
                model = Tag.find_or_create({'name': tag})

            tag_models.append(model)

        return tag_models
