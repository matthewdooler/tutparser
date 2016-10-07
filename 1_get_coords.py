#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
import os
import hashlib
import errno
import ConfigParser

environment = 'dev'  # TODO: get this from somewhere
config_directory = 'config'

config = ConfigParser.RawConfigParser()
config.read(config_directory + "/" + environment + ".cfg")

# Secure config is stored in a separate file (so that normal config can go in the repo)
secure_config = ConfigParser.RawConfigParser()
secure_config.read(config_directory + "/" + environment + "-secure.cfg")

disk_caching = config.get("tutparser", "disk_caching") == 'True'
disk_caching_dir = config.get("tutparser", "disk_caching_dir")

user_agent = secure_config.get("firsttutors", "useragent")
cookie = secure_config.get("firsttutors", "cookie")

headers = {
    'User-Agent': user_agent,
    'Cookie': cookie
}

def write_response_to_cache(uri, params, response):
    if response.status_code == 200:  # only cache ok responses
        try:
            os.makedirs(disk_caching_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        f = open(disk_caching_dir+"/"+_get_response_cache_filename(uri, params), "wb")
        f.write(response.content)
        f.close()
    return None

def read_response_from_cache(uri, params):
    f = open(disk_caching_dir+"/"+_get_response_cache_filename(uri, params), "rb")
    content = f.read()
    f.close()
    return CachedHTTPResponse(content=content, status_code=200)

def _get_response_cache_filename(uri, params):
    h = hashlib.sha256()
    h.update(uri+str(params))
    return h.hexdigest()

# Make a HTTP request, using the cache if enabled
def _http_get_with_cache_if_enabled(uri, params):
    if disk_caching:
        try:
            r = read_response_from_cache(uri, params)
            if r.content:
                return r
            else:
                # empty cache file (it happens!)
                r = _http_get_without_cache(uri, params)
                write_response_to_cache(uri, params, r)
                return r
        except IOError:
            # not in local cache, so make a real request and cache the response
            r = _http_get_without_cache(uri, params)
            write_response_to_cache(uri, params, r)
            return r
    else:
        return _http_get_without_cache(uri, params)

def _http_get_without_cache(uri, params):
    time.sleep(1)
    return requests.get(uri, headers=headers)

class CachedHTTPResponse(object):
    def __init__(self, content, status_code):
        self.content = content
        self.text = content.decode()
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)

with open('data/conversations.json') as f:    
    conversations = json.load(f)

for conversation in conversations:
    request_uri = conversation["link"]
    print request_uri
    response = _http_get_with_cache_if_enabled(request_uri, params=[])
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    a = soup.find('a', text="Area Map")
    if a is not None:
        link = a.attrs["href"]
        coords_str = link.replace("https://maps.google.com/maps/api/staticmap?center=", "").split("&zoom")[0]
        conversation["coords"] = coords_str

output = json.dumps(conversations, ensure_ascii=False, indent=4, sort_keys=True)
print output

with open("data/conversations-with-coords.json", "w") as f:
    f.write(output)
