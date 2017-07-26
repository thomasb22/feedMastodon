#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
from mastodon import Mastodon
import feedparser
import re

your_instance = 'https://mastodon.social'
login = 'me@email.com'
pwd = ''

feedurl = 'http://exemple.com/rss.xml'
hashtags = '#feedMastodon #Mastodon'

filename = 'feedMastodon-db.txt'
show_summary = True;
maxtoots = 2
maxchar = 500

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

nbtoot = 0
feed = feedparser.parse(feedurl)

for item in reversed(feed.entries):
	send = True
	title = item.title
	summary = re.sub('<.*?>', '', item.summary)
	link = item.link
	toot = title + ' ' + link

	if show_summary:
		toot = title + '\n\n"' + summary + '"\n\n' + link

	if hashtags:
		toot += ' ' + hashtags

	if show_summary and len(toot) > maxchar and len(summary) > (len(toot) - maxchar) - 4:
		if hashtags:
			maxsum = len(summary) - (len(toot) - maxchar) - 4
		else:
			maxsum = len(summary) - (len(toot) - maxchar) - 3
		toot = title + '\n\n"' + summary[:maxsum] + '[…]"\n\n' + link

		if hashtags and len(toot) <= maxchar - (len(hashtags) + 1):
			toot += '\n\n' + hashtags
	elif len(toot) > maxchar and len(title) > (len(toot) - maxchar) - 3:
		maxtitle = len(title) - (len(toot) - maxchar) - 3
		toot = title[:maxtitle] + '[…] ' + link

		if hashtags and len(toot) <= maxchar - (len(hashtags) + 1):
			toot += ' ' + hashtags

	if len(toot) > maxchar:
		send = False

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
		if nbtoot == 0:
			mastodon.log_in(login, pwd)

		mastodon.toot(toot)
		db.write(link + '\n')
		db.flush()

		nbtoot = nbtoot + 1
		if nbtoot >= maxtoots:
			break

	db.close()
