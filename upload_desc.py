"""
code from
https://github.com/mini-kep/parsers/blob/master/parsers/mover/uploader.py
is used
"""

import requests
from time import sleep
import json

UPLOAD_API_TOKEN = 'insert token here'
UPLOAD_URL = 'http://minikep-db.herokuapp.com/api/desc'

def post(data, token=UPLOAD_API_TOKEN, endpoint=UPLOAD_URL):
    """
    Post *data* as json to API endpoint.
    Returns: status_code
    """
    json_data = json.dumps(data)
    return requests.post(url=endpoint,
                         data=json_data,
                         headers={'API_TOKEN': token}).status_code


def yield_chunks(gen, chunk_size=1000):
    """Split generator or list into smaller parts.
    Args:
        gen - list or generator of datapoints to send
        chunk_size - number of datapoints to send at one time
    Yields:
        list of size *chunk_size* or smaller
    """
    gen = list(gen)
    for i in range(0, len(gen), chunk_size):
        yield gen[i:i + chunk_size]


class Poster():
    """Post to database:
     - attempts to post to db and delay between attempts (safe post mechanism)
     - collects response status
     - holds number of attempts
    """
    max_attempts = 3  # times
    delay = 5  # seconds
    timer = None

    def __init__(self, data_chunk, post_func=post, delay=None):
        self.data = list(data_chunk)
        self.post_func = post_func
        if delay:  # override default delay time
            self.delay = delay
        self.attempts = 0
        self.status_code = None
        self.elapsed = 0

    def post(self):
        """Posts chunk of data to database using self.post()."""
        for self.attempts in range(1, self.max_attempts + 1):
            self.status_code = self.post_func(data=self.data)
            if self.status_code == 200:
                break
            sleep(self.delay)

    @property
    def is_success(self):
        return self.status_code == 200

    def __len__(self):
        return len(self.data)

    @property
    def status_message(self):
        n = len(self)
        if self.is_success:
            return f'Uploaded {n} datapoints in {self.attempts} attempt(s)'
        else:
            return f'Failed to upload {n} datapoints in {self.attempts} attempt(s)'

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}: {self.attempts} attempts, status code {self.status_code}'


if __name__ == "__main__": # pragma: no cover
    data = [
        {'abbr': 'bln_rub', 'en': 'bln rub', 'ru': 'млрд.руб.'},
        {'abbr': 'bln_usd', 'en': 'bln usd', 'ru': 'млрд.долл.'},
        {'abbr': 'gdp_percent', 'en': '% GDP', 'ru': '% ВВП'},
        {'abbr': 'mln_rub', 'en': 'mln rub', 'ru': 'млн.руб.'},
        {'abbr': 'rub', 'en': 'rub', 'ru': 'руб.'},
        {'abbr': 'rog', 'en': '% change to previous period', 'ru': '% к пред. периоду'},
        {'abbr': 'yoy', 'en': '% change to 12 months earlier', 'ru': '% год к году'},
        {'abbr': 'ytd', 'en': 'year to date', 'ru': 'период с начала года'},
        {'abbr': 'pct', 'en': '%', 'ru': '%'},
        {'abbr': 'bln_tkm', 'en': 'bln t-km', 'ru': 'млрд. тонно-км'}
    ]
    p = Poster(data)
    p.post()
    assert p.status_code == 200
