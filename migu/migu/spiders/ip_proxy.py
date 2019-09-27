# coding=utf-8
import requests

from lxml import html

etree = html.etree
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'


def get_all_proxies(content):
    ips = etree.HTML(content).xpath('//table[contains(@id, "ip_list")]/tr/td[2]/text()')
    ports = etree.HTML(content).xpath('//table[contains(@id, "ip_list")]/tr/td[3]/text()')

    all_proxies = []
    for i in range(len(ips)):
        all_proxies.append(f"{ips[i]}:{ports[i]}")
    return all_proxies


def is_proxy_valid(ip_port):
    proxy = {'http': ip_port}

    migu_url = 'http://music.migu.cn/v3'
    try:
        res = requests.get(url=migu_url, headers={'User-Agent': user_agent}, proxies=proxy, timeout=1)
        return True if res.content else False
    except BaseException as e:
        print(e)
    return False


def get_proxies():
    url = 'http://www.xicidaili.com/nn/1'
    response = requests.get(url=url, headers={'User-Agent': user_agent})
    all_proxies = get_all_proxies(response.content)

    valid_proxies = []
    for data in all_proxies:
        if is_proxy_valid(data):
            valid_proxies.append(f'http://{data}')

    return valid_proxies
