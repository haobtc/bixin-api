
class APIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        super(APIError, self).__init__(msg)