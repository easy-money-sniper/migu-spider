# coding=utf-8
from scrapy import cmdline

"""
singer:
    jay 112 (default)
    eason 116
    mayday 529
type:
    SD 标清
    HD 高清
    LL 无损
"""

name = 'jay'
cmd = 'scrapy crawl {0} -a singer=112 -a type=LL -a username=xxx -a password=xxx'.format(
    name)
cmdline.execute(cmd.split())
