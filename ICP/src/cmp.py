# coding=utf-8
from pymongo import *
import re

client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info

def get_domain_icp():
    global collection
    global domain_q
    res = collection.find({'cmp':0},{'auth_icp':True, 'page_icp':True })

#  粤ICP备09088851号-9
def cmp_icp(domain_icp_list):
    global collection
    cmp_res = []
    for item in domain_icp_list:
        if item['auth_icp'] == '--' and item['page_icp'] == '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':1}})
        elif item['auth_icp'] == '--' and item['page_icp'] != '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':2}})
        elif item['auth_icp'] != '--' and item['page_icp'] == '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':3}})
        else:
            auth_icp = unicode(item['auth_icp'], "utf-8")
            page_icp = unicode(item['page_icp'], "utf-8")
            auth_icp = re.compile(u'([\u4e00-\u9fa5]{1}(ICP[\u5907][\d]{6,8}[\u53f7])*-*[\d]*)').findall(html)

            # cmp_res.append({'_'})




if __name__ == '__main__':
    # get_domain_icp()
    icp = u'粤ICP备15061677号-1'
    auth_icp = re.compile(u'[\u4e00-\u9fa5]{1}(ICP[\u5907][\d]{6,8}[\u53f7])*-*[\d]*').findall(icp)
    print auth_icp
    print auth_icp[0]
