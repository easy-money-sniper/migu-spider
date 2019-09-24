# Introduction
This is a scrapy spider for crawling singer's all music on music.migu.com
# How to use
1. configure path to save downloaded music in settings.py
2. download an appropriate version of chrome driver and save the current path which you're gonna execute scrapy shell
3. configure spider parameters
	1. -a singer=112 (get it from singer home page from migu, e.g. http://music.migu.cn/v3/music/artist/112?from=migu, optional, 112 default)
	2. -a type=LL (LL: lossless, HD: high definition, SD: standard definition. optional, SD default)
	3. -a username=xxx (your migu account, phone number, mandatory)
	4. -a password=xxx (your password, mandatory)
# Example
scrapy crawl jay -a singer=112 -a type=LL -a username=xxx -a password=xxx
# Where to get chrome driver
>https://sites.google.com/a/chromium.org/chromedriver/home
