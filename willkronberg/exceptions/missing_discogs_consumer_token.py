from discogs_client.exceptions import HTTPError


class MissingDiscogsConsumerToken(Exception):
    message: str

    def __init__(self, error: HTTPError):
        print(error)
        self.message = error.msg