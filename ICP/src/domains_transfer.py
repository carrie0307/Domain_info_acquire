# coding=utf-8
from pymongo import *
'''
将原始的domain转移到icp表中
'''


client = MongoClient('172.29.152.152', 27017)

def get_ip_domains():
    """
    从ip库中获取原始的域名
    :return: 域名列表
    """
    db = client.eds_last
    collection = db.domain_ip_cname1
    # 通过find的第二个参数来指定返回的键
    res = collection.find({},{'domain': True, '_id':False })
    domains = [str(domain['domain']) for domain in list(res)]
    return domains


def transfer_domains(domains):
    """
    将域名和document的原始构造插入表中
    :param domains: 原始的域名列表
    :return: 域名列表
    """
    db = client.domain_icp_analysis
    collection = db.domain_icp_info
    domain_documents = [{'domain':domain, 'auth_icp':'', 'page_icp':'', 'cmp':0} for domain in domains]
    collection.insert_many(domain_documents)
    print 'insert over ... '





if __name__ == '__main__':
    domains = get_ip_domains()
    transfer_domains(domains)
