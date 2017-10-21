# coding=utf-8
import tornado.web
from methods.db_operation import domain_oper_num

class domain_Oper_Handler(tornado.web.RequestHandler):
    def get(self):
        self.render('domain_oper.html')

    def post(self):
        domain_oper_data = domain_oper_num()
        print domain_oper_data
        print '---'
        self.write(domain_oper_data)
