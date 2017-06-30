from mastodon import Mastodon
import feedparser
import os

your_instance = 'https://mastodon.social'
login = 'me@email.com'
pwd = ''

filename = 'feedMastodon-db.txt'
feedurl = 'http://exemple.com/rss.xml'
hashtags = '#feedMastodon #Mastodon'
maxtoots = 3

if not os.path.exists('feedMastodon-pytooter_clientcred.txt'):
	Mastodon.create_app(
		'feedMastodon',
		to_file = 'feedMastodon-pytooter_clientcred.txt',
		api_base_url = your_instance
	)

mastodon = Mastodon(
	client_id = 'feedMastodon-pytooter_clientcred.txt',
	api_base_url = your_instance
)
mastodon.log_in(
	login,
	pwd
)

nbtoot = 0
feed = feedparser.parse(feedurl)

for item in reversed(feed.entries):
	send = True
	title = item.title
	link = item.link
	toot = title + ' ' + link

	if hashtags:
		toot += ' ' + hashtags

	if os.path.exists(filename):
		db = open(filename, "r+")
		entries = db.readlines()
	else:
		db = open(filename, "a+")
		entries = []

	for entry in entries:
		if link in entry:
			send = False

	if send:
		mastodon.toot(toot)
		db.write(link + '\n')
		db.flush()

		nbtoot = nbtoot + 1
		if nbtoot >= maxtoots:
			break

db.close()
