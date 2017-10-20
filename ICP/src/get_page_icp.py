# coding=utf-8
import requests
import re
import urllib2
import Queue
import chardet
import StringIO
from pymongo import *
import threading
import time

client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info2

domain_q = Queue.Queue()
html_q = Queue.Queue()
icp_q = Queue.Queue()

thread_num = 20

def get_domains():
    global collection
    global domain_q
    res = collection.find({'page_icp.icp':''},{'domain': True, '_id':False })
    for domain in list(res):
        domain_q.put(str(domain['domain']))

# urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
def pre_deal_html(req):
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
            print domain + "访问有误\n"
    print 'download over ...'


def get_page_icp():
    '''
    获取页面上的icp信息，分三种情况进行处理：
    pattern1: 备案：粤ICP备11007122号-2 (500.com)
    pattern2: 京ICP证 030247号 (icbc)
    pattern2: 京ICP证000007 (sina)
    pattern3: 粤B2-20090059-111 (qq.com)
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
                pattern2 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u8bc1].*[\d]{6,8})').findall(html)
                if pattern2 != []:
                    icp = pattern2[0]
                else:
                    icp = '--'
                # 这种方法提取后错误太多
                # else:
                #     pattern3 = re.compile(r'([\u4e00-\u9fa5]\w{1}[\d]*-[\d]{6,8}-*[\d]*)').findall(html)
                #     if pattern3 != []:
                #         icp = pattern3[0]
                #     else:
                #         icp = '--'
            icp_q.put([domain, icp])
        except:
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
            print domain + "存储异常\n"



if __name__ == '__main__':
    get_domains()
    get_html_td = []
    for _ in range(thread_num):
        get_html_td.append(threading.Thread(target=download_htmlpage))
    for td in get_html_td:
        td.start()
    print 'get raw html ...\n'
    time.sleep(5)
    print 'get icp ...\n'
    get_icp_td = threading.Thread(target=get_page_icp)
    get_icp_td.start()
    time.sleep(5)
    print 'save icp ...\n'
    save_db_td = threading.Thread(target=mongodb_save_icp)
    save_db_td.start()
    save_db_td.join()
