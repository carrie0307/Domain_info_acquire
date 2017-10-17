# coding=utf-8
import requests
import re
from pymongo import *


client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info
res = collection.find({'page_icp':{'$ne':''}},{'page_icp':True, 'auth_icp':True, 'domain':True, '_id':False})
for item in list(res):
    # if item['page_icp'] != '--' and item['page_icp'] != '-1':
        # print item['domain'], item['auth_icp'], item['page_icp']
    # if u'ICP证' in item['page_icp'] or u'ICP证' in item['auth_icp']:
        # print item['domain'], item['auth_icp'], item['page_icp']
        # collection.update({'domain': item['domain']}, {'$set': {'page_icp':''}})
    if u'ICP证' in item['auth_icp']:
        print item['domain'], item['auth_icp'], item['page_icp']
        # collection.update({'domain': item['domain']}, {'$set': {'page_icp':''}})



'''
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
'''
