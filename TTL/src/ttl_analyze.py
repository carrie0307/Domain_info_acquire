# encoding:utf-8
from pymongo import *

'''建立链接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_ttl


def size_count():
    global collection
    ip_dict = {}
    cname_dict = {}
    res = collection.find({'flag':1},{'domain': True, '_id':False ,'cname_ttl':True, 'ip_ttl':True})
    for item in list(res):
        # ip_dict[len(item['ip_ttl']['ips'])] = auth_icp_dict.get(item['auth_icp']['icp'], 0) + 1
        # print item['cname_ttl']['cnames']
        print len(item['ip_ttl']['ips'])



if __name__ == '__main__':
    size_count()
