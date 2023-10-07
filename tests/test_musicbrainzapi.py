from src import MusicBrainzAPI as mb

def test_active():
	assert(1 == 1)
	assert(True is not False)

def test_getArtistByMBID():
	artistMBIDList = ['35f92c4a-69d0-4ed1-ab9e-05259db89d14']
	artist = mb.getArtistByMBID(artistMBIDList[0])
	assert(artist["type"] == "Group")
	assert(artist['sort-name'] == "At the Gates")
	releases = mb.getReleaseTitlesByArtist(artistMBIDList[0])