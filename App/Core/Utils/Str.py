from typing import Union, Optional
import re


class Str:
    REPLACE_PATTERN = r'{{\s*%s\s*}}'

    @staticmethod
    def __replace_many(content: str, item: str, replace: str):
        return re.sub(Str.REPLACE_PATTERN % item, replace.replace('\\', '/'), content)

    @staticmethod
    def replace_templated(content: str, items: Union[list, str, dict], replace: Optional[str] = None) -> str:
        if isinstance(items, dict):
            for item, replace in items.items():
                content = Str.__replace_many(content, item, replace)

            return content

        if isinstance(items, str):
            items = [items]

        for item in items:
            content = Str.__replace_many(content, item, replace)

        return content
