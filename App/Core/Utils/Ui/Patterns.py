class Patterns:
    DIRECTORY_WINDOWS = r'^\w:(\\[\w!-]+)*$'
    DIRECTORY_NON_WINDOWS = r'^(?:/[\w!-]+)+$'
    IP = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'

    _PRINTING_PAGE_PATTERN = r'[1-9]\d*(?:-[1-9]\d*)?'
    PRINTING_PAGE_PATTERN = f'^(?:{_PRINTING_PAGE_PATTERN})(?:,{_PRINTING_PAGE_PATTERN})*$'
