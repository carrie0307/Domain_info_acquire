# encoding:utf-8
from pymongo import *

'''建立链接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_ttl


def size_count():
    '''
    整体所有域名ip和cname数量的统计
    ip_dict = {0: 1033, 1: 4894, 2: 89, 3: 21, 4: 19, 5: 12, 6: 2, 7: 3, 8: 1, 9: 10, 10: 12, 11: 1, 13: 5}
    cname_dict = {0: 4425, 1: 1221, 2: 424, 3: 27, 4: 1, 5: 4}
    '''
    global collection
    ip_dict = {}
    cname_dict = {}
    res = collection.find({'flag':1},{'domain': True, '_id':False ,'cname_ttl':True, 'ip_ttl':True})
    for item in list(res):
        ip_num = len(item['ip_ttl']['ips'])
        # cname_num = len(item['cname_ttl']['cnames'])
        cname_num = len(item['cname_ttl']['cname'])
        ip_dict[ip_num] = ip_dict.get(ip_num, 0) + 1
        cname_dict[cname_num] = cname_dict.get(cname_num, 0) + 1
    print ip_dict
    print cname_dict


def ttl_count():
    '''
    (同一个域名的ttl一致性统计)
    每个域名的ip和cname的ttl的种类统计
    ip/cname的ttl的数量为n个的域名有m个
    {n: m, n1: m1, n2: m2}
    ip = {0: 1033, 1: 5064, 2: 5}
    cname = {0: 4425, 1: 1557, 2: 118, 3: 2}
    '''
    global collection
    ip_dict = {}
    cname_dict = {}
    res = collection.find({'flag':1},{'domain': True, '_id':False ,'cname_ttl':True, 'ip_ttl':True})
    for item in list(res):
        ip_ttls = []
        cname_ttls = []
        for ip_ttl in item["ip_ttl"]["ttl"]:
            if ip_ttl not in ip_ttls:
                ip_ttls.append(ip_ttl)
        ip_ttls_num = len(ip_ttls)
        ip_dict[ip_ttls_num] = ip_dict.get(ip_ttls_num, 0) + 1
        for cname_ttl in item["cname_ttl"]["ttl"]:
            if cname_ttl not in cname_ttls:
                cname_ttls.append(cname_ttl)
        cname_ttls_num = len(cname_ttls)
        cname_dict[cname_ttls_num] = cname_dict.get(cname_ttls_num, 0) + 1
    print ip_dict
    print cname_dict
    print counter


def ttl_value_count():
    '''
    统计ttl值下域名的数量
    ip： {28800: 27, 1: 7, 900: 85, 1799: 2, 1800: 313, 10: 44, 3600: 689, 172817: 13, 86400: 1, 30: 8, 7200: 58, 7207: 1, 300: 182, 1209600: 1, 10800: 8, 60: 241, 14400: 2, 200: 4, 43200: 1, 334: 1, 469: 1, 600: 3333, 3601: 2, 500: 1, 245: 1, 120: 48}
    cname： {7200: 2, 1200: 239, 3: 3, 900: 12, 1799: 2, 200: 16, 28800: 27, 300: 37, 1800: 11, 3600: 550, 600: 509, 86400: 257, 150: 2, 14400: 8, 120: 83, 604800: 1, 60: 29, 10: 8, 10800: 3}
    '''
    global collection
    ip_dict = {}
    cname_dict = {}
    res = collection.find({'flag':1},{'domain': True, '_id':False ,'cname_ttl':True, 'ip_ttl':True})
    for item in list(res):
        ip_unique_ttls = list(set(item["ip_ttl"]["ttl"]))
        for ttl in ip_unique_ttls:
            ip_dict[ttl] = ip_dict.get(ttl, 0) + 1
        cname_unique_ttls = list(set(item["cname_ttl"]["ttl"]))
        for ttl in cname_unique_ttls:
            cname_dict[ttl] = cname_dict.get(ttl, 0) + 1
        # for ip_ttl in item["ip_ttl"]["ttl"]:
        #     ip_dict[ip_ttl] = ip_dict.get(ip_ttl, 0) + 1
    print ip_dict
    print cname_dict






if __name__ == '__main__':
    # size_count()
    # ttl_count()
    # ttl_value_count()
