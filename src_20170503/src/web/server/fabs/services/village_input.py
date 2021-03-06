# -*- coding: utf-8 -*-
"""
    yinsho.services.SeimService
    #####################

    yinsho SeimService module
"""
import datetime
from flask import json, g,current_app
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload_all
import xlrd
from ..base import utils
from ..model import Branch,Menu,User,UserBranch,Village_Input,Deposit_Plan_Parameter_Input,Loan_Plan_Parameter_Input,Ebank_Plan_Parameter_Input,TransactionCode,REPORT_MANAGER_DEP,QuarterTermSaleMbank,EtcData,UserGroup,Group,ManEbankAddPoints
import os, time, random,sys
from datetime import datetime,timedelta
from userreport import UserReport
from flask import current_app
ur = UserReport()
class VillageinputService():
    """ Target Service  """

    def save(self,**kwargs):
        self.ckyy = ['date_id','org_code','org_name','staff_code','staff_name','times']
        newdata =  kwargs.get('newdata')
        data ={}
        for k,v in newdata.items():
            if k in self.ckyy : data[k] = v
        g.db_session.add(Village_Input(**data))
        return u"ok" 

    def delete(self,**kwargs):
        self.ckyy = ['date_id','org_code','org_name','staff_code','staff_name','times','id']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(Village_Input).filter(Village_Input.id == pid).delete()
        return u"ok" 

    def update(self,**kwargs):
        self.ckyy = ['date_id','org_code','org_name','staff_code','staff_name','times','id']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        newdata.pop('id');
        data ={}
        g.db_session.query(Village_Input).filter(Village_Input.id == pid).update(newdata)
        return u"ok"  

    def sql2dict(self,sql,cursor):
        cursor.execute( sql )
        r=cursor.fetchone()
        d = {}
        while r:
            d[str(r[0])] = list(r)
            r = cursor.fetchone()
        return d

    """ 存款业务计划数参数 """

    def deposit_save(self,**kwargs):
        self.ckyy = ['third_org_code','manager_code','base','target','third_org_name','org_code','org_name','manager_name','dbyear']
        newdata =  kwargs.get('newdata')
        data ={}
        for k,v in newdata.items():
            if k in self.ckyy : 
                if k == 'base' :
                    v = long(float(v)*100)
                if k == 'target':
                    v = long(float(v)*100)
                data[k] = v
        dbyear = data['dbyear']
        manager_code=data['manager_code']
        manager_name=data['manager_name']
        try:
            fy = g.db_session.query(Deposit_Plan_Parameter_Input).filter(Deposit_Plan_Parameter_Input.dbyear==dbyear).filter(Deposit_Plan_Parameter_Input.manager_code==manager_code).first()
            if fy:
                err_message=u'该客户经理:'+str(manager_name)+u',编号:'+str(manager_code)+u'在'+str(dbyear)+u'已经存在'
                raise Exception(err_message)
            else:
                g.db_session.add(Deposit_Plan_Parameter_Input(**data))
        except Exception as e:
            current_app.logger.debug(e)
            return str(e) 
        return u"ok" 

    def deposit_delete(self,**kwargs):
        self.ckyy = ['id','dbyear','third_org_code','manager_code','base','target','third_org_name','org_code','org_name','manager_name']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(Deposit_Plan_Parameter_Input).filter(Deposit_Plan_Parameter_Input.id == pid).delete()
        return u"ok" 

    def deposit_update(self,**kwargs):
        self.ckyy = ['id','dbyear','third_org_code','manager_code','base','target','third_org_name','org_code','org_name','manager_name']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        newdata.pop('id');
        data ={}
        current_app.logger.debug("newbase",newdata['base'])
        if newdata['base']:
            newdata['base']=float(newdata['base'])*100
        if newdata['target']:
            newdata['target'] = float(newdata['target'])*100
        g.db_session.query(Deposit_Plan_Parameter_Input).filter(Deposit_Plan_Parameter_Input.id == pid).update(newdata)
        return u"ok"  
    def deposit_upload(self, filepath,):
        """
            批量录入
        """
        print '导入开始'
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            print nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            bill_targete_sign = ""
            list = []
        except Exception,e:
            return str(e)
        #数据重复检查
        source = []
        for r in range(1,nrows):
            try:
                dbyear = int(sheet.cell(r,0).value)
                strdbyear = str(dbyear)[:4]
                dbyear = int(strdbyear)
                temp_third_org_code = sheet.cell(r,1).value
                third_org_code = str(int(temp_third_org_code)).strip()
                third_org_name = sheet.cell(r,2).value
                #org_code = sheet.cell(r,3).value
                #org_name = sheet.cell(r,4).value
                temp_manager_code = sheet.cell(r,3).value
                manager_code = str(int(temp_manager_code)).strip()
                manager_name = sheet.cell(r,4).value
                base = long(float(sheet.cell(r,5).value)*100)
                target = long(float(sheet.cell(r,6).value)*100)
                current_app.logger.debug("2222222222222222222") 
                line = r + 1
                err_message = u'第' + str(line) + u'行,机构号:' + third_org_code
                if third_org_name.strip()=='':
                    raise Exception(err_message + u'请填写网点名称')
                if manager_name.strip()=='':
                    raise Exception(err_message + u'请填写客户经理名称')
                if base == None:
                    raise Exception(err_message + u'请填写考核基数')
                if target == None:
                    raise Exception(err_message + u'请填写目标任务')
                org_no_value=g.db_session.query(Branch).filter(Branch.branch_code==third_org_code).all()
                if not org_no_value:
                    raise Exception(err_message + u"不正确")
                
                if manager_code[0:3] != '966' :
                    err_message = err_message + u'客户经理号码不符合规则!'
                    raise Exception(err_message)

                if len(manager_code) !=7:
                    err_message = err_message + u'客户经理号码长度错误!'
                    raise Exception(err_message)

                to_teller_branch = g.db_session.execute("select bb.branch_code from user_branch ub, f_user fu, branch bb where bb.role_id = ub.branch_id and ub.user_id = fu.role_id and fu.user_name = '%s'"%(manager_code)).fetchone()
                if to_teller_branch is None:
                    err_message = err_message + u',客户经理号码错误'
                    raise Exception(err_message+to_teller_branch)

                if to_teller_branch[0] != third_org_code:
                    err_message = err_message + u',客户经理非本网点'
                    raise Exception(err_message)

                temp = {'dbyear':dbyear, 
                        'third_org_code':third_org_code, 
                        'third_org_name':third_org_name, 
                        #'org_code':org_code, 
                        #'org_name':org_name, 
                        'manager_code':manager_code, 
                        'manager_name':manager_name, 
                        'base':base,
                        'target':target
                }
                #return third_org_code.strip()
                #pos_value=g.db_session.query(Deposit_Plan_Parameter_Input).filter(Deposit_Plan_Parameter_Input.third_org_code==third_org_code.strip(),Deposit_Plan_Parameter_Input.third_org_name==third_org_name.strip()).all()
                #if pos_value:
                #     raise Exception(u"导入错误")
                #else:     
                key = str(dbyear).strip()+str(third_org_code).strip()+str(manager_code).strip()
                if key in source:
                   raise Exception(u'第'+str(r+1)+u'行,'+str(third_org_code)+u'网点编号，excel中已存在，请勿重复导入')
                else:
                    source.append(key)
                counter_work = g.db_session.query(Deposit_Plan_Parameter_Input).filter(Deposit_Plan_Parameter_Input.dbyear==temp['dbyear'],Deposit_Plan_Parameter_Input.third_org_code==temp['third_org_code'],Deposit_Plan_Parameter_Input.manager_code==temp['manager_code']).first()
                if counter_work:
                    current_app.logger.debug("数据库重复")
                    raise Exception(u"此年('%s'),网点(%s)已有客户经理('%s')有计划参数"%(temp['dbyear'],temp['third_org_code'],temp['manager_code']))
                else:
                    g.db_session.add(Deposit_Plan_Parameter_Input(**temp))
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        return u'导入成功'

    """ 贷款业务计划数参数 """

    def loan_save(self,**kwargs):
        self.ckyy = ['branch_code','third_org_code','manager_code','es_p_base','es_p_target','es_c_base','es_nc_base','ave_base','ave_target','cre_m_target','cre__h_target','cre__es_c_h_target','aq_f_base','av','card_base','card_target','branch_name','third_org_name','manager_name','bdyear']
        newdata =  kwargs.get('newdata')
        data ={}
        try:
                for k,v in newdata.items():
                    if k in self.ckyy : 
                        if k == 'es_p_base' :
                            v = long(float(v)*100)
                        if k == 'es_c_base':
                            v = long(float(v)*100)
                        if k == 'es_nc_base':
                            v = long(float(v)*100)
                        if k == 'ave_base':
                            v = long(float(v)*100)
                        if k == 'ave_target':
                            v = long(float(v)*100)
                        if k == 'cre_m_target':
                            v = long(float(v)*100)
                        if k == 'cre__h_target':
                            v = long(float(v)*100)
                        if k == 'cre__es_c_h_target':
                            v = long(float(v))
                        if k == 'aq_f_base':
                            v = long(float(v)*100)
                        if k == 'card_base':
                            v = long(float(v)*100)
                        if k == 'card_target':
                            v = long(float(v)*100)
                        if k == 'bdyear':
                            v=v[:4]
                        data[k] = v
                bdyear=newdata['bdyear']
                current_app.logger.debug(type(bdyear))
                manager_code=newdata['manager_code']
                current_app.logger.debug(bdyear)
                current_app.logger.debug(manager_code)
                fy = g.db_session.query(Loan_Plan_Parameter_Input).filter(Loan_Plan_Parameter_Input.manager_code==manager_code,Loan_Plan_Parameter_Input.bdyear==bdyear).first()
                fx = g.db_session.query(User).join(UserGroup,UserGroup.user_id==User.role_id).join(Group,Group.id==UserGroup.group_id).filter(User.user_name==manager_code).filter(Group.group_name=='客户经理').filter(Group.group_type_code=='2000').first()
                if not fx:
                    current_app.logger.debug("该员工不是客户经理")
                    raise Exception(u'该员工不是客户经理！')
                if fy:
                    current_app.logger.debug("该客户经理已添加")
                    raise Exception(u'该客户经理已添加！')
                g.db_session.add(Loan_Plan_Parameter_Input(**data))
                current_app.logger.debug("添加列")
                return u"添加成功" 
        except Exception, e:
            return str(e)

    def loan_delete(self,**kwargs):
        self.ckyy = ['branch_code','third_org_code','manager_code','es_p_base','es_p_target','es_c_base','es_nc_base','ave_base','ave_target','cre_m_target','cre__h_target','cre__es_c_h_target','aq_f_base','av','card_base','card_target','branch_name','third_org_name','manager_name','id','bdyear']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(Loan_Plan_Parameter_Input).filter(Loan_Plan_Parameter_Input.id == pid).delete()
        return u"ok" 

    def loan_update(self,**kwargs):
        self.ckyy = ['branch_code','third_org_code','manager_code','es_p_base','es_p_target','es_c_base','es_nc_base','ave_base','ave_target','cre_m_target','cre__h_target','cre__es_c_h_target','aq_f_base','av','card_base','card_target','branch_name','third_org_name','manager_name','id','bdyear']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        newdata.pop('id');
        data ={}
        if newdata['es_p_base']:
            newdata['es_p_base']=float(newdata['es_p_base'])*100
        if newdata['es_p_target']:
            newdata['es_p_target']=float(newdata['es_p_target'])*100
        if newdata['es_c_base']:
            newdata['es_c_base']=float(newdata['es_c_base'])*100
        if newdata['es_nc_base']:
            newdata['es_nc_base']=float(newdata['es_nc_base'])*100
        if newdata['ave_base']:
            newdata['ave_base']=float(newdata['ave_base'])*100
        if newdata['ave_target']:
            newdata['ave_target']=float(newdata['ave_target'])*100
        if newdata['cre_m_target']:
            newdata['cre_m_target']=float(newdata['cre_m_target'])*100
        if newdata['cre__h_target']:
            newdata['cre__h_target']=float(newdata['cre__h_target'])*100
        if newdata['cre__es_c_h_target']:
            newdata['cre__es_c_h_target']=float(newdata['cre__es_c_h_target'])
        if newdata['aq_f_base']:
            newdata['aq_f_base']=float(newdata['aq_f_base'])*100
        if newdata['card_base']:
            newdata['card_base']=float(newdata['card_base'])*100
        if newdata['card_target']:
            newdata['card_target']=float(newdata['card_target'])*100
        g.db_session.query(Loan_Plan_Parameter_Input).filter(Loan_Plan_Parameter_Input.id == pid).update(newdata)
        return u"ok"  
    

    def loan_upload(self, filepath,):
        """
            批量录入
        """
        print '导入开始'
        current_app.logger.debug("sssssssssssssssssssssssssssssssssssssssssssssss")
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            print nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            bill_targete_sign = ""
            list = []
        except Exception,e:
            return str(e)
        #数据重复检查
        source = []
        for r in range(1,nrows):
            try:
                by = str(sheet.cell(r,0).value)[:4]
                bdyear = int(by)
                
                temp_branch_code = sheet.cell(r,1).value
                branch_code = str(int(temp_branch_code)).strip()
                branch_name = sheet.cell(r,2).value
                temp_manager_code = sheet.cell(r,3).value
                manager_code = str(int(temp_manager_code)).strip()
                manager_name = sheet.cell(r,4).value
                es_p_base = long(float(str(''.join((str(sheet.cell(r,5).value).split(',')))))*100)
                es_p_target =long(float(str(''.join((str(sheet.cell(r,6).value).split(',')))))*100)
                es_c_base = long(float(str(''.join((str(sheet.cell(r,7).value).split(',')))))*100)
                es_nc_base = long(float(str(''.join((str(sheet.cell(r,8).value).split(',')))))*100)
                ave_base = long(float(str(''.join((str(sheet.cell(r,9).value).split(',')))))*100)
                ave_target= long(float(str(''.join((str(sheet.cell(r,10).value).split(',')))))*100)
                cre_m_target= long(float(str(''.join((str(sheet.cell(r,11).value).split(',')))))*100)
                cre__h_target= long(float(str(''.join((str(sheet.cell(r,12).value).split(',')))))*100)
                cre__es_c_h_target= long(float(str(''.join((str(sheet.cell(r,13).value).split(','))))))
                aq_f_base = long(float(str(''.join((str(sheet.cell(r,14).value).split(',')))))*100)
                av = str(int(sheet.cell(r,15).value)).strip()
                card_base = long(float(str(''.join((str(sheet.cell(r,16).value).split(',')))))*100)
                card_target = long(float(str(''.join((str(sheet.cell(r,17).value).split(',')))))*100)
                current_app.logger.debug('uploadupload')
                line = r + 1
                err_message = u'第' + str(line) + u'行,机构号:' + branch_code

                if branch_code.strip()=='':
                    raise Exception(err_message + u'请填写支行编号')
                if manager_code.strip()=='':
                    raise Exception(err_message + u'请填写客户经理编号')
                if es_p_base==None or es_p_target==None or es_nc_base==None or ave_target==None or ave_base==None or cre__es_c_h_target==None or cre__h_target==None or cre_m_target==None or card_target==None or card_base==None:
                    raise Exception(err_message + u'请填写完整数据')

                org_no_value=g.db_session.query(Branch).filter(Branch.branch_code==branch_code).all()
                if not org_no_value:
                    raise Exception(err_message + u"不正确")
                
                if manager_code[0:3] != '966' :
                    err_message = err_message + u'客户经理号码不符合规则!'
                    raise Exception(err_message)

                if len(manager_code) !=7:
                    err_message = err_message + u'客户经理号码长度错误!'
                    raise Exception(err_message)

                to_teller_branch = g.db_session.execute("select bb.branch_code from user_branch ub, f_user fu, branch bb where bb.role_id = ub.branch_id and ub.user_id = fu.role_id and fu.user_name = '%s'"%(manager_code)).fetchone()
                if to_teller_branch is None:
                    err_message = err_message + u',客户经理号码错误'
                    raise Exception(err_message+to_teller_branch)

                if to_teller_branch[0] != branch_code:
                    err_message = err_message + u',客户经理非本网点'
                    raise Exception(err_message)


                temp = {'bdyear':bdyear, 
                        'branch_code':branch_code, 
                        'branch_name':branch_name, 
                        'manager_code':manager_code, 
                        'manager_name':manager_name, 
                        'es_p_base':es_p_base,
                        'es_p_target':es_p_target,
                        'es_c_base':es_c_base,
                        'es_nc_base':es_nc_base,
                        'ave_base':ave_base,
                        'ave_target':ave_target,
                        'cre_m_target':cre_m_target,
                        'cre__h_target':cre__h_target,
                        'cre__es_c_h_target':cre__es_c_h_target,
                        'aq_f_base':aq_f_base,
                        'av':av,
                        'card_base':card_base,
                        'card_target':card_target
                }
                #pos_value=g.db_session.query(Loan_Plan_Parameter_Input).filter(Loan_Plan_Parameter_Input.branch_code==branch_code.strip(),Loan_Plan_Parameter_Input.branch_name==branch_name.strip()).all()
                #return pos_value 
                #if not  pos_value:
                #     raise Exception(u"导入错误")
                #else:  
                key=str(bdyear).strip()+str(branch_code).strip()+str(manager_code).strip()
                if key in source:
                    raise Exception(u'第'+str(r+1)+u'行'+u'在'+str(bdyear)+u',网点号：'+str(branch_code)+u',客户经理：'+str(manager_code)+u',excel已存在，请勿重复导入')
                else:
                    source.append(key)
                counter_work = g.db_session.query(Loan_Plan_Parameter_Input).filter(Loan_Plan_Parameter_Input.bdyear==temp['bdyear'],Loan_Plan_Parameter_Input.branch_code==temp['branch_code'],Loan_Plan_Parameter_Input.manager_code==temp['manager_code']).first()
                if counter_work:
                    raise Exception(u"此年('%s'),支行(编号'%s')已有客户经理(编号'%s')已经添加贷款计划参数"%(temp['bdyear'],temp['branch_code'],temp['manager_code']))
                g.db_session.add(Loan_Plan_Parameter_Input(**temp))
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        return u'导入成功'

    """ 电子银行业务计划数参数 """

    def ebank_save(self,**kwargs):
        print kwargs
        self.ckyy = ['YEAR','third_org_code','manager_code','base','tar_sj','tar_wy','tar_pos','tar_etc','tar_epay','tar_zn','tar_third','third_org_name','manager_name','org_code','org_name']
        newdata =  kwargs.get('newdata')
        data ={}
        for k,v in newdata.items():
            if k in self.ckyy : data[k] = v
        print data
        g.db_session.add(Ebank_Plan_Parameter_Input(**data))
        return u"ok" 

    def ebank_delete(self,**kwargs):
        self.ckyy = ['YEAR','third_org_code','manager_code','base','tar_sj','tar_wy','tar_pos','tar_etc','tar_epay','tar_zn','tar_third','third_org_name','manager_name','org_code','org_name']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(Ebank_Plan_Parameter_Input).filter(Ebank_Plan_Parameter_Input.id == pid).delete()
        return u"ok" 

    def ebank_update(self,**kwargs):
        self.ckyy = ['YEAR','third_org_code','manager_code','base','tar_sj','tar_wy','tar_pos','tar_etc','tar_epay','tar_zn','tar_third','third_org_name','manager_name','org_code','org_name']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        newdata.pop('id');
        data ={}
        g.db_session.query(Ebank_Plan_Parameter_Input).filter(Ebank_Plan_Parameter_Input.id == pid).update(newdata)
        return u"ok"  
    

    def ebank_upload(self, filepath,):
        """
            批量录入
        """
        print '导入开始'
        try:
            #today=datetime.date.today()
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            print nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            bill_targete_sign = ""
            list = []
        except Exception,e:
            return str(e)
        for r in range(1,nrows):
            try:
                YEAR = int(sheet.cell(r,0).value)
                temp_third_org_code = sheet.cell(r,1).value
                third_org_code = str(int(temp_third_org_code)).strip()
                third_org_name = sheet.cell(r,2).value
                temp_manager_code = sheet.cell(r,3).value
                manager_code = str(int(temp_manager_code)).strip()
                manager_name = sheet.cell(r,4).value
                tar_sj= int(sheet.cell(r,5).value)
                tar_wy =int(sheet.cell(r,6).value)
                tar_pos=int(sheet.cell(r,7).value)
                tar_etc=int(sheet.cell(r,8).value)
                tar_epay=int(sheet.cell(r,9).value)
                tar_zn=int(sheet.cell(r,10).value)

                line = r + 1
                err_message = u'第' + str(line) + u'行,机构号:' + third_org_code

                if third_org_name.strip()=='':
                    raise Exception(err_message + u'请填写网点名称')
                if manager_name.strip()=='':
                    raise Exception(u'请填写客户经理名称')
                if tar_zn==None or tar_epay==None or tar_etc==None or tar_pos==None or tar_wy==None or tar_sj==None:
                    raise Exception(err_message + u'请填写完整数据')

                org_no_value=g.db_session.query(Branch).filter(Branch.branch_code==third_org_code).all()
                if not org_no_value:
                    raise Exception(err_message + u"不正确")
                
                if manager_code[0:3] != '966' :
                    err_message = err_message + u'客户经理号码不符合规则!'
                    raise Exception(err_message)

                if len(manager_code) !=7:
                    err_message = err_message + u'客户经理号码长度错误!'
                    raise Exception(err_message)

                to_teller_branch = g.db_session.execute("select bb.branch_code from user_branch ub, f_user fu, branch bb where bb.role_id = ub.branch_id and ub.user_id = fu.role_id and fu.user_name = '%s'"%(manager_code)).fetchone()
                if to_teller_branch is None:
                    err_message = err_message + u',客户经理号码错误'
                    raise Exception(err_message+to_teller_branch)

                if to_teller_branch[0] != third_org_code:
                    err_message = err_message + u',客户经理非本网点'
                    raise Exception(err_message)


                temp = {'YEAR':YEAR, 
                        'third_org_code':third_org_code, 
                        'third_org_name':third_org_name, 
                        'manager_code':manager_code, 
                        'manager_name':manager_name, 
                        'tar_sj':tar_sj,
                        'tar_wy':tar_wy,
                        'tar_pos':tar_pos,
                        'tar_etc':tar_etc,
                        'tar_epay':tar_epay,
                        'tar_zn':tar_zn
                }
                #pos_value=g.db_session.query(Ebank_Plan_Parameter_Input).filter(Ebank_Plan_Parameter_Input.third_org_code==third_org_code.strip(),Ebank_Plan_Parameter_Input.third_org_name==third_org_name.strip()).all()
                #return pos_value
                #if pos_value:
                #     raise Exception(u"导入错误")
                #else:     
                g.db_session.add(Ebank_Plan_Parameter_Input(**temp))
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        return u'导入成功'


    """ 交易码折算率"""

    def transaction_save(self,**kwargs):
        newdata = kwargs.get('newdata')
        newdata['begin_dt']=int(newdata['begin_dt'])
        newdata['end_dt']=int(newdata['end_dt'])
        tran_id=g.db_session.query(TransactionCode).filter(TransactionCode.tranid==newdata['tranid']).first()
        if tran_id:
            raise Exception(u"已有此交易码,请前去编辑")
        g.db_session.add(TransactionCode(**newdata))
        g.db_session.commit()
        g.db_session.execute("delete from F_TRADE_DISCOUNT where tranid= '%s'"%(newdata['tranid']) )
        g.db_session.execute("""
        insert into F_TRADE_DISCOUNT 
        select d.id date_id,TRANID,TRANNAME,DISCOUNT from
        TRANSACTION_CODE f , d_date d
        where f.BEGIN_DT<=d.id and f.END_DT>=d.id  and f.tranid ='%s' """%(newdata['tranid']) )
        return u"添加成功" 

    def transaction_delete(self,**kwargs):
        self.ckyy = ['tranid','tranname','begin_dt','end_dt','discount']
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(TransactionCode).filter(TransactionCode.id == pid).delete()
        g.db_session.commit()
        g.db_session.execute(" delete from F_TRADE_DISCOUNT where tranid= '%s'"%(newdata['tranid']))
        return u"删除成功"

    def daycalc(self,etldate,days):
        if etldate == 0:
            return 0
        s=str(etldate)
        d1=datetime(int(s[0:4]),int(s[4:6]),int(s[6:8])) + timedelta(days)
        s=str(d1.strftime('%Y%m%d'))
        return s

    def transaction_update(self,**kwargs):
        newdata = kwargs.get('newdata')
        begin_dt=newdata['begin_dt']
        end_dt=newdata['end_dt']
        pid=newdata['id']
        newdata['begin_dt']=int(newdata['begin_dt'])
        newdata['end_dt']=int(newdata['end_dt'])
        g.db_session.query(TransactionCode).filter(TransactionCode.id == pid).update(newdata)
        g.db_session.commit()
        g.db_session.execute("delete from F_TRADE_DISCOUNT where tranid= '%s'"%(newdata['tranid']) )
        g.db_session.execute("""
        insert into F_TRADE_DISCOUNT 
        select d.id date_id,TRANID,TRANNAME,DISCOUNT from
        TRANSACTION_CODE f , d_date d
        where f.BEGIN_DT<=d.id and f.END_DT>=d.id  and f.tranid ='%s' """%(newdata['tranid']) )

        return u"更新成功"
    

    def transaction_upload(self, filepath,):
        """
            批量录入
        """
        print '导入开始'
        try:
            #today=datetime.date.today()
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            print nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            bill_targete_sign = ""
            list = []
        except Exception,e:
            return str(e)
        trand_id_excel=[]
        trand_id_data=[]
        tranid_list=g.db_session.query(TransactionCode.tranid).all()
        for i in tranid_list:
            trand_id_data.append(str(i[0]))
        try:
            for r in range(1,nrows):
                temp_tranid= sheet.cell(r,0).value
                current_app.logger.debug(temp_tranid)
                tranid= str(temp_tranid).replace('.0',"").replace('.00',"").strip()
                tranname= sheet.cell(r,1).value
                begin_dt= str(sheet.cell(r,2).value).replace('.0',"").replace('.00',"").strip()
                end_dt = str(sheet.cell(r,3).value).replace('.0',"").replace('.00',"").strip()
                discount= sheet.cell(r,4).value
                
                line = r + 1
                err_message = u'第' + str(line) + u'行' 

                if tranid =="":
                    raise Exception(err_message + u'请填写交易码')
                err_message = u'第' + str(line) + u'行' + tranid

                if tranid in trand_id_excel:
                    raise Exception(err_message + u'在导入的excel中出现重复的数据')
                else:
                    trand_id_excel.append(tranid)
                if tranid in trand_id_data:
                    raise Exception(err_message + u'交易码已存在,只能编辑,不能添加')
                if ( not str(begin_dt).replace('.0',"").replace('.00',"").isdigit()) or len(str(int(begin_dt)))!=8:
                    raise Exception(err_message + u"开始时间有误")

                if (not str(end_dt).replace('.0',"").replace('.00',"").isdigit()) or len(str(int(begin_dt)))!=8:
                    raise Exception(err_message + u"开始时间有误")


                if tranname.strip()=='':
                    raise Exception(err_message + u'请填写交易名称')
                if begin_dt ==None or end_dt==None or discount==None or begin_dt =="" or end_dt=="" or discount==""  :
                    raise Exception(err_message + u'请填写完整数据')
                
                temp = {'tranid':tranid, 
                        'tranname':tranname,
                        'begin_dt':begin_dt,
                        'end_dt':end_dt,
                        'discount':discount
                }
                temp['begin_dt']=int(temp['begin_dt'])
                temp['end_dt']=int(temp['end_dt'])
                g.db_session.add(TransactionCode(**temp))
        except Exception,e:    
            g.db_session.rollback()
            print Exception,':',e
            return u'第'+str(r+1)+u'行有问题:'+str(e)
        else:
            g.db_session.commit()
            g.db_session.execute("delete from  F_TRADE_DISCOUNT ")
            g.db_session.execute("""
            insert into F_TRADE_DISCOUNT 
            select d.id date_id,TRANID,TRANNAME,DISCOUNT from
            TRANSACTION_CODE f , d_date d
            where f.BEGIN_DT<=d.id and f.END_DT>=d.id 
            """)
        return u'导入成功'



    def deposit_try(self, filepath,):
        """
            批量录入
        """
        print '导入开始'
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            #print nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            bill_targete_sign = ""
            list = []
        except Exception,e:
            return str(e)
        for r in range(2,nrows):
            try:
                date_id= sheet.cell(r,0).value
                temp_org_code= sheet.cell(r,1).value
                org_code= str(str(temp_org_code)).strip()
                temp_sale_code= sheet.cell(r,3).value
                sale_code= str(str(temp_sale_code)).strip()
                temp_try_last_avg_sal= (sheet.cell(r,7).value) 
                try_last_avg_sal= (float(((''.join(str(temp_try_last_avg_sal).split(','))))) * 100000000 *12 ) 
                temp_last_avg_sal= (sheet.cell(r,7).value) 
                last_avg_sal= (float(((''.join(str(temp_last_avg_sal).split(',')))))*100000000 *12  )
                temp_try_add_avg_sal=(sheet.cell(r,8).value)
                try_add_avg_sal=(float(((''.join(str(temp_try_add_avg_sal).split(',')))))*100000000)
                temp_add_avg_sal=(sheet.cell(r,8).value)
                add_avg_sal=( float(((''.join(str(temp_add_avg_sal).split(',')))))*100000000)
                #return add_avg_sal

                line = r + 1
                err_message = u'第' + str(line) + u'行' + sale_code 

                if try_add_avg_sal== None :
                    raise Exception(err_message + u'请填写存量日均存款试算效酬')
                if try_add_avg_sal==None :
                    raise Exception(err_message + u'请填写新增日均存款试算效酬')
                
                #return temp_last_avg_sal
                temp = {'DATE_ID':date_id, 
                        'SALE_CODE':sale_code,
                        'TRY_LAST_AVG_SAL':try_last_avg_sal,
                        'LAST_AVG_SAL':last_avg_sal,
                        'TRY_ADD_AVG_SAL':try_add_avg_sal,
                        'ADD_AVG_SAL':add_avg_sal
                }
                g.db_session.query(REPORT_MANAGER_DEP).filter(REPORT_MANAGER_DEP.DATE_ID== date_id).filter(REPORT_MANAGER_DEP.SALE_CODE==sale_code.strip()).update(temp)
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        return u'导入成功'

    def quarter_term_sale_mbank_base_upload(self, filepath):
        """
            批量录入
        """
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            if nrows in [0,1]:
                raise Exception(u"警告:文件为空")
            date_id = int(sheet.cell(2,0).value)
            g.db_session.query(QuarterTermSaleMbank).filter(QuarterTermSaleMbank.date_id == date_id).delete()
        except Exception,e:
            g.db_session.rollback()
            return str(e)


        for r in range(2,nrows):
            try:
                #考核日期   机构号  机构名称    客户内码    账号    交易笔数    客户名称    客户号  电话号码
                date_id = int(sheet.cell(r,0).value)
                org_code = str(sheet.cell(r,1).value).strip().replace(".0","")
                cust_in_no = str(sheet.cell(r,3).value).strip().replace(".0","") 
                account_no = str(sheet.cell(r,4).value).strip().replace(".0","") 
                cnt = int(sheet.cell(r,5).value)
                cust_name = str(sheet.cell(r,6).value)
                cust_no = str(sheet.cell(r,7).value).strip().replace(".0","") 
                tel_no = str(sheet.cell(r,8).value).strip().replace(".0","") 
                print date_id, org_code, cust_in_no, account_no, cnt, cust_name, cust_no, tel_no

                line = r + 1
                err_message = u'第' + str(line) + u'行,机构号:' + org_code

                if date_id is None:
                    raise Exception(err_message + u'请填写考核日期')
                if org_code.strip()=='':
                    raise Exception(err_message + u'请填写机构号')
                if cust_in_no.strip()=='':
                    raise Exception(err_message + u'请填写内码')
                if cust_no.strip()=='':
                    raise Exception(err_message + u'请填写客户号')

                temp = {'date_id':date_id, 
                        'org_no':org_code, 
                        'cust_in_no':cust_in_no, 
                        'cust_no':cust_no, 
                        'cust_name':cust_name, 
                        'account_no':account_no, 
                        'tel_no':tel_no, 
                        'cnt':cnt, 
                }
                g.db_session.add(QuarterTermSaleMbank(**temp))
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        return u'导入成功'

    def etc_data_upload(self, filepath):
        """
            批量录入
        """
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            if nrows in [0,1,2]:
                raise Exception(u"警告:文件为空")
            date_id = int(sheet.cell(2,0).value)
        except Exception,e:
            g.db_session.rollback()
            return str(e)

        sql = """ select cust_net_no, e.* from etc_data e """
        connection  = g.db_session.bind.raw_connection()
        cursor  = connection.cursor()
        tbs = self.sql2dict(sql,cursor) #车牌号:

        all_msg = []
        souser = []
        for r in range(2,nrows):
            try:
                #签约日期   车牌号  车主    卡号    卡主    签约机构    签约柜员    归属柜员号  归属机构号

                date_id = int(sheet.cell(r,0).value)
                cust_net_no = str(sheet.cell(r,1).value)
                cust_name = str(sheet.cell(r,2).value)
                card_no= str(int(sheet.cell(r,3).value))
                card_name = str(sheet.cell(r,4).value)
                sign_org_no = str(sheet.cell(r,5).value).replace('.0','')
                sign_teller_no = str(sheet.cell(r,6).value).replace('.0','')
                teller_no = str(sheet.cell(r,7).value).replace('.0','')
                org_no =  str(sheet.cell(r,8).value).replace('.0','')
                print date_id, cust_net_no, cust_name, card_no, card_name, sign_org_no, sign_teller_no, org_no, teller_no

                line = r + 1
                err_message = u'第' + str(line) + u'行,车牌号:' + cust_net_no 

                tb = tbs.get(str(cust_net_no))
                if tb is not None :
                    err_message = err_message + u',车牌号重复'
                    raise Exception(err_message)

                if len(str(date_id)) != 8 :
                    raise Exception(err_message + u'请填写正确的签约日期')
                if cust_net_no.strip()=='':
                    raise Exception(err_message + u'请填写车牌号')
                if cust_name.strip()=='':
                    raise Exception(err_message + u'请填写车主')
                if len(card_no) != 16:
                    raise Exception(err_message + u'请填写正确的信用卡卡号')
                if card_name.strip()=='':
                    raise Exception(err_message + u'请填写卡主')
                if sign_org_no.strip()=='':
                    raise Exception(err_message + u'请填写签约机构号')
                if sign_teller_no.strip()=='':
                    raise Exception(err_message + u'请填写签约柜员')
                if org_no.strip()=='':
                    raise Exception(err_message + u'请填写归属机构号')

                sorg = g.db_session.query(Branch).filter(Branch.branch_code==sign_org_no,Branch.branch_level<>'支行').first()
                if not sorg:
                    return u'第'+str(r+1)+u'行,机构'+str(sign_org_no)+u'请填写正确的签约机构！'
                org = g.db_session.query(Branch).filter(Branch.branch_code==org_no,Branch.branch_level<>'支行').first()
                if not org:
                    return u'第'+str(r+1)+u'行,机构'+str(org_no)+u'请填写正确的归属机构号！'

                if isinstance(sign_org_no,(int, float)):
                    sign_org_no = str(int(sign_org_no))

                if isinstance(sign_teller_no,(int, float)):
                    sign_teller_no = str(int(sign_teller_no))

                if isinstance(org_no,(int, float)):
                    org_no = str(int(org_no))

                if isinstance(teller_no,(int, float)):
                    teller_no = str(int(teller_no))

                temp = {'date_id':date_id, 
                        'cust_net_no':cust_net_no, 
                        'cust_name':cust_name, 
                        'card_no':card_no, 
                        'card_name':card_name, 
                        'sign_org_no':sign_org_no, 
                        'sign_teller_no':sign_teller_no, 
                        'org_no':org_no, 
                        'teller_no':teller_no, 
                }
                all_msg.append(temp)
                key = str(cust_net_no)
                if key in souser:
                    return u'第'+str(r+1)+u'行车牌号'+str(cust_net_no)+u'已经存在excel中,请仔细核对'
                else:
                    souser.append(key)
            except ValueError, e:
                g.db_session.rollback()
                return u'第'+str(r + 1) + u'行有错误'+str(e)+u"请检查年份是否正确,信用卡卡号是否正确"
            except IndexError,e:
                g.db_session.rollback()
                return u'第'+str(r+1)+u'行有错误,请检查列数'
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        for i in range(0,len(all_msg)):
            g.db_session.add(EtcData(**all_msg[i]))
        return u'导入成功'

    def etc_data_delete(self,**kwargs):
        newdata =  kwargs.get('newdata')
        pid = newdata.get('id')
        g.db_session.query(EtcData).filter(EtcData.id == pid).delete()
        return u"删除成功" 

    def etc_data_edit(self,**kwargs):
        newdata =  kwargs.get('etc_update')
        pid = newdata.get('id')
        newdata.pop('id');

        org_no = newdata.get('org_no')
        org = g.db_session.query(Branch).filter(Branch.branch_code==org_no,Branch.branch_level<>'支行').first()
        if not org:
            return str(org_no)+u'请填写正确的归属机构号！'

        teller_no = newdata.get('teller_no')
        fx = g.db_session.query(User).join(UserGroup,UserGroup.user_id==User.role_id).join(Group,Group.id==UserGroup.group_id).filter(User.user_name==teller_no).first()
        if not fx:
            return str(teller_no)+u'没有此客户经理'
            
        login_branch_no = newdata.get('login_branch_no')
        branch = ur.org_list(str(login_branch_no),True)
        if org_no not in branch and login_branch_no != '966000':
            return str(org_no) + u'非本网点!'

        #判断网点是不是归属支行
        org_list = ur.org_list(str(org_no),True)
        fy = g.db_session.query(User).join(UserBranch,UserBranch.user_id==User.role_id).join(Branch,Branch.role_id==UserBranch.branch_id).filter(Branch.branch_code.in_(org_list),User.user_name==teller_no).first()
        if not fy:
            return u'机构'+str(org_no)+u'没有此客户经理'+str(teller_no)


        newdata.pop('login_branch_no');
        g.db_session.query(EtcData).filter(EtcData.id == pid).update(newdata)
        return u"编辑成功"  

    def etc_org_upload(self, filepath,org_code):
        """
            批量录入
        """
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            if nrows in [0,1,2]:
                raise Exception(u"警告:文件为空")
            date_id = int(sheet.cell(2,0).value)
        except Exception,e:
            g.db_session.rollback()
            return str(e)

        sql = """ select cust_net_no, e.* from etc_data e """
        connection  = g.db_session.bind.raw_connection()
        cursor  = connection.cursor()
        tbs = self.sql2dict(sql,cursor) #车牌号:

        org_list = ur.org_list(str(org_code),True)

        all_msg = []
        souser = []
        for r in range(2,nrows):
            try:
                #签约日期   车牌号  车主    卡号    卡主    签约机构    签约柜员    归属柜员号  归属机构号

                date_id = int(sheet.cell(r,0).value)
                cust_net_no = str(sheet.cell(r,1).value)
                cust_name = str(sheet.cell(r,2).value)
                card_no= str(int(sheet.cell(r,3).value))
                card_name = str(sheet.cell(r,4).value)
                sign_org_no = str(sheet.cell(r,5).value).replace('.0','')
                sign_teller_no = str(sheet.cell(r,6).value).replace('.0','')
                teller_no = str(sheet.cell(r,7).value).replace('.0','')
                org_no =  str(sheet.cell(r,8).value).replace('.0','')
                print date_id, cust_net_no, cust_name, card_no, card_name, sign_org_no, sign_teller_no, org_no, teller_no

                line = r + 1
                err_message = u'第' + str(line) + u'行,车牌号:' + cust_net_no 


                tb = tbs.get(str(cust_net_no))
                if tb is None :
                    err_message = err_message + u',没有此车牌号'
                    raise Exception(err_message)

                if len(str(date_id)) != 8 :
                    raise Exception(err_message + u'请填写正确的签约日期')
                if cust_net_no.strip()=='':
                    raise Exception(err_message + u'请填写车牌号')
                if cust_name.strip()=='':
                    raise Exception(err_message + u'请填写车主')
                if len(card_no) != 16:
                    raise Exception(err_message + u'请填写正确的信用卡卡号')
                if card_name.strip()=='':
                    raise Exception(err_message + u'请填写卡主')
                if sign_org_no.strip()=='':
                    raise Exception(err_message + u'请填写签约机构号')
                if sign_teller_no.strip()=='':
                    raise Exception(err_message + u'请填写签约柜员号')
                if org_no.strip()=='':
                    raise Exception(err_message + u'请填写归属机构号')
                if teller_no.strip()=='':
                    raise Exception(err_message + u'请填写归属柜员号')

                sorg = g.db_session.query(Branch).filter(Branch.branch_code==sign_org_no,Branch.branch_level<>'支行').first()
                if not sorg:
                    return u'第'+str(r+1)+u'行,机构'+str(sign_org_no)+u'请填写正确的签约机构！'
                org = g.db_session.query(Branch).filter(Branch.branch_code==org_no,Branch.branch_level<>'支行').first()
                if not org:
                    return u'第'+str(r+1)+u'行,机构'+str(org_no)+u'请填写正确的归属机构号！'

                if org_no not in org_list:
                    return u'第'+str(r+1)+u'行机构'+str(org_no)+u'非本网点'

                fx = g.db_session.query(User).join(UserGroup,UserGroup.user_id==User.role_id).join(Group,Group.id==UserGroup.group_id).filter(User.user_name==teller_no).first()
                if not fx:
                    return u'第'+str(r+1)+u'行'+str(teller_no)+u'没有此客户经理'

                fy = g.db_session.query(User).join(UserBranch,UserBranch.user_id==User.role_id).join(Branch,Branch.role_id==UserBranch.branch_id).filter(Branch.branch_code.in_(org_list),User.user_name==teller_no).first()
                if not fy:
                    return u'第'+str(r+1)+u'行机构'+str(org_no)+u'没有此客户经理'+str(teller_no)


                if isinstance(sign_org_no,(int, float)):
                    sign_org_no = str(int(sign_org_no))

                if isinstance(sign_teller_no,(int, float)):
                    sign_teller_no = str(int(sign_teller_no))

                if isinstance(org_no,(int, float)):
                    org_no = str(int(org_no))

                if isinstance(teller_no,(int, float)):
                    teller_no = str(int(teller_no))

                temp = {'date_id':date_id, 
                        'cust_net_no':cust_net_no, 
                        'cust_name':cust_name, 
                        'card_no':card_no, 
                        'card_name':card_name, 
                        'sign_org_no':sign_org_no, 
                        'sign_teller_no':sign_teller_no, 
                        'org_no':org_no, 
                        'teller_no':teller_no, 
                }
                all_msg.append(temp)
                key = str(cust_net_no)
                if key in souser:
                    return u'第'+str(r+1)+u'行车牌号'+str(cust_net_no)+u'已经存在excel中,请仔细核对'
                else:
                    souser.append(key)
            except ValueError, e:
                g.db_session.rollback()
                return u'第'+str(r + 1) + u'行有错误'+str(e)+u"请检查年份是否正确,信用卡卡号是否正确"
            except IndexError,e:
                g.db_session.rollback()
                return u'第'+str(r+1)+u'行有错误,请检查列数'
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        for i in range(0,len(all_msg)):
            g.db_session.query(EtcData).filter(EtcData.cust_net_no==all_msg[i]['cust_net_no']).update({EtcData.org_no:all_msg[i]['org_no'],EtcData.teller_no:all_msg[i]['teller_no']})
        return u'导入成功'

    #电子银行得分附加
    def ebank_add_save(self, **kwargs):
        current_app.logger.debug("kkkkkkkkk")
        try:
            kyear = kwargs.get('kyear')
            org_no = kwargs.get('org_no')
            org_name = kwargs.get('org_name')
            user_name = kwargs.get('user_name')
            name = kwargs.get('name')
            add_points = kwargs.get('add_points')
            remarks = kwargs.get('remarks')
            
            if float(add_points) < 0:
                return u'附加分不能为负'
 
            fx = g.db_session.query(User).join(UserGroup,UserGroup.user_id==User.role_id).join(Group,Group.id==UserGroup.group_id).filter(User.user_name==user_name).filter(Group.group_name=='客户经理').filter(Group.group_type_code=='2000').first()
            fy = g.db_session.query(ManEbankAddPoints).filter(ManEbankAddPoints.user_name==user_name,ManEbankAddPoints.kyear==kyear).first()
            if not fx:
                raise Exception(u'该员工不是客户经理！')
            if fy:
                raise Exception(u'该客户经理已添加！')

            g.db_session.add(ManEbankAddPoints(kyear=kyear, org_no=org_no, user_name=user_name, add_points=add_points, remarks=remarks))
            return u'添加成功！'
        except Exception,e:
            return str(e)
 

    def ebank_add_update(self, **kwargs):
        try:
            item_id = kwargs.get('item_id')
            kyear = kwargs.get('kyear')
            org_no = kwargs.get('org_no')
            org_name = kwargs.get('org_name')
            user_name = kwargs.get('user_name')
            name = kwargs.get('name')
            add_points = kwargs.get('add_points')
            remarks = kwargs.get('remarks')

            if float(add_points) < 0:
                return u'附加分不能为负'

            g.db_session.query(ManEbankAddPoints).filter(ManEbankAddPoints.id == item_id).update({ManEbankAddPoints.kyear:kyear, ManEbankAddPoints.org_no:org_no, ManEbankAddPoints.user_name:user_name, ManEbankAddPoints.add_points:add_points, ManEbankAddPoints.remarks:remarks})
            return u'修改成功！'
        except Exception, e:
            return str(e)

    def ebank_add_delete(sel, **kwargs):
        try:
            row_id = kwargs.get('row_id')

            g.db_session.query(ManEbankAddPoints).filter(ManEbankAddPoints.id == row_id).delete()

            return u'删除成功！'
        except Exception, e:
            return u'删除失败！'

    def ebak_add_upload(self, filepath):
        """
            批量录入
        """
        try:
            data = xlrd.open_workbook(filepath)
            sheet = data.sheet_by_index(0)
            #行
            nrows = sheet.nrows
            if nrows in [0,1,2,3]:
                raise Exception(u"警告:文件为空")
        except Exception,e:
            g.db_session.rollback()
            return str(e)

        all_msg = []
        souser = []
        for r in range(3,nrows):
            try:
                kyear = int(sheet.cell(r,0).value)
                org_no = str(sheet.cell(r,1).value)
                org_name = str(sheet.cell(r,2).value)
                user_name = str(int(sheet.cell(r,3).value))
                name = str(sheet.cell(r,4).value)
                add_points = str(sheet.cell(r,5).value).replace('.0','')
                remarks = str(sheet.cell(r,6).value).replace('.0','')

                line = r + 1
                err_message = u'第' + str(line) + u'行,客户经理号:' + user_name


                if len(str(kyear)) != 4 :
                    raise Exception(err_message + u'请填写正确的年份')
                if org_no.strip()=='':
                    raise Exception(err_message + u'请填写机构号')
                if user_name.strip()=='':
                    raise Exception(err_message + u'请填写客户经理号')
                if add_points.strip()=='':
                    raise Exception(err_message + u'请填写附加分')

                sorg = g.db_session.query(Branch).filter(Branch.branch_code==org_no).first()
                if not sorg:
                    return u'第'+str(r+1)+u'行,机构'+str(sign_org_no)+u'请填写正确的机构号！'

                fx = g.db_session.query(User).join(UserGroup,UserGroup.user_id==User.role_id).join(Group,Group.id==UserGroup.group_id).filter(User.user_name==user_name).first()
                if not fx:
                    return u'第'+str(r+1)+u'行'+str(teller_no)+u'没有此客户经理'

                fy = g.db_session.query(User).join(UserBranch,UserBranch.user_id==User.role_id).join(Branch,Branch.role_id==UserBranch.branch_id).filter(Branch.branch_code==org_no,User.user_name==user_name).first()
                if not fy:
                    return u'第'+str(r+1)+u'行机构'+str(org_no)+u'没有此客户经理'+str(teller_no)


                if isinstance(org_no,(int, float)):
                    org_no = str(int(org_no))

                if isinstance(user_name,(int, float)):
                    user_name = str(int(user_name))

                if isinstance(add_points,(int, float)):
                    add_points = str(int(add_points))


                temp = {'kyear':kyear, 
                        'org_no':org_no, 
                        'user_name':user_name, 
                        'add_points':add_points, 
                        'remarks':remarks, 
                }
                all_msg.append(temp)
                key = str(kyear) + str(org_no) + str(user_name)
                if key in souser:
                    return u'第'+str(r+1)+u'行客户经理号'+str(user_name)+u'已经存在excel中,请仔细核对'
                else:
                    souser.append(key)
            except ValueError, e:
                g.db_session.rollback()
                return u'第'+str(r + 1) + u'行有错误'+str(e)+u"请检查年份是否正确"
            except IndexError,e:
                g.db_session.rollback()
                return u'第'+str(r+1)+u'行有错误,请检查列数'
            except Exception,e:    
                g.db_session.rollback()
                print Exception,':',e
                return u'第'+str(r+1)+u'行有问题:'+str(e)
        for i in range(0,len(all_msg)):
            g.db_session.add(ManEbankAddPoints(**all_msg[i]))
        return u'导入成功'
