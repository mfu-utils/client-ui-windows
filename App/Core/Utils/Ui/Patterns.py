class Patterns:
    DIRECTORY_WINDOWS = r'^\w:(\\[\w!-_ ]+)*$'
    DIRECTORY_NON_WINDOWS = r'^(?:/[\w!-_ ]+)+$'

    EXEC_WINDOWS = r'^\w:(\\[\w!-_ ]+)*.exe$'
    EXEC_NON_WINDOWS = r'^(?:/[\w!-_ ]+)+$'

    IP = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'

    _PRINTING_PAGE_PATTERN = r'[1-9]\d*(?:-[1-9]\d*)?'
    PRINTING_PAGE_PATTERN = f'^(?:{_PRINTING_PAGE_PATTERN})(?:,{_PRINTING_PAGE_PATTERN})*$'
