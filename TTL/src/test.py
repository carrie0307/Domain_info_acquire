# encoding:utf-8
from pymongo import *



'''建立链接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_ttl

# collection.update({'domain': 'www.168168cc.com'}, {'$set': {'cname_ttl.cnames':['aaa','bbb'], 'cname_ttl.ips':['111.112', '223.345']}})
# res = collection.find({'flag':1},{'domain': True, '_id':False ,'cname_ttl':True}).limit(3000)
# print '---'
# for item in list(res):
#     print item['domain'],len(item['cname_ttl']['cnames'])

res = collection.find({'domain': 'www.68fff.win'})[0]
print len(res['ip_ttl']['ips'])
print len(list(set(res['ip_ttl']['ips'])))
