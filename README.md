# MusicBrainzAPI
A series of scripts that enable retrieving information from MusicBrainz API: https://musicbrainz.org/doc/MusicBrainz_API

# Usage
```python
import MusicBrainzAPI as mb
#mb.debug = True
```

# Functions

Get artist data using unique identifier
```
getArtistByMBID(mbid)
```

Get all releases by artist
```
getReleasesByArtist(mbid)
```

Get just a list of release titles
```
getReleaseTitlesByArtist(mbid)
```