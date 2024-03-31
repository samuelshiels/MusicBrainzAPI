"""
Provides a class and functions to manage sending requests to
MusicBrainz. Calls will include an entire second of waiting
to conform to MusicBrainz API standards
"""
import logging
import os
from pathlib import Path
import jsonpickle
from diskcache import Cache
from rest_client_micro import Response as R
from rest_client_micro import RESTClient as RC
from rest_client_micro import RESTObject as RO
from .cover_reponse import CoverResponse as CR


class MusicBrainzAPI():
    """
    Main class to run API calls against MusicBrainz
    """

    app_name: str = 'MusicBrainzAPI'
    # sleep time, in ms, between any api calls, MB allows 1/s
    sleep: int = 1100
    # 1 week 10800mins
    time: int
    cache: Cache
    cache_dir: str
    config_dir: str
    use_cache: bool
    force_cache: bool
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
                 cache_refresh_mins: int = 10800,
                 force_cache: bool = False,
                 use_cache: bool = True) -> None:
        """Initialise a MusicBrainzAPI instance

        :param config_dir: Directory to store/use configuration
        :param cache_dir: Directory to store cached data
        :param cache_refresh_mins: Duration to store cache data
            (default 10800 minutes)
        :param force_cache: Bypass cached data and force a rest call
            (default False)
        :param use_cache: Store and read results from cache
            (default True)
        """
        self.config_dir = config_dir or os.path.join(
            str(Path.home()), ".config/", self.app_name)
        self.cache_dir = cache_dir or os.path.join(
            str(Path.home()), ".cache/", self.app_name)
        self.time = cache_refresh_mins
        self.force_cache = force_cache
        self.use_cache = use_cache
        self.cache = Cache(self.cache_dir)

    def _build_header_obj(self) -> dict:
        headers = {}
        headers['User-Agent'] = self.user_agent
        # we want responses in json, because fuck xml
        headers['Accept'] = 'application/json'
        return headers

    def _run_get(self, e: str, p: dict, o: str, c) -> R:
        if self.force_cache:
            return self._run_rest(e, p, o, c)

        if self.use_cache:
            cache_result = self.cache.get(o)
            if cache_result is not None:
                return cache_result
            else:
                return self._run_rest(e, p, o, c)

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
        response = rc.execute(rest_obj)
        if self.use_cache:
            self._set_cache(o, response)

        return response

    def clear_cache(self) -> None:
        """
        Clears all keys from the diskcache database
        """
        self.cache.clear()

    def _set_cache(self, key: str, response: R) -> None:
        if response.error is False:
            thawed = jsonpickle.decode(response.response)
            if 'error' not in thawed:
                self.cache.set(
                    key=key,
                    value=response,
                    expire=self.time*60)

    def get_artist_by_mbid(self, mbid: str) -> R:
        """ Using the MusicBrainz ID of an artist returns the full
        MusicBrainz response

        :param mbid: MusicBrainz ID including dashes
        :returns: Response, check for error property True or False, if 
            False 'response' property can be used
        """
        self._debug("getArtistByMBID")
        return self._run_get(f'artist/{mbid}', {'inc': 'aliases'}, mbid, 'artist')

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

    def get_recording_cover(self, recording_mbid: str) -> CR | None:
        """From a recording mbid determines if it is a recording


        :param mbid: MusicBrainz recording ID including dashes
        :returns: CoverResponse object or None
        """
        recording_rels = self._run_get(
            f"recording/{recording_mbid}",
            {"inc": "aliases+work-rels+artist-credits"},
            recording_mbid,
            'recording'
        )
        if recording_rels.error is False:
            thawed = jsonpickle.decode(recording_rels.response)
            if 'relations' not in thawed:
                return None
            for r in thawed['relations']:
                if 'cover' in r['attributes']:
                    cr = CR()
                    cr.cover_track_mbid = recording_mbid
                    cr.cover_track_title = thawed['title']
                    cr.cover_track_artist = thawed['artist-credit'][0]['name']
                    cr.original_work_mbid = r['work']['id']
                    return cr
        return None
