from typing import Union
import re


class PDFService:
    COUNT_PAGES_REGEX = re.compile(rb"/Type\s*/Page([^s]|$)", re.MULTILINE | re.DOTALL)

    @staticmethod
    def count_pages(file: Union[str, bytes]):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file = f.read()

        return len(PDFService.COUNT_PAGES_REGEX.findall(file))
