# -*- coding: UTF-8 -*-
import ip
import alexa
import threading



def main():
    ip.run_Getter()
    print '--------'
    time.sleep(30) # 这个时间很关键，确切说是从运行
    ip.ip_Verify()
    time.sleep(180)
    watcher = threading.Thread(target=ip.ip_watcher)
    watcher.setDaemon(True)
    watcher.start()
    get_html_td = []
    if ip.available_IP_q.qsize() > 15:
        for i in range(5):
            get_html_td.append(threading.Thread(target=alexa.get_html_content, args=(conn, cur)))
