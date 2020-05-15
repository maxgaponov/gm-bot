import cachetools.func
import requests
import json
import config

def convert_rates_to_base(rates):
	result = {}
	for cur in config.CURRENCIES:
		result[cur] = rates[config.BASE_CURRENCY] / rates[cur]
	return result

def make_api_request():
	params = {
		'app_id': config.RATES_API_KEY
	}
	return requests.get(config.RATES_API_URL, params=params)

@cachetools.func.ttl_cache(maxsize=1, ttl=10)
def get_rates():
	response = make_api_request()
	rates = json.loads(response.text)['rates']
	return convert_rates_to_base(rates)
