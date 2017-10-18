# coding=utf-8
from pymongo import *
import threading


client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info


def get_icps():
    global collection
    global domain_q
    res = collection.find({'cmp':0},{'auth_icp':True, 'page_icp':True })
    return list(res)


if __name__ == '__main__':
    res = collection.find({},{'_id':False, 'domain':True, 'auth_icp':True, 'page_icp':True })
    auth_icp_dict = {}
    page_icp_dict = {}
    for item in list(res):
        if item['auth_icp'] != '--':
            auth_icp_dict[item['auth_icp']] = auth_icp_dict.get(item['auth_icp'], 0) + 1
        if item['page_icp'] != '--':
            page_icp_dict[item['page_icp']] = page_icp_dict.get(item['page_icp'], 0) + 1
    for icp in auth_icp_dict:
        if auth_icp_dict[icp] > 1:
            print icp, auth_icp_dict[icp]
    print '\n==================================\n'
    for icp in page_icp_dict:
        if page_icp_dict[icp] > 1:
            print icp, page_icp_dict[icp]
