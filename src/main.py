import getRestData
import json
from RESTObject import RESTObject as ro

rootURL = 'https://musicbrainz.org/ws/2/'
#Provide a User-Agent so they can contact us if something goes wrong
userAgent = 'MusicBrainzAPI/0.1 (https://github.com/samuelshiels/MusicBrainzAPI)'
#sleep time, in ms, between any api calls, MB allow up to 50/s but we only need 10 for now
sleep = 100
#cache time, in mins, for api calls to refresh cached data, we keep anything for 1 week since I have some obscure bands that may suddenly get their catalog updated
time = 10080
#root cache directory
cache = 'cache/'

def buildHeaderObj():
    global userAgent
    headers = {}
    headers['User-Agent'] = userAgent
    #we want responses in json, because fuck xml
    headers['Accept'] = 'application/json'
    return headers

def runRest(e, p, o, c):
    global rootURL
    global cache
    global time
    global sleep
    restObj = ro(operation='get', endpoint=rootURL + e,params=p,headers=buildHeaderObj(),payload={})
    config = {}

    config['output'] = o + '.json'
    config['cache'] = cache + c
    config['time'] = time
    config['sleep'] = sleep
    config['rest'] = restObj
    return getRestData.execute(config)

def getArtistByMBID(mbid):
    return runRest('artist/' + mbid, {'inc':'aliases'}, mbid, 'artist')
    pass

def getReleasesByArtist(mbid):
    #contains property 'release-groups'
    return runRest('artist/' + mbid, {'inc':'aliases+release-groups'}, mbid, 'releases')
    pass

def main():
    #At The Gates
    responseString = getReleasesByArtist('35f92c4a-69d0-4ed1-ab9e-05259db89d14')
    response = json.loads(getReleasesByArtist('35f92c4a-69d0-4ed1-ab9e-05259db89d14'))
    for release in response['release-groups']:
        print (release['title'])
    pass

if __name__ == "__main__":
    main()