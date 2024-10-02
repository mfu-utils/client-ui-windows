from typing import List, Union, Any


class DotPathAccessor:
    def __init__(self, data: Union[dict, list]):
        self._data = data

    def data(self) -> dict:
        return self._data

    def get(self, dot_path: Union[List, str]) -> Any:
        if not dot_path:
            return self._data

        if type(dot_path) is str:
            if '.' not in dot_path:
                return self._data.get(dot_path)

            dot_path = dot_path.split('.')

        data_item = self._data

        for segment in dot_path:
            data_item = data_item.get(segment)

            if data_item is None:
                return data_item

        return data_item

    def set(self, dot_path: str, value: Any) -> bool:
        if '.' not in dot_path:
            self._data[dot_path] = value

        segments = dot_path.split('.')

        data_item = self._data

        for segment in segments:
            if data_item is None:
                return False

            if segment == segments[-1]:
                data_item[segment] = value
                break

            if not (item := data_item.get(segment)):
                item = data_item[segment] = {}

            data_item = item

        return True
