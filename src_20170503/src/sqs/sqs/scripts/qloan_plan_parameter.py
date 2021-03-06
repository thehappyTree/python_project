# -*- coding:utf-8 -*-

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from objectquery import ObjectQuery
"""
贷款业务计划数参数
"""

class Query(ObjectQuery):

    def prepare_object(self):
        self.filterlist = ['BE_YEAR','org','SALE_CODE']
        filterstr,vlist = self.make_eq_filterstr()
        sql=u"""
        SELECT p.BDYEAR,p.BRANCH_CODE,b.BRANCH_NAME,p.THIRD_ORG_CODE,p.THIRD_ORG_NAME,p.MANAGER_CODE,f.NAME,p.ES_P_BASE/100.00,p.ES_P_TARGET/100.00,p.ES_C_BASE/100.00,p.ES_NC_BASE/100.00,p.AVE_BASE/100.00,p.AVE_TARGET/100.00,p.CRE_M_TARGET/100.00,p.CRE__H_TARGET/100.00,p.CRE__ES_C_H_TARGET,p.AQ_F_BASE/100.00,p.AV,p.CARD_BASE/100.00,p.CARD_TARGET/100.00,p.ID       
        FROM P_LOAN_NUM as p
        join BRANCH as b on p.branch_code=b.branch_code
        join F_User as f on p.manager_code=f.user_name
        WHERE 1=1 %s

         ORDER BY BDYEAR,BRANCH_CODE,THIRD_ORG_CODE,MANAGER_CODE,BRANCH_NAME,THIRD_ORG_NAME,MANAGER_NAME
        
        """%(filterstr)
        row = self.engine.execute(sql,vlist).fetchall()
        needtrans ={}
        i=0
        rowlist=[]

        for i in row:
            t = list(i[0:7])
            for j in i[7:15]:
                if j is None: j=0
                j = self.amount_trans_dec(j)
                t.append(j)
            temp = list(i[15:16])
            for j in i[16:17]:
                if j is None: j=0
                j=self.amount_trans_dec(j)
                temp.append(j)
            temp1 = list(i[17:18])
            for j in i[18:]:
                if j is None: j=0
                j = self.amount_trans_dec(j)
                temp1.append(j)
            t = t + temp + temp1
            rowlist.append(t)    
        return self.translate(rowlist,needtrans)

    def make_eq_filterstr(self):
        filterstr =""
        vlist = []
        for k,v in self.args.items():
            print k,v
            if k == 'login_teller_no':
                if self.deal_teller_query_auth(v) == True:
                    filterstr = filterstr+" and p.MANAGER_CODE = '%s'"%v
            elif k == 'login_branch_no':
                bb = self.deal_branch_query_auth(v)
                if bb != False:
                    filterstr = filterstr+" and p.BRANCH_CODE in ( %s )"%bb

            if v and k in self.filterlist:
                if k == 'org':
                    vvv = self.dealfilterlist(v)
                    filterstr = filterstr+" and p.BRANCH_CODE in ( %s) "%(vvv)
                elif k=='BE_YEAR':
                    if v != '':
                        filterstr = filterstr+" and p.bdYEAR = '%s'"%v
                elif k=='SALE_CODE':
                    if v !='':
                        filterstr = filterstr+" and p.MANAGER_CODE = '%s'"%v
 
        print filterstr,vlist
        return filterstr,vlist
    def column_header(self):
        return ["所属年份","网点编号","网点名称","客户经理编号","客户经理名称","对私考核基数","对私目标任务","纯公司类贷款考核基数","非纯公司类贷款考核基数","日均贷款增加额考核基数","日均贷款增加额目标任务","小额信用贷款余额占比目标(%)","小额信用贷款户数占比目标(%)","纯公司类贷款信用对公考核基数(户)","四级不良考核基数","分管行政村(村)","丰收两卡指标考核基数","丰收两卡指标考核目标任务","操作"]

    @property
    def page_size(self):
        return 15
