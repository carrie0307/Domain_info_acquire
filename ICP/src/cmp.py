# coding=utf-8
from pymongo import *
import re

'''
最终遗留的几个特殊格式，但未影响比较结果
www.ihuaerjie.com ICP证 桂B2-20040022
www.qipaishequ.com -- ICP证&nbsp;桂B2-20040022
www.zqsjbzlk.com -- 京ICP证号京ICP备号京公网安备11010702000014
www.ourloto.com -- ICP证 桂B2-20040022
www.ihuaerjie.com -- ICP证&nbsp;桂B2-20040022
www.lzljluchun.com.cn -- ICP证：粤B2-20100355
'''

client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info



def get_domain_icp():
    global collection
    global domain_q
    res = collection.find({'cmp':0},{'auth_icp':True, 'page_icp':True })
    return list(res)


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
        elif item['auth_icp'] == '--' and item['page_icp'] == '-1':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':-1}})
        elif item['auth_icp'] != '--' and item['page_icp'] == '-1':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':-2}})
        else:
            # 港ICP证030577号、港ICP证0188188 等转化为030577、0188188
            # 将“沪ICP备09091848号-1”格式类型，全部转化为0909184
            # 读出的字符本身就算unicode，因此不必转换
            if u'ICP证' in item['auth_icp']:
                auth_icp = re.compile(u'ICP[\u8bc1]([\d]+)').findall(item['auth_icp'])[0]
            else:
                auth_icp = re.compile(u'[\u4e00-\u9fa5]{0,1}ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(item['auth_icp'])[0]
            if u'ICP证' in item['page_icp']:
                page_icp = re.compile(u'ICP[\u8bc1]([\d]+)').findall(item['page_icp'])[0]
            else:
                page_icp = re.compile(u'[\u4e00-\u9fa5]{0,1}ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(item['page_icp'])[0]
            if auth_icp == page_icp:
                collection.update({'_id': item['_id']}, {'$set': {'cmp':4}})
            else:
                collection.update({'_id': item['_id']}, {'$set': {'cmp':5}})




if __name__ == '__main__':
    domain_icp_list = get_domain_icp()
    cmp_icp(domain_icp_list)
    # print 'com over ...'
    # icp = u'沪ICP备09091848号-1'
    # auth_icp_1 = re.compile(u'[\u4e00-\u9fa5]{0,1}ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp)[0]
    # print auth_icp_1
    # www.trxqw.cn -- 京ICP证120511&#12288;京公网安备 11010802020321
    # www.dhxqw.cn -- 京ICP证120511&#12288;京公网安备 11010802020321
    # 港ICP证030577号
    # 港ICP证0188188
    # icp = u'京ICP证060962号-1'
    # page_icp = re.compile(u'ICP[\u8bc1]([\d]+)').findall(icp)[0]
    # print page_icp