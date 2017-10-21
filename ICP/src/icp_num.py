# coding=utf-8
import re
'''
    功能： icp格式转化函数
'''


def get_icp_num(icp):
    '''
    将icp转化为形如港030577（省份 + 主编号）
    '''
    if u'ICP证' in icp:
        icp_num = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u8bc1]([\d]+)').findall(icp)
    else:
        icp_num = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp)
    if icp_num != []:#特殊cmp列出的几个
        icp = ''.join(list(icp_num[0])) #形如港030577（省份 + 主编号）
        return icp
    else:
        # 主要是诸如 粤B2-20090059-111 与 cmp.py中列举出的几个特例
        return icp #提取失败的，返回原icp
        # page_icp_dict[page_icp] = page_icp_dict.get(page_icp, 0) + 1
