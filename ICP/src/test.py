# coding=utf-8
import requests
import re

html = requests.get('http://icp.chinaz.com/www.365bet.cd', proxies = {'http': 'http://111.13.7.121:80'}).text
print html
if "<h2>404" in html:
    print '------'
    # eg. www.365bet.cd的查询结果
    icp = '--'
else:
    content = re.compile(r'<p><font>(.+?)</font>').findall(html)
    if content == []:
        content = re.compile(r'<p class="tc col-red fz18 YaHei pb20">([^<]+?)<a href="javascript:" class="updateByVcode">').findall(html)
    icp = content[0]
    print icp
