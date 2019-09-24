# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from urllib2 import unquote

import requests
from pydispatch import dispatcher
from scrapy import signals

from settings import MUSIC_DIR


def get_name(migu_name):
    name_arr = migu_name.split('_')
    if len(name_arr) < 2:
        return None
    return name_arr[0] + '_' + name_arr[1]


class MiguPipeline(object):

    def __init__(self):
        # signal connect
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        files = os.listdir(MUSIC_DIR)
        self.name_set = set()
        self.id_set = set()
        for item in files:
            if item != 'flac' and (item.endswith('mp3') or item.endswith('flac') or item.endswith('m4a')):
                name = get_name(item)
                if not name:
                    self.name_set.add(name)

    # 下载音乐
    def process_item(self, item, spider):
        url = item['url']
        if url is not None:
            name = unquote(url.split('FN=')[1].encode('utf-8'))
            # id未下载且文件名不存在
            if item['id'] not in self.id_set and get_name(name) not in self.name_set:
                f = requests.get(url)
                try:
                    with open(MUSIC_DIR + name, 'wb') as code:
                        code.write(f.content)
                    self.id_set.add(item['id'])
                except IOError as e:
                    print e

    # 将已下载的id记录到临时文件
    def spider_closed(self, spider):
        with open(spider.singer_id + '_song_ids.log', 'a') as f:
            for song_id in self.id_set:
                f.write(song_id + '\n')
