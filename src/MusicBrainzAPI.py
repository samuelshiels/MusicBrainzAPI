import getRestData
import json
from RESTObject import RESTObject as ro
import LinuxHelper as lh

rootURL = 'https://musicbrainz.org/ws/2/'
#Provide a User-Agent so they can contact us if something goes wrong
userAgent = 'MusicBrainzAPI/0.1 (https://github.com/samuelshiels/MusicBrainzAPI)'
#sleep time, in ms, between any api calls, MB allow up to 50/s but we only need 10 for now
sleep = 100
#cache time, in mins, for api calls to refresh cached data, we keep anything for 1 week since I have some obscure bands that may suddenly get their catalog updated
time = 10800
#root cache directory
cache = lh.getHomeDirectory() + '/' + lh.getCacheDirectory() + 'MusicBrainzAPI/'

def __buildHeaderObj():
	global userAgent
	headers = {}
	headers['User-Agent'] = userAgent
	#we want responses in json, because fuck xml
	headers['Accept'] = 'application/json'
	return headers

def __runRest(e, p, o, c, log=False):
	global rootURL, cache, time, sleep
	restObj = ro(operation='get', endpoint=rootURL + e,params=p,headers=__buildHeaderObj(),payload={})
	config = {}

	config['output'] = o + '.json'
	config['cache'] = cache + c
	config['time'] = time
	config['sleep'] = sleep
	config['rest'] = restObj
	return getRestData.execute(config, log)

def getArtistByMBID(mbid, log=False):
	return __runRest('artist/' + mbid, {'inc':'aliases'}, mbid, '/artist', log)

def getReleasesByArtist(mbid, log=False):
	#contains property 'release-groups'
	return __runRest('artist/' + mbid, {'inc':'aliases+release-groups'}, mbid, '/releases', log)

def getReleaseTitlesByArtist(mbid, log=False):
	"""runs a getReleasesByArtist but returns the release titles of the response"""
	retVal = []
	artistReleases = getReleasesByArtist(mbid)
	response = json.loads(artistReleases)
	for release in response['release-groups']:
		retVal.append(release['title'])
	return retVal