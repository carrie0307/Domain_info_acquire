# conding:utf-8
import requests
import re

html = requests.get('http://icp.chinaz.com/qq.com').text
content = re.compile(r'<p><font>(.+?)</font>').findall(html)
print content[0]
