import MusicBrainzAPI as mb
log = True

artistMBID = '35f92c4a-69d0-4ed1-ab9e-05259db89d14'
print(mb.getArtistByMBID(artistMBID, log))
print(mb.getReleaseTitlesByArtist(artistMBID, log))

artistMBIDList = ['35f92c4a-69d0-4ed1-ab9e-05259db89d14']

for artist in artistMBIDList:
	print(mb.getArtistByMBID(artist, log))
	print(mb.getReleaseTitlesByArtist(artist, log))