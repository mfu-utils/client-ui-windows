from re import findall


class Import:
    @staticmethod
    def parse_import(namespace: str):
        segments = namespace.split('.')

        if segments[-1][-1] == '!':
            segments[-1] = segments[-1][:-1]
            segments.append(segments[-1][:])

        return '.'.join(segments[:-1]), segments[-1]

    @staticmethod
    def create_controller_alias(name: str) -> str:
        return '_'.join(findall('[A-Z][a-z0-9]*', name)[:-1]).lower()
