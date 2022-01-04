import unicodedata
import re
import requests
import pandas as pd

def slugify(value, allow_unicode=False):
	# Taken from https://github.com/django/django/blob/master/django/utils/text.py
	value = str(value)
	if allow_unicode:
		value = unicodedata.normalize("NFKC", value)
	else:
		value = unicodedata.normalize("NFKD", value).encode(
			"ascii", "ignore").decode("ascii")
	value = re.sub(r"[^\w\s-]", "", value.lower())
	return re.sub(r"[-\s]+", "-", value).strip("-_")

# National Transit Database page is here: https://www.transit.dot.gov/ntd
transit_systems = [
	{
		"5_digit_ntd_id": "20006",
		"name": "City of Long Beach Bus"
	}, {
		"5_digit_ntd_id": "20071",
		"name": "Huntington Area Rapid Transit"
	}, {
		"5_digit_ntd_id": "20072",
		"name": "Suffolk County Transit"
	}, {
		"5_digit_ntd_id": "20100",
		"name": "Long Island Rail Road"
	}, {
		"5_digit_ntd_id": "20206",
		"name": "Nassau Inter-County Express"
	}, {
		"5_digit_ntd_id": "20217",
		"name": "Hampton Jitney, Inc."
	}
]

transit_system_ids = [ transit_system["5_digit_ntd_id"] for transit_system in transit_systems ]
where_query_string = "$where=_5_digit_ntd_id='" + "' OR _5_digit_ntd_id='".join(transit_system_ids) + "'"

# We are defining the Socrata datasets we want to scrape here.
datasets = [
	{
		"identifier": "wwdp-t4re",
		# "title": "Service Flat File",
		# "dataset_link": "https://data.transportation.gov/Public-Transit/Service-Flat-File/wwdp-t4re/data",
		# "api_documentation_link": "https://dev.socrata.com/foundry/data.transportation.gov/wwdp-t4re",
		"description": "Transit system annual service data"
	}, {
		"identifier": "h3hh-wfqt",
		# "title": "Transit System Time Series",
		# "dataset_link": "https://data.transportation.gov/Public-Transit/Transit-System-Time-Series/h3hh-wfqt/data",
		# "api_documentation_link": "https://dev.socrata.com/foundry/data.transportation.gov/h3hh-wfqt",
		"description": "Transit system annual financial data"
	}, {
		"identifier": "5ti2-5uiv",
		# "title": "Monthly Modal Time Series",
		# "dataset_link": "https://data.transportation.gov/Public-Transit/Monthly-Modal-Time-Series/5ti2-5uiv/data",
		# "api_documentation_link": "https://dev.socrata.com/foundry/data.transportation.gov/5ti2-5uiv",
		"description": "Transit system monthly safety data"
	}, {
		"identifier": "9ivb-8ae9",
		# "title": "Major Safety Events",
		# "dataset_link": "https://data.transportation.gov/Public-Transit/Major-Safety-Events/9ivb-8ae9/data",
		# "api_documentation_link": "https://dev.socrata.com/foundry/data.transportation.gov/9ivb-8ae9",
		"description": "Transit system safety incidents"
	}
]

# We are going to call every item within "datasets" a "dataset". As we go through each dataset, we are going to scrape the dataset.
for dataset in datasets:
	try:
		# We are creating an empty list called "results".
		results = []
		url = "https://data.transportation.gov/resource/" + dataset["identifier"] + ".json"
		# The limit can be up to 50000.
		limit = 1000
		count_payload = "$select=count(*)&" + where_query_string
		# "requests" documentation page is here: https://docs.python-requests.org/en/master/user/quickstart/
		count_request = requests.get(url, params=count_payload)
		# As we go through each page of the dataset, we are going to scrape that page of the dataset.
		count = int(count_request.json()[0]["count"])
		i = 0
		while i < count / limit:
			offset = i * limit
			loop_payload = "$limit=" + str(limit) + "&$offset=" + str(offset) + "&" + where_query_string
			loop_request = requests.get(url, params=loop_payload)
			for result in loop_request.json():
				results.append(result)
			i += 1
		# "pandas" documentation page is here: https://pandas.pydata.org/docs/index.html
		df = pd.DataFrame(results)
		file_name = slugify(dataset["description"])
		df.to_csv("csv/" + file_name + ".csv", index=False)
	except:
		pass