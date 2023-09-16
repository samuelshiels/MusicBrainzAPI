import getRestData
import json
from RESTObject import RESTObject as ro
from pathlib import Path

appName = 'MusicBrainzAPI'
#sleep time, in ms, between any api calls, MB allow up to 50/s but we only need 10 for now. 2023 - Re-read rules and its 1/s
sleep = 1100
#cache time, in mins, for api calls to refresh cached data, we keep anything for 1 week since I have some obscure bands that may suddenly get their catalog updated
time = 10800
#root cache directory
cache = f'{Path.home}/.cache/{appName}/'

import os
ae = {}
ae['app_name'] = appName
ae['version'] = '0.1.0'
ae['root_dir'] = os.path.join(str(Path.home()), ".config/", ae['app_name'])
ae['cache_dir'] = os.path.join(str(Path.home()), '.cache', ae['app_name'])
ae['sleep'] = sleep
ae['time'] = time

rootURL = 'https://musicbrainz.org/ws/2/'
#Provide a User-Agent so they can contact us if something goes wrong
userAgent = 'MusicBrainzAPI/0.1 (https://github.com/samuelshiels/MusicBrainzAPI)'

import logging
logging.basicConfig(
format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)
debug = True
def __debugMessage(message):
	global debug
	if debug:
		logging.debug(str(message))


def __buildHeaderObj():
	global userAgent
	headers = {}
	headers['User-Agent'] = userAgent
	#we want responses in json, because fuck xml
	headers['Accept'] = 'application/json'
	return headers

def __runRest(e, p, o, c, log=False):
	global rootURL, cache, time, sleep
	restObj = ro(operation='get', endpoint=f'{rootURL}{e}',params=p,headers=__buildHeaderObj(),payload={})
	config = {}

	config['output'] = o + '.json'
	config['cache'] = cache + c
	config['time'] = time
	config['sleep'] = sleep
	config['rest'] = restObj
	return getRestData.execute(config, log)

def getArtistByMBID(mbid, log=False):
	return __runRest(f'artist/{mbid}', {'inc':'aliases'}, mbid, 'artist', log)



def getReleasesByArtist(mbid, log=False):
	"""contains property 'release-groups'"""
	return __runRest(f'artist/{mbid}', {'inc':'aliases+release-groups'}, mbid, 'releases', log)

def getReleaseTitlesByArtist(mbid, log=False):
	"""runs a getReleasesByArtist but returns the release titles of the response"""
	retVal = []
	artistReleases = getReleasesByArtist(mbid)
	response = json.loads(artistReleases)
	for release in response['release-groups']:
		retVal.append(release['title'])
	return retVal