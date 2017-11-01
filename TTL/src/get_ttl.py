# encoding:utf-8
'''
    域名A记录和CNAME的TTL值获取
    流程：
        1. 向递归服务器请求顶级域的权威（eg. com -- c.gtld-servers.net 等）
        2. 向权威以此请求NS服务器
        3. 向NS请求实际域名的A记录和CNAME的TTL
        [

        向递归请求com的权威得到c.gtld-servers.net 等，
        向c.gtld-servers.net请求baidu.com的NS服务器记录
        （始终请求NS服务器，直到最后一级域名，即完整的域名）,
        向ns服务器请求最后一级域名的ttl值。可能先获取到的是cname的内容，则再cname开始以上过程，获取ip及ttl数值

        ]
'''

import DNS
import tldextract
import random
import Queue
import threading
import time
from log import *
from pymongo import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')



'''建立链接'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_ttl2

'''DNS请求'''
req_obj = DNS.Request()

'''相关参数'''
timeout = 10   # 超时时间
server = '222.194.15.253'

'''全局变量'''
g_cnames = []
g_cnames_ttl = []
g_ips = []
g_ips_ttl = []


res_q = Queue.Queue()



def get_ns(dm,ns_server):
    '''
    获取域名ns服务器
    '''
    # print 'dm:' + dm, 'ns: ' + ns_server
    ns = []
    dm_split = dm.split('.')
    for index in range(len(dm_split)):
        '''
        获取顺序：www.baidu.com , baidu.com ... 每当获取到后，便直接返回ns记录列表，若始终获取不到则返回空列表
        '''
        dm = '.'.join(dm_split[index:])
        # 连续获取三次（避免网络不稳定导致的获取不到）
        for _ in range(3):
            try:
                answer_obj = req_obj.req(name=dm, qtype=DNS.Type.NS, server=ns_server, timeout=timeout)

                if ns_server != server:
                    answers = answer_obj.authority
                else:
                    answers = answer_obj.answers
                for i in answers:
                    if i['typename'] == 'NS':
                        ns.append(i['data'])
                if ns: # 如果获取到了ns记录，则直接返回，该函数运行结束
                    return ns
                else:
                    break # ns记录为空，则从循环访问中退出，获取上一级域名进行获取ns
            # 有异常则在输出异常信息后，尝试再次请求
            except Exception, e:
                print dm + "获取NS异常 \n"
    return []


def get_A_TTL(dm, ns_server):
    '''
    获取ip的tll数值
    '''
    # print 'ns:' + ns_server, 'domain: ' + dm + '\n'
    ip,ip_ttl,cname,cname_ttl = [],[],[],[]
    for _ in range(3):
        try:
            ns_server = random.choice(ns_server)
            answer_obj = req_obj.req(name=dm, qtype=DNS.Type.A, server=ns_server, timeout=timeout)
            # 请求没有异常，则直接获取结果
            answers = answer_obj.answers
            for i in answers:
                r_data = i['data']
                r_ttl = i['ttl']
                if i['typename'] == 'A':
                    ip.append(r_data)
                    ip_ttl.append(r_ttl)
                elif i['typename'] == 'CNAME':
                    cname.append(r_data)
                    cname_ttl.append(r_ttl)

            # print ip,ip_ttl,cname,cname_ttl
            return ip,ip_ttl,cname,cname_ttl

        except Exception, e:
            print  ns_server
            print dm + "获取A记录ttl异常 \n"
            logger.info("获取A记录异常： " + dm + '  ' + str(e) + '\n')

    # 程序如果执行到这里，则说明始终有异常，返回空
    return [],[],[],[]





def get_domain_ttl(domain):
    '''
    获取域名ip和cname的ttl数值
    '''
    global g_cnames, g_cnames_ttl, g_ips, g_ips_ttl
    split_domain = domain.split('.')
    check_domain = ''
    for index in reversed(range(len(split_domain))):
        # 以www.baidu.com为例，check_name以此为com, baidu.com, www.baidu.com
        check_domain = '.'.join(split_domain[index:])
        if index == len(split_domain) - 1: # 获取顶级域(eg. com.)ns服务器
            ns = get_ns(check_domain,server)
        elif index == 0: #对完整的域名(www.baidu.com)获取A记录的ttl
            if ns != None:
                # print 'domain:' + check_domain
                # print ns
                # print '\n'
                ip,ip_ttl,cname,cname_ttl = get_A_TTL(check_domain, ns)
                if [ip,ip_ttl,cname,cname_ttl] == [[],[],[],[]]:
                    return False
                if cname:
                    g_cnames.extend(cname)
                    g_cnames_ttl.extend(cname_ttl)
                    get_domain_ttl(cname[-1])
                elif ip:
                    g_ips.extend(ip)
                    g_ips_ttl.extend(ip_ttl)
            else:
                # print 'domain:' + check_domain
                # print 'NS服务器序列为空...\n'
                return False
        else: # 对顶级域和完整域名之间的部分监测，例如baidu.com
            if ns != None and ns != []:
                auth_NS = random.choice(ns)
            else:
                return False
            ns = get_ns(check_domain,auth_NS)
    # print domain
    # print g_ips,g_ips_ttl,g_cnames,g_cnames_ttl
    return True
    # print g_ips,g_ips_ttl,g_cnames,g_cnames_ttl


def insert_data():
    '''
     ttl结果存储
    '''
    global collection
    global res_q
    while True:
        try:
            domain, g_ips,g_ips_ttl,g_cnames,g_cnames_ttl,flag = res_q.get(timeout=800)
        except:
            break
        try:
            if flag:
                collection.update({'domain': domain}, {'$set': {'cname_ttl.cnames':g_cnames, 'cname_ttl.ttl':g_cnames_ttl, 'ip_ttl.ips':g_ips,'ip_ttl.ttl':g_ips_ttl, 'flag':1}})
            else:
                collection.update({'domain': domain}, {'$set': {'cname_ttl.cnames':g_cnames, 'cname_ttl.ttl':g_cnames_ttl, 'ip_ttl.ips':g_ips,'ip_ttl.ttl':g_ips_ttl, 'flag':-1}})
        except:
            print domain + 'save wrong ...'
    print 'save over ...\n'


def main():
    '''
    主函数（ttl的获取与存储分不同的线程进行）
    '''
    global g_cnames, g_cnames_ttl, g_ips, g_ips_ttl
    global res_q

    domains = collection.find({'flag':0},{'domain': True, '_id':False })
    domains = list(domains)
    print 'save ttl res ...\n'
    save_db_td = threading.Thread(target=insert_data)
    save_db_td.start()
    for domain in domains:
        g_ips,g_ips_ttl,g_cnames,g_cnames_ttl = [],[],[],[]
        domain = domain['domain']
        # time.sleep(5) # 防止被ban
        res = get_domain_ttl(domain)
        if res:
            print domain
            print g_ips,g_ips_ttl,g_cnames,g_cnames_ttl
            res_q.put([domain, g_ips,g_ips_ttl,g_cnames,g_cnames_ttl,res])
        else:
            res_q.put([domain, g_ips,g_ips_ttl,g_cnames,g_cnames_ttl,res])

# answer_obj = req_obj.req(name='com.cn', server='d.dns.cn',timeout=15)
# if answer_obj.authority:
#     answers = answer_obj.authority
# else:
#     answers = answer_obj.answers
# for j in answers:
#     print j



if __name__ == '__main__':
    main()
    # for domain in ['www.026kj.com', 'f2a6e7f4c1901e0b.360safedns.com']:
        # get_domain_ttl(domain)
    # answer_obj = req_obj.req(name='qq.com', qtype=DNS.Type.NS, server="a.gtld-servers.net", timeout=timeout)
    # for i in answer_obj.authority:
    #     print i
