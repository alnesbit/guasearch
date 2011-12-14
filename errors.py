class HTTPError(Exception):
    def __init__(self, status_code, info=None):
        self.status_code = status_code
        self.info = info

    def __repr__(self):
        return '<HTTPError: %s>' % self.status_code
