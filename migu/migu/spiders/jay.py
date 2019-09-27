# -*- coding: utf-8 -*-
import json

import scrapy
# from lxml import etree
from scrapy import Request
from scrapy.selector import Selector
from selenium import webdriver

import migu.spiders.ip_proxy as proxy_helper
from migu.items import MiguItem


def transfer_cookie(cookie):
    """
    transfer string cookie to dict
    :param cookie: a=1;b=2
    :return: {'a': '1', 'b': '2'}
    """
    if not cookie:
        return None
    item_dict = {}
    items = cookie.split(';')
    for item in items:
        kv = item.split('=')
        if len(kv) < 2:
            continue
        key = kv[0].replace(' ', '')
        value = kv[1]
        item_dict[key] = value
    return item_dict


def download_parse(response, song_id):
    """
    parse song download url
    :param song_id: song id
    :param response: response with song download info
    :return: download url
    """
    res = json.loads(response.text)
    item = MiguItem()
    item['url'] = res.get('downUrl')
    item['id'] = song_id
    yield item


def login_and_get_cookie(username, password):
    driver = webdriver.Chrome('./chromedriver')
    driver.get(
        'https://passport.migu.cn/login?sourceid=220001&apptype=0&forceAuthn=false&isPassive=false&authType=MiguPassport&passwordControl=0&display=web&referer=http://music.migu.cn/v3&logintype=1')
    driver.find_element_by_xpath("./*//li[@class='accountLg fr']").click()
    driver.find_element_by_xpath("./*//input[@id='J_AccountPsd']").send_keys(username)
    driver.find_element_by_xpath("./*//input[@id='J_PasswordPsd']").send_keys(password)
    driver.find_element_by_xpath("./*//div[@class='form-item form-item0']").click()
    driver.get('http://music.migu.cn/v3')
    cookie_items = driver.get_cookies()
    cookie = {}
    for cookie_item in cookie_items:
        cookie[cookie_item['name']] = cookie_item['value']
    return cookie


class JaySpider(scrapy.Spider):
    def __init__(self, name=None, type='SD', singer='112', username='', password='', **kwargs):
        super(JaySpider, self).__init__(name, **kwargs)

        if not username or not password:
            raise Exception('please pass [username] and [password] to spider!!!')

        self.type = type
        self.singer_id = singer
        self.proxies = proxy_helper.get_proxies()
        if len(self.proxies) <= 0:
            raise Exception('no valid ip proxy here!!!')
        self.cookie = login_and_get_cookie(username=username, password=password)
        try:
            with open(self.singer_id + '_song_ids.log', 'r') as f:
                self.download_songs = set([song.strip('\n') for song in set(f)])
        except IOError as e:
            self.download_songs = set()
            print(e)

    name = 'jay'
    allowed_domains = ['music.migu.cn']
    # start_urls = ['http://music.migu.cn/']

    # 歌手歌曲列表页
    song_list_url = 'http://music.migu.cn/v3/music/artist/{singer_id}/song?from=migu&page={page}'
    # 歌曲下载页
    download_url = 'http://music.migu.cn/v3/api/order/download'
    # 下载请求body
    download_body = 'copyrightId={song_id}2&payType={pay_type}&type={type}&songType={song_type}'
    # 下载请求Header referer
    download_referer = 'http://music.migu.cn/v3/music/order/download/{song_id}'

    # cookie
    # cookie = transfer_cookie(
    #     'migu_cn_cookie_id=db6a93d5-cedb-495c-b281-29e548a41087; migu_cookie_id=b9c1457d-db40-4d38-8ac4-58b6f067dd32-n41568804654235; Hm_lvt_ec5a5474d9d871cb3d82b846d861979d=1567602519,1568804628,1569202768,1569225223; player_stop_open=0; addplaylist_has=1; add_play_now=1; audioplayer_exist=1; Hm_lpvt_ec5a5474d9d871cb3d82b846d861979d=1569304770; WT_FPC=id=288d09dddce98a61bba1567602492730:lv=1569304787598:ss=1569304560455; audioplayer_new=0; playlist_overlay=0; playlist_change=0; playlist_adding=0; audioplayer_open=0; WT_FPC=id=288d09dddce98a61bba1567602492730:lv=1569307005361:ss=1569307005361; migu_music_status=true; migu_music_uid=3c86c7ca-35f9-4c2e-9378-a7253eaddb10; migu_music_avatar=%252F%252Fcdnmusic.migu.cn%252Fv3%252Fstatic%252Fimg%252Fcommon%252Fheader%252Fdefault-avatar.png; migu_music_nickname=%E5%8F%AF%E7%88%B1%E7%9A%84%E8%A5%BF%E6%B4%8B%E6%9C%A8%E9%B1%BC; migu_music_level=0; migu_music_credit_level=2; migu_music_platinum=1; migu_music_msisdn=13504094299; migu_music_email=; migu_music_sid=s%3AkwV6aZxonU0Ritx5MpUxehL3UneMk3Ru.sep0Wi559K4Zazmk2MDJJcX0DEMEXs4KrMmB7MysQ0g'
    # )

    def start_requests(self):
        # return an iterable object
        yield Request(self.song_list_url.format(singer_id=self.singer_id, page=1),
                      callback=self.song_parse,
                      cb_kwargs={'next_page': 2})

    def song_parse(self, response, next_page):
        """
        请求下一页 & 解析音乐列表页
        :param response: response
        :param next_page: next_page
        :return:
        """
        # song_elements = etree.HTML(response.text).xpath('//div[@class="row J_CopySong"]')
        song_elements = Selector(text=response.text).xpath('//div[@class="row J_CopySong"]')
        for element in song_elements:
            song_id = element.attrib['data-cid']

            # 忽略已下载的音乐
            if song_id in self.download_songs:
                continue

            # 获取无损/高清/标清音乐
            if self.type == 'LL':
                yield self.request_download(song_id=song_id, pay_type='01', type=2, song_type='LLSONG')
            elif self.type == 'HD':
                yield self.request_download(song_id=song_id, pay_type='01', type=2, song_type='HDSONG')
            else:
                yield self.request_download(song_id=song_id)

        # 下一页
        # has_next_page = len(etree.HTML(response.text).xpath('//a[@class="pagination-next"]')) > 0
        has_next_page = len(Selector(text=response.text).xpath('//a[@class="pagination-next"]')) > 0
        if has_next_page:
            yield Request(self.song_list_url.format(singer_id=self.singer_id, page=next_page),
                          callback=self.song_parse,
                          cb_kwargs={'next_page': next_page + 1})

    def request_download(self, song_id, pay_type='00', type=1, song_type=''):
        """
        请求音乐下载地址
        :param song_id: song id
        :param pay_type: pay type
        :param type: type
        :param song_type: song type
        :return: download request
        """
        if not song_id:
            return

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.download_referer.format(song_id=song_id),
        }

        return Request(self.download_url,
                       body=self.download_body.format(
                           song_id=song_id,
                           pay_type=pay_type,
                           type=type,
                           song_type=song_type
                       ),
                       headers=headers,
                       method='POST',
                       cookies=self.cookie,
                       callback=download_parse,
                       cb_kwargs={'song_id': song_id})

    def parse(self, response):
        pass
