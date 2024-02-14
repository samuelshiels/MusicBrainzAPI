from src.music_brainz_api_micro.music_brainz_api import MusicBrainzAPI as MB
import jsonpickle


def get_artist_by_mbid():
    """
    Run a simple call with one mbid, confirm it is the correct
    artist by checking type and sort-name
    """
    mb = MB()
    artist_mbid_list = ['35f92c4a-69d0-4ed1-ab9e-05259db89d14']
    artist = mb.get_artist_by_mbid(artist_mbid_list[0])
    assert artist.error is False
    thawed = jsonpickle.decode(artist.response)
    assert thawed['type'] == "Group"
    assert thawed['sort-name'] == "At the Gates"


def test_get_release_titles_by_artist():
    """
    Test returning the full release list of an artist, implicitly
    tests get_releases_by_artist, we tentively check the length
    of the returned array
    """
    mb = MB()
    artist_mbid_list = ['35f92c4a-69d0-4ed1-ab9e-05259db89d14']
    releases = mb.get_release_titles_by_artist(artist_mbid_list[0])
    assert len(releases) > 24
