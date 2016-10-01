#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
import ConfigParser

environment = 'dev'  # TODO: get this from somewhere
config_directory = 'config'

config = ConfigParser.RawConfigParser()
config.read(config_directory + "/" + environment + ".cfg")

# Secure config is stored in a separate file (so that normal config can go in the repo)
secure_config = ConfigParser.RawConfigParser()
secure_config.read(config_directory + "/" + environment + "-secure.cfg")

user_agent = secure_config.get("firsttutors", "useragent")
cookie = secure_config.get("firsttutors", "cookie")
cutoff_date = config.get("tutparser", "cutoff")
pages = [1,2,3]

cutoff_dt = datetime.datetime.strptime(cutoff_date, "%d/%m/%Y")
current_baseuri = config.get("firsttutors", "baseuri")+"/uk/members/tutor-requests.php?old=0"
old_baseuri = config.get("firsttutors", "baseuri")+"/uk/members/tutor-requests.php?old=1"

uris = []
for page in pages:
	uris.append({"page": page, "uri": current_baseuri})
for page in pages:
	uris.append({"page": page, "uri": old_baseuri})

headers = {
    'User-Agent': user_agent,
    'Cookie': cookie
}

conversations = []

for uri in uris:
	request_uri = uri["uri"] + "&page=" + str(uri["page"])
	print request_uri
	response = requests.get(request_uri, headers=headers)
	html_doc = response.text

	soup = BeautifulSoup(html_doc, 'html.parser')

	conversation_divs = soup.findAll('div', {"class" : "conversation"})
	for conversation_div in conversation_divs:
		conversation_div = BeautifulSoup(str(conversation_div), 'html.parser')
		title = conversation_div.findAll('div', {"class" : "left"})[0].text
		match = False
		if "(match)" in title:
			match = True
		title = title.replace("(no match) ", "").replace("(match) ", "")
		date = conversation_div.findAll('div', {"class" : "right"})[0].text.replace("Request made: ", "")
		date_dt = datetime.datetime.strptime(date, "%d/%m/%Y")
		link = conversation_div.findAll('div', {"class" : "footer"})[0].a.attrs["href"]
		conversation = {"title": title, "date": date, "link": link, "match": match}
		#print conversation

		if(date_dt >= cutoff_dt):
			conversations.append(conversation)
		else:
			print "Skipping conversation on " + date + " as it is before the cutoff date"
	time.sleep(1)

output = json.dumps(conversations, ensure_ascii=False, indent=4, sort_keys=True)
print output

with open("data/conversations.json", "w") as f:
    f.write(output)
