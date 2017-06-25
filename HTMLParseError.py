class HTMLParseError(Exception):
    def __init__(self, message):
        super(HTMLParseError, self).__init__(message)
