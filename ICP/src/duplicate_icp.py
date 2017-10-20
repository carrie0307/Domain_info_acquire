# coding=utf-8
from pymongo import *
import icp_num
import re


client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info2


def get_icps():
    global collection
    global domain_q
    res = collection.find({},{'auth_icp':True, 'page_icp':True })
    return list(res)


def exact_cmp(icp_res):
    '''
    精确比对，即icp完整地进行比对
    '''
    auth_icp_dict = {}
    page_icp_dict = {}
    for item in icp_res:
        if item['auth_icp']['icp'] != '--':
            auth_icp_dict[item['auth_icp']['icp']] = auth_icp_dict.get(item['auth_icp']['icp'], 0) + 1
        if item['page_icp']['icp'] != '--' and item['page_icp']['icp'] != '-1':
            page_icp_dict[item['page_icp']['icp']] = page_icp_dict.get(item['page_icp']['icp'], 0) + 1
    auth_icp_dict['--'] = -1
    page_icp_dict['--'] = -1
    page_icp_dict['-1'] = -1
    print page_icp_dict[u'苏ICP备13052275号-5']
    updage_res('auth_icp', 'exact_unique', auth_icp_dict)
    updage_res('page_icp', 'exact_unique', page_icp_dict)
    # for icp in auth_icp_dict:
    #     if auth_icp_dict[icp] > 1:
    #         print icp, auth_icp_dict[icp]
    # print '\n==================================\n'
    # for icp in page_icp_dict:
    #     if page_icp_dict[icp] > 1:
    #         print icp, page_icp_dict[icp]


def vague_cmp(icp_res):
    '''
    模糊比对，只比对icp主体的号码
    '''
    auth_icp_dict = {}
    page_icp_dict = {}
    for item in icp_res:
        if item['auth_icp']['icp'] != '--':
            auth_icp = icp_num.get_icp_num(item['auth_icp']['icp']) # #形如港030577（省份 + 主编号）
            auth_icp_dict[auth_icp] = auth_icp_dict.get(auth_icp, 0) + 1
        if item['page_icp']['icp'] != '--' and item['page_icp']['icp'] != '-1':
            page_icp = icp_num.get_icp_num(item['page_icp']['icp']) # #形如港030577（省份 + 主编号）
            page_icp_dict[page_icp] = page_icp_dict.get(page_icp, 0) + 1
    auth_icp_dict['--'] = -1
    page_icp_dict['--'] = -1
    page_icp_dict['-1'] = -1
    updage_res('auth_icp', 'vague_unique', auth_icp_dict)
    updage_res('page_icp', 'vague_unique', page_icp_dict)
    # for icp in auth_icp_dict:
    #     if auth_icp_dict[icp] > 1:
    #         print icp, auth_icp_dict[icp]
    # print '\n==================================\n'
    # for icp in page_icp_dict:
    #     if page_icp_dict[icp] > 1:
    #         print icp, page_icp_dict[icp]


def updage_res(icp_type, unique_type, unique_res):
    '''
    param: icp_type: auth_icp / page_icp
    param: uniqye_type: exact_unique / vague_unique
    param: unique_res: 数量统计结果的字典{icp:num} / {icp_num: num}
    '''
    global collection
    icp_condition = icp_type + '.' + 'icp' # 'auth_icp.icp' / 'page_icp.icp'
    set_unique_type = icp_type + '.' + unique_type # 'auth_icp.exact_unique' / 'auth_icp.vague_unique' /'page_icp.exact_unique' / 'page_icp.vague_unique'
    if unique_type == 'exact_unique':
        for icp in unique_res:
            collection.update({icp_condition: icp}, {'$set': {set_unique_type:unique_res[icp]}},multi=True)
    else:
        ini_icp_res = list(collection.distinct(icp_condition)) # 选出该类型的icp
        for icp in ini_icp_res:
            icp_number = icp_num.get_icp_num(icp) # 形如港030577（省份 + 主编号）
            collection.update({icp_condition: icp}, {'$set': {set_unique_type:unique_res[icp_number]}},multi=True)




if __name__ == '__main__':
    # updage_res('auth_icp', 'exact_unique',{})
    icp_res = get_icps()
    vague_cmp(icp_res)
    # exact_cmp(icp_res)
