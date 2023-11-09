#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import wget
from mastodon import Mastodon
import feedparser
from bs4 import BeautifulSoup

your_instance = 'https://mastodon.social'
login = 'me@email.com'
pwd = ''

feedsUrl = ['http://exemple.com/rss1.xml', 'http://exemple.com/rss2.xml']
hashtags = '#feedMastodon #Mastodon'

filename = 'feedMastodon-db.txt'
tmpdir = 'tmp'
show_summary = [False, False]
show_picture = [False, False]
maxtoots = [2, 2]
maxchar = [500, 500]
logged = False

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

for idx, feedUrl in enumerate(feedsUrl):
	nbtoot = 0
	feed = feedparser.parse(feedUrl)

	for item in reversed(feed.entries):
		send = True
		soup = BeautifulSoup(item.title, 'lxml')
		title = soup.text
		soup = BeautifulSoup(item.summary, 'lxml')
		summary = soup.text
		link = item.link
		toot = title + '\n\n' + link

		if show_summary[idx]:
			toot = title + '\n\n"' + summary + '"\n\n' + link

		if hashtags:
			toot += '\n\n' + hashtags

		if show_summary[idx] and len(toot) > maxchar[idx] and len(summary) > (len(toot) - maxchar[idx]) - 2:
			if hashtags:
				maxsum = len(summary) - (len(toot) - maxchar[idx]) - 2
			else:
				maxsum = len(summary) - (len(toot) - maxchar[idx]) - 1
			toot = title + '\n\n"' + summary[:maxsum] + '…"\n\n' + link

			if hashtags and len(toot) <= maxchar[idx] - (len(hashtags) + 1):
				toot += '\n\n' + hashtags
		elif len(toot) > maxchar[idx] and len(title) > (len(toot) - maxchar[idx]) - 1:
			maxtitle = len(title) - (len(toot) - maxchar[idx]) - 1
			toot = title[:maxtitle] + '… ' + link

			if hashtags and len(toot) <= maxchar[idx] - (len(hashtags) + 1):
				toot += '\n\n' + hashtags

		if len(toot) > maxchar[idx]:
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
			if not logged:
				mastodon.log_in(login, pwd)
				logged = True

			print( str(idx) + " " + str(show_picture[idx]) )

			if show_picture[idx] and item.enclosures:
				if item.enclosures[0].type[:5] == 'image' and int(item.enclosures[0].length) <= 1000000:
					tmpfilename = item.enclosures[0].href.split('/')[-1]
					tmppath = tmpdir + '/' + tmpfilename
					pictures_ids = []

					if not os.path.exists(tmpdir):
						os.mkdir(tmpdir)

					wget.download(item.enclosures[0].href, tmppath)
					pictures_ids.append( mastodon.media_post(tmppath) )
					mastodon.status_post(toot, media_ids=pictures_ids)
					os.remove(tmppath)
			else:
				mastodon.toot(toot)

			db.write(link + '\n')
			db.flush()

			nbtoot = nbtoot + 1
			if nbtoot >= maxtoots[idx]:
				break

		db.close()

if os.path.exists(tmpdir):
	os.rmdir(tmpdir)
