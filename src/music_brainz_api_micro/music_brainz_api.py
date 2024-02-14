"""
Provides a class and functions to manage sending requests to
MusicBrainz. Calls will include an entire second of waiting
to conform to MusicBrainz API standards
"""
import jsonpickle
import logging
import os
import json
from pathlib import Path
from rest_client_micro.rest_client import RESTClient as RC
from rest_client_micro.rest_object import RESTObject as RO
from rest_client_micro.response import Response as R


class MusicBrainzAPI():
    """
    Main class to run API calls against MusicBrainz
    """

    app_name: str = 'MusicBrainzAPI'
    # sleep time, in ms, between any api calls, MB allows 1/s
    sleep: int = 1100
    # cache time, in mins, for api calls to refresh cached data, we keep anything for 1 week
    time: int = 10800
    cache_dir: str = os.path.join(str(Path.home()), ".cache/", app_name)
    config_dir = os.path.join(str(Path.home()), ".config/", app_name)

    user_agent: str = 'MusicBrainzAPI/0.1 (https://github.com/samuelshiels/MusicBrainzAPI)'
    root_url: str = 'https://musicbrainz.org/ws/2/'

    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)
    debug: bool = False

    def _debug(self, message: str):
        if self.debug:
            logging.debug(str(message))

    def __init__(self) -> None:
        pass

    def _build_header_obj(self):
        headers = {}
        headers['User-Agent'] = self.user_agent
        # we want responses in json, because fuck xml
        headers['Accept'] = 'application/json'
        return headers

    def _run_rest(self, e, p, o, c):
        self._debug("__runRest")
        rc = RC()
        rest_obj = RO(operation='get', endpoint=f'{self.root_url}{e}',
                      params=p, headers=self._build_header_obj(), payload={})
        config = {}
        config['output'] = o + '.json'
        config['cache'] = self.cache_dir + c
        config['time'] = self.time
        config['sleep'] = self.sleep
        config['rest'] = rest_obj
        self._debug(f"{config}")
        return rc.execute(rest_obj)

    def get_artist_by_mbid(self, mbid: str):
        """ Using the MusicBrainz ID of an artist returns the full
        MusicBrainz response

        Args:
            mbid (str): ID including dashes

        Returns:
            Response: Check for error property True or False, if 
            False 'response' property can be used
        """
        self._debug("getArtistByMBID")
        return self._run_rest(f'artist/{mbid}', {'inc': 'aliases'}, mbid, 'artist')

    def get_releases_by_artist(self, mbid: str):
        """contains property 'release-groups'"""
        return self._run_rest(f'artist/{mbid}', {'inc': 'aliases+release-groups'}, mbid, 'releases')

    def get_release_titles_by_artist(self, mbid: str) -> list[str] | list[R]:
        """runs a getReleasesByArtist but returns the release titles of the response"""
        ret_val = []
        artist_releases = self.get_releases_by_artist(mbid)
        if artist_releases.error is True:
            ret_val.append(artist_releases)
            return ret_val
        thawed = jsonpickle.decode(artist_releases.response)
        for release in thawed['release-groups']:
            ret_val.append(release['title'])
        return ret_val
