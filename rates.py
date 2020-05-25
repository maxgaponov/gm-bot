import json
import requests
from cachetools.func import ttl_cache
from config import BASE_CURRENCY, RATES_API_KEY, RATES_API_URL, CURRENCIES


def convert_rates_to_base(rates):
    result = {}
    for cur in CURRENCIES:
        result[cur] = rates[BASE_CURRENCY] / rates[cur]
    return result


def make_api_request():
    params = {
        'app_id': RATES_API_KEY
    }
    return requests.get(RATES_API_URL, params=params)


@ttl_cache(maxsize=1, ttl=60 * 60)
def get_rates():
    response = make_api_request()
    rates = json.loads(response.text)['rates']
    return convert_rates_to_base(rates)
