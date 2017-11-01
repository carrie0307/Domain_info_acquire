# coding:utf-8
import requests
import MySQLdb
import Queue
import time
import threading
from bs4 import BeautifulSoup
from log import *
import ip

domain_q = Queue.Queue()
res_q = Queue.Queue()


def get_domains():
    global domain_q
    conn = MySQLdb.connect("172.26.253.3", "root", "platform","malicious_domain_sys", charset = 'utf8')
    cur = conn.cursor()
    SQL = "select ID,domain from domain_index where ID in (select ID from malicious_info where flag like '%1' or flag like '%2') and ID not in (select ID from other_info)"
    # SQL = "select ID,domain from domain_index where ID in (select ID from malicious_info where flag like '%1' or flag like '%2') and ID in (select ID from other_info)"
    cur.execute(SQL)
    result = cur.fetchall()
    for item in result:
        domain_q.put([item[0], str(item[1])])
    cur.close()
    conn.close()



def parse_html(html):
    global domain_q
    try:
        if '非法的内容' in html:
            rank = '-1'
            return rank
        elif '非法字符' in html:
            rank = '-1'
            return rank
        else:
            soup = BeautifulSoup(html)
            for ul in soup.find_all('ul', {'class': 'result_top'}):
                if len(ul['class']) == 1:
                    if ul.find_all('li'): # 有时返回的页面排名为空
                        rank = ul.find_all('li')[5].string
                        return rank
                    else:
                        # 没有获取到排名，将该域名加入domain_q再获取一次(也说明此时代理无效)
                        print domain + "提取失败 ...\n"
                        domain_q.put([hash(domain), domain])
                        return False
        # print str(ID) + '  ' + str(rank) + '\n\n'
    except: # 一些获取的网页并非Alex排名获取网页，因此解析失败的再次加入domain队列等待新的获取
        domain_q.put([hash(domain), domain])
        print domain + "  获取失败...\n"
        return False


def get_html_content():
    proxy = ip.available_IP_q.get()
    global domain_q
    while True:
        try:
            ID,domain = domain_q.get()
        except:
            print '域名全部跑完...\n'
            break
        try:
            response = requests.get('http://alexa.chinaz.com/' + domain, proxies = proxy, timeout=5)
            html = response.text
            Rank = parse_html(html)
            if Rank == False: # 提取为空的时候也换ip
                print '排名提取有误，更换代理...\n'
                proxy = ip.available_IP_q.get()
            else:
                print '获取到排名...'
                res_q.put([hash(domain), Rank])
        except:
            print "获取出现异常，更换代理...\n"
            proxy = ip.available_IP_q.get()
    print 'get html over ...\n'



def commit_res():
    global res_q
    conn = MySQLdb.connect("172.26.253.3", "root", "platform","malicious_domain_sys", charset = 'utf8')
    cur = conn.cursor()
    while True:
        try:
            ID,rank = res_q.get(timeout = 600)
            print 'saving:  ' + str(ID) + '  ' + str(rank) + '\n\n'
        except:
            print '结果全部存储完...\n'
            break
        # SQL = "UPDATE other_info SET Alex = '%s' WHERE ID = %s" %(rank, ID)
        try:
            SQL = "INSERT INTO other_info(ID,Alex) VALUES(%s,'%s')" %(ID,rank)
            cur.execute(SQL)
            conn.commit()
        except Exception, e:
            print '结果存储有误...'
            logger.info(ID + str(e) + '\n')
    cur.close()
    conn.close()
    print 'commit over ...\n'


if __name__ == '__main__':
    ip.run_Getter()
    print '--------'
    time.sleep(30) # 这个时间很关键，确切说是从运行
    ip.ip_Verify()
    time.sleep(120)
    watcher = threading.Thread(target=ip.ip_watcher)
    watcher.setDaemon(True)
    watcher.start()
    get_html_td = []
    parse_html_td = []
    print 'whether run ... ??\n'
    if ip.available_IP_q.qsize() > 15:
        get_domains()
        print 'running \n'
        for i in range(5):
            get_html_td.append(threading.Thread(target=get_html_content))
        for td in get_html_td:
            td.start()
        time.sleep(60)
        save_db_td = threading.Thread(target=commit_res)
        save_db_td.start()
        save_db_td.join()
