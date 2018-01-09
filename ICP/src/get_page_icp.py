# coding=utf-8
'''
    功能： 从页面上获取icp信息

    注意： 运行时修改'collection = db.taiyuan_part_icp' 选择不同表中的域名获取
'''
import requests
import re
import urllib2
import Queue
import chardet
import StringIO
from pymongo import *
import threading
import time
from log import *

'''建立链接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info3

'''同步队列'''
domain_q = Queue.Queue()
html_q = Queue.Queue()
icp_q = Queue.Queue()


'''线程数量'''
thread_num = 20


def get_domains():
    '''
    功能：从数据库读取未获取页面icp信息的域名
    '''
    global collection
    global domain_q
    res = collection.find({'page_icp.icp':''},{'domain': True, '_id':False })
    for domain in list(res):
        print domain['domain']
        domain_q.put(str(domain[domain.keys()[0]]))


# urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
def pre_deal_html(req):
    '''
    功能：urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
    '''
    info = req.info()
    content = req.read()
    encoding = info.getheader('Content-Encoding')
    if encoding == 'gzip':
        buf = StringIO(content)
        gf = gzip.GzipFile(fileobj=buf)
        content = gf.read()
    charset = chardet.detect(content)['encoding']
    if charset != 'utf-8' and charset != None:
        content = content.decode(charset, 'ignore')
    return content


def download_htmlpage():
    '''
    功能：获取网页源代码，添加入html队列

    注： 页面无法访问的，置icp信息为-1
    '''
    global domain_q
    global html_q
    global icp_q
    while not domain_q.empty():
        domain = domain_q.get()
        url = 'http://' + domain
        try:
            resp = urllib2.urlopen(url)
            html = pre_deal_html(resp) # 处理编码
            html_q.put([domain, html])
        except Exception, e:
            icp_q.put([domain, '-1'])
            print str(e)
            logger.info("页面icp：获取html异常" + domain + '  ' + str(e) + '\n')
            print domain + "访问有误\n"
    print 'download over ...'


def get_page_icp():
    '''
    功能：获取页面上的icp信息，分三种情况进行处理：
        pattern1: 备案：粤ICP备11007122号-2 (500.com)
        pattern2: 京ICP证 030247号 (icbc)
        pattern2: 京ICP证000007 (sina)
        pattern3: 粤B2-20090059-111 (qq.com) （增值营业号）
    '''
    global html_q
    global icp_q
    while True:
        try:
            domain,html = html_q.get()
        except Queue.Empty:
            print 'get icp info over ...'
            break
        try:
            pattern1 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u5907][\d]{6,8}[\u53f7]*-*[\d]*)').findall(html)
            if pattern1 != []:
                icp = pattern1[0]
            else:
                pattern2 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u8bc1].*[\d]{6,8}[\u53f7])').findall(html)
                if pattern2 != []:
                    icp = pattern2[0]
                # 增值业务营业号
                else:
                    pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1}[A-B][1-2]-[\d]{6,8}-*[\d]*)').findall(html)
                    if pattern3 != []:
                        icp = pattern3[0]
                    else:
                        icp = '--'
            icp_q.put([domain, icp])
        except:
            logger.info("页面icp:从html提取icp异常" + domain + '  ' +'\n')
            print domain + "get icp WRONG\n"


def mongodb_save_icp():
    global icp_q
    global collection
    while True:
        try:
            domain,icp = icp_q.get()
        except Queue.Empty:
            print 'save over ... \n'
            break
        try:
            collection.update({'domain': domain}, {'$set': {'page_icp.icp':icp}})
            print 'saved: ' + domain + '  ' + icp
        except:
            logger.info("页面icp:存储异常" + domain + '  ' + '\n')
            print domain + "存储异常\n"


def single_test():
    resp = urllib2.urlopen('http://' + '177dapai.com')
    html = pre_deal_html(resp)
    pattern1 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u5907][\d]{6,8}[\u53f7]*-*[\d]*)').findall(html)
    if pattern1 != []:
    	print '================'
        icp = pattern1[0]
    else:
        pattern2 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u8bc1].*[\d]{6,8}[\u53f7])').findall(html)
        print '-------------'
        if pattern2 != []:
            icp = pattern2[0]
        # 增值业务营业号
        else:
            pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1}[A-B][1-2]-[\d]{6,8}-*[\d]*)').findall(html)
            print '333333333333333333'
            if pattern3 != []:
                icp = pattern3[0]
            else:
                icp = '--'
    print icp


if __name__ == '__main__':
    single_test()
    

    # get_domains()
    # get_html_td = []
    # for _ in range(thread_num):
    #     get_html_td.append(threading.Thread(target=download_htmlpage))
    # for td in get_html_td:
    #     td.start()
    # print 'get raw html ...\n'
    # time.sleep(5)
    # print 'get icp ...\n'
    # get_icp_td = threading.Thread(target=get_page_icp)
    # get_icp_td.start()
    # time.sleep(5)
    # print 'save icp ...\n'
    # save_db_td = threading.Thread(target=mongodb_save_icp)
    # save_db_td.start()
    # save_db_td.join()
