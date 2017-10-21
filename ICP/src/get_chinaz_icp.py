# coding=utf-8
'''
    功能： 从站长之家获取ICP备案信息的权威结果

    注意： 运行时修改'collection = db.taiyuan_part_icp' 选择不同表中的域名获取
'''
import requests
import re
from pymongo import *
import time
import Queue
import threading
import ip
from log import *


'''建立连接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.taiyuan_part_icp

'''同步队列'''
domain_q = Queue.Queue()
html_q = Queue.Queue()
icp_q = Queue.Queue()

'''线程数量'''
thread_num = 10


def get_domains():
    '''
    功能:从数据库中读取未获取权威icp信息的域名，添加入域名队列
    '''
    global collection
    global domain_q
    res = collection.find({'auth_icp.icp':''},{'domain': True, '_id':False })
    for domain in list(res):
        domain_q.put(str(domain['domain']))


def get_raw_html():
    '''
    功能： 从站长之家获取包含域名icp信息的原始页面（注意由于被ban的问题，添加了获取代理），将html页面添加入队列
    '''
    global domain_q
    global html_q
    proxy = ip.available_IP_q.get() # 获取一个代理
    while not domain_q.empty():
        domain = domain_q.get()
        try:
            url = 'http://icp.chinaz.com/{query_domain}'.format(query_domain=domain)
            html = requests.get(url, proxies = proxy, timeout=5).text
            html_q.put([domain, html])
        except Exception, e: # 其他异常
            if "Connection" in str(e):
                domain_q.put(domain) # 被ban导致的获取失败，将域名加入队列，重新获取
                proxy = ip.available_IP_q.get()
            else:
                print str(e) + '===\n'
                logger.info("站长之家icp：获取html异常" + domain + '  ' + str(e) + '\n')
                print domain + "获取html异常"
                continue
    print 'domain queue is empty ...'


def get_icp_info():
    '''
    功能： 从html页面中提取icp信息，添加入icp队列
    '''
    global collection
    global html_q
    global icp_q
    while True:
        try:
            domain,html = html_q.get(timeout=100)
        except Queue.Empty:
            print 'get icp info over ...'
            break
        if "<h2>404" in html:
            #获取icp异常 eg. www.365bet.cd的查询结果
            icp = '--'
            continue
        try:
            content = re.compile(r'<p><font>(.+?)</font>').findall(html)
            if content == []:
                content = re.compile(r'<p class="tc col-red fz18 YaHei pb20">([^<]+?)<a href="javascript:" class="updateByVcode">').findall(html)
            icp = content[0]
            if icp == u"未备案或者备案取消，获取最新数据请":
                icp = '--'
            icp_q.put([domain, icp])
        except:
            logger.info("站长之家icp：html中提取icp异常" + domain + '  ' + '\n')
            print domain + "获取icp异常"


def mongodb_save_icp():
    '''
    功能：在mongo数据库中存储icp结果
    '''
    global icp_q
    global collection
    while True:
        try:
            domain,icp = icp_q.get(timeout=100)
        except Queue.Empty:
            print 'save over ... \n'
            break
        try:
            collection.update({'domain': domain}, {'$set': {'auth_icp.icp':icp}})
            print domain, icp
        except:
            logger.info("站长之家icp：存储异常" + domain + '  ' + '\n')
            print domain + "存储异常\n"



if __name__ == '__main__':
    ip.run_Getter()
    time.sleep(20) # 这个时间很关键，确切说是从运行
    ip.ip_Verify() # ip可用性验证
    time.sleep(90)
    watcher = threading.Thread(target=ip.ip_watcher) # 可用ip数量监测
    watcher.setDaemon(True)
    watcher.start()
    '''开始icp批量获取'''
    get_domains()
    get_html_td = []
    for _ in range(thread_num):
        get_html_td.append(threading.Thread(target=get_raw_html))
    for td in get_html_td:
        td.start()
    print 'get raw html ...\n'
    time.sleep(5)
    print 'get icp ...\n'
    get_icp_td = threading.Thread(target=get_icp_info)
    get_icp_td.start()
    time.sleep(5)
    print 'save icp ...\n'
    save_db_td = threading.Thread(target=mongodb_save_icp)
    save_db_td.start()
    save_db_td.join()
