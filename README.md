# MusicBrainzAPI
A series of scripts that enable retrieving information from MusicBrainz API: https://musicbrainz.org/doc/MusicBrainz_API

# Usage
```python
import jsonpickle
from music_brainz_api_micro.music_brainz_api import MusicBrainzAPI as MB

mb = MB()
artist = mb.get_artist_by_mbid(
    "35f92c4a-69d0-4ed1-ab9e-05259db89d14"
    )
if artist.error is False:
    artist_obj = jsonpickle.decode(artist.reponse)
    print(artist_obj["sort-name"])
    # "At the Gates" 
```

# Functions

Get artist data using unique identifier
```
get_artist_by_mbid(mbid)
```

Get all releases by artist
```
get_releases_by_artist(mbid)
```

Get just a list of release titles
```
get_release_titles_by_artist(mbid)
```

# Build
```python
python -m build
python -m twine upload dist/*
```