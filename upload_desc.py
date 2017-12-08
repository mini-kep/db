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
    p = post(data)
    assert p.status_code == 200
