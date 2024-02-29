"""
Provides a class and functions to manage sending requests to
MusicBrainz. Calls will include an entire second of waiting
to conform to MusicBrainz API standards
"""
import logging
import os
from pathlib import Path
import jsonpickle
from rest_client_micro.rest_client import RESTClient as RC
from rest_client_micro.rest_object import RESTObject as RO
from rest_client_micro import Response as R


class MusicBrainzAPI():
    """
    Main class to run API calls against MusicBrainz
    """

    app_name: str = 'MusicBrainzAPI'
    # sleep time, in ms, between any api calls, MB allows 1/s
    sleep: int = 1100
    # cache time, in mins, for api calls to refresh cached data, we keep anything for 1 week 10800mins
    time: int
    cache_dir: str
    config_dir: str

    user_agent: str = 'MusicBrainzAPI/0.1 (https://github.com/samuelshiels/MusicBrainzAPI)'
    root_url: str = 'https://musicbrainz.org/ws/2/'

    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)
    debug: bool = False

    def _debug(self, message: str):
        if self.debug:
            logging.debug(str(message))

    def __init__(self,
                 config_dir: str = None,
                 cache_dir: str = None,
                 cache_refresh: int = 10800) -> None:
        self.config_dir = config_dir or os.path.join(
            str(Path.home()), ".config/", self.app_name)
        self.cache_dir = cache_dir or os.path.join(
            str(Path.home()), ".cache/", self.app_name)
        self.time = cache_refresh

    def _build_header_obj(self) -> dict:
        headers = {}
        headers['User-Agent'] = self.user_agent
        # we want responses in json, because fuck xml
        headers['Accept'] = 'application/json'
        return headers

    def _run_rest(self, e: str, p: dict, o: str, c) -> R:
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

    def get_artist_by_mbid(self, mbid: str) -> R:
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

    def get_releases_by_artist(self, mbid: str) -> R:
        """contains property 'release-groups'"""
        return self._run_rest(f'artist/{mbid}', {'inc': 'aliases+release-groups'}, mbid, 'releases')

    def get_release_titles_by_artist(self, mbid: str) -> list[str] | list[R]:
        """Runs a getReleasesByArtist but returns the release titles of the responses
        
        :param mbid: MusicBrainz ID including dashes
        :returns: List of release titles for the associated artist        
        """
        ret_val = []
        artist_releases = self.get_releases_by_artist(mbid)
        if artist_releases.error is True:
            ret_val.append(artist_releases)
            return ret_val
        thawed = jsonpickle.decode(artist_releases.response)
        for release in thawed['release-groups']:
            ret_val.append(release['title'])
        return ret_val
