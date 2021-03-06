# -*- coding:utf-8 -*-
import os,sys
from multiprocessing import Process,Queue,Pool
import multiprocessing
import os, time, random  
from datetime import datetime,timedelta
from decimal import *
import DB2  
import csv

import etl.base.util as util
from etl.base.conf import Config
import man_dep_sal as depsal
import org_dep as orgdep
import man_dep_sco_new as dep_sco 
from etl.base.logger import info
     
condecimal = getcontext()

def sum_cl_dep(db, etldate,last_year):
    try:
        clsql = """
                SELECT 
                     sum(CASE WHEN LEFT(Ff.CST_NO,2)='81' then   ff.year_pdt*ay.percentage /100/d2.year_days else 0 end)  DSCL
                    ,sum(CASE WHEN LEFT(Ff.CST_NO,2)='82' then   ff.year_pdt*ay.percentage /100/d2.year_days else 0 end)  DGCL
                    ,sum(ff.year_pdt/d2.year_days*ay.percentage/100) CL
                    ,%d
                    ,ay.manager_no
                    , ay.org_no
                FROM f_balance ff
                INNER JOIN D_ORG o ON O.ID = FF.ORG_ID
                inner join d_account a on a.id= ff.account_id
                INNER JOIN ACCOUNT_HOOK ay on ay.account_no  = a.account_no  and ay.org_no = o.org0_code
                INNER JOIN D_DATE D2  ON ff.date_id = D2.ID
                where ff.date_id = %d
                    and ay.end_date >= ff.date_id
                    and ay.START_DATE<=ff.date_id
                    and ff.ACCT_TYPE='1'
                group by  ay.org_no,ay.manager_no
        """%(etldate, last_year)

        db.cursor.execute(clsql)
        row=db.cursor.fetchone()
        resultrow=[]
        while row:
            resultrow.append( list(row) )
            row = db.cursor.fetchone()
        return resultrow
    finally :
        db.closeDB()


"""
客户经理存款指标报表
"""
def man_dep(stardate,etldate):
    last_year = (int(str(etldate)[0:4])-1)*10000 +1231
    info("start dep.man_dep %s-%s"%(str(stardate),str(etldate)))
    try:
        oneday=datetime.now()
        db = util.DBConnect()
        cllist = sum_cl_dep(db, etldate,last_year)
        db = util.DBConnect()
        while int(stardate) <= int(etldate):
            sql0="""
            UPDATE YDW.REPORT_MANAGER_DEP 
            SET  PRI_LAST_AVG=0, PUB_LAST_AVG=0, LAST_AVG=0, PRI_THIS_AVG=0, PUB_THIS_AVG=0, THIS_AVG=0, FIN_LAST_AVG=0, FIN_THIS_AVG=0, PRI_BAL=0, PUB_BAL=0, FIN_BAL=0, BAL=0, LAST_AVG_SAL=0, ADD_AVG_SAL=0, PRI_MONTH_AVG=0, PUB_MONTH_AVG=0, MONTH_AVG=0, PRI_PDT=0, PUB_PDT=0, LICAI_PDT=0, DEP_SCORE=0, TRY_LAST_AVG_SAL=0, TRY_ADD_AVG_SAL=0,FLAG = 0
            WHERE DATE_ID=?
            """
            db.cursor.execute(sql0,int(stardate))
            db.conn.commit()

            sql="""
            SELECT 
            0  AS DSCL,
            0 AS DGCL,
            BIGINT(SUM(CASE WHEN F.ACCT_TYPE=8 THEN NVL(F1.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)/ DD.YEAR_DAYS) AS CL,--存量（理财部分)
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='81' THEN ( CASE WHEN SUBSTR(DATE_ID,5,2)!='01'THEN (NVL(F.YEAR_PDT,0)-NVL(F2.YEAR_PDT,0))*M.PERCENT/ 100 ELSE NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 END ) ELSE 0 END)/ D.BEG_MONTH_DAYS) AS DSYLJ,--对私月日均
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='82' THEN ( CASE WHEN SUBSTR(DATE_ID,5,2)!='01'THEN (NVL(F.YEAR_PDT,0)-NVL(F2.YEAR_PDT,0))*M.PERCENT/ 100 ELSE NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 END ) ELSE 0 END)/ D.BEG_MONTH_DAYS) AS DGYLJ,--对公月日均
            BIGINT(SUM(CASE WHEN SUBSTR(DATE_ID,5,2)!='01' THEN (NVL(F.YEAR_PDT,0)-NVL(F2.YEAR_PDT,0))*M.PERCENT/ 100 ELSE NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 END )/ D.BEG_MONTH_DAYS) AS YLJ,--月日均
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='81' AND F.ACCT_TYPE=1 THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)/ D.BEG_YEAR_DAYS) AS DSXL,--对私现量
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='82' AND F.ACCT_TYPE=1 THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)/ D.BEG_YEAR_DAYS) AS DGXL,--对公现量
            BIGINT(SUM(NVL(F.YEAR_PDT,0) *M.PERCENT/ 100)/ D.BEG_YEAR_DAYS) AS XL,--现量
            BIGINT(SUM(CASE WHEN F.ACCT_TYPE=8 THEN NVL(F1.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)/ DD.YEAR_DAYS) AS LCCL,--理财存量日均
            BIGINT(SUM(CASE WHEN F.ACCT_TYPE=8 THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)/ D.BEG_YEAR_DAYS) AS LCXL,--理财现量
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='81' AND F.ACCT_TYPE=1 THEN NVL(F.BALANCE,0)*M.PERCENT/ 100 ELSE 0 END)), --对私余额
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='82' AND F.ACCT_TYPE=1 THEN NVL(F.BALANCE,0)*M.PERCENT/ 100 ELSE 0 END)), --对公余额
            BIGINT(SUM(CASE WHEN F.ACCT_TYPE=8 AND A.CLOSE_DATE_ID>F.DATE_ID THEN NVL(F.BALANCE,0)*M.PERCENT/ 100 ELSE 0 END)), --理财余额 
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='81' AND F.ACCT_TYPE=1 THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)), --对私积数
            BIGINT(SUM(CASE WHEN LEFT(F.CST_NO,2)='82' AND F.ACCT_TYPE=1 THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)), --对公积数
            BIGINT(SUM(CASE WHEN F.ACCT_TYPE=8 AND A.CLOSE_DATE_ID>F.DATE_ID THEN NVL(F.YEAR_PDT,0)*M.PERCENT/ 100 ELSE 0 END)), --理财积数 
            BIGINT(SUM(CASE WHEN A.CLOSE_DATE_ID>F.DATE_ID THEN  NVL(F.BALANCE,0)*M.PERCENT/ 100 ELSE 0 END)),  --余额合计
            NVL(M.THIRD_BRANCH_NAME,'无'),NVL(M.SALE_NAME,'无'),F.DATE_ID,M.SALE_CODE,M.THIRD_BRANCH_CODE
            FROM F_BALANCE F
            LEFT JOIN (SELECT DISTINCT ACCOUNT_ID,YEAR_PDT FROM F_BALANCE F  JOIN D_ACCOUNT D ON F.ACCOUNT_ID = D.ID JOIN ACCOUNT_HOOK AH ON D.ACCOUNT_NO = AH.ACCOUNT_NO
            WHERE DATE_ID=(SELECT L_YEAREND_ID FROM D_DATE WHERE ID=?) AND F.ACCT_TYPE IN(1,8) AND AH.START_DATE <=(SELECT L_YEAREND_ID FROM D_DATE WHERE ID=?) ) F1 ON F1.ACCOUNT_ID=F.ACCOUNT_ID
            LEFT JOIN (SELECT ACCOUNT_ID,YEAR_PDT FROM F_BALANCE F WHERE DATE_ID=(SELECT L_MONTHEND_ID FROM D_DATE WHERE ID=?) AND ACCT_TYPE IN(1,8)) F2 ON F2.ACCOUNT_ID=F.ACCOUNT_ID
            JOIN D_ACCOUNT A ON F.ACCOUNT_ID=A.ID 
            JOIN D_ACCOUNT_TYPE T ON F.ACCOUNT_TYPE_ID=T.ID AND ( F.ACCT_TYPE=8 
            OR LEFT(T.SUBJECT_CODE,4) IN ('2001','2003','2005','2006','2011','2014','2002','2004','2012','2013') 
            OR LEFT(T.SUBJECT_CODE,6) IN ('231401','231409','231421','231499','231403','231402','231422','201712','201713','201714','201702','201703','201704') 
            OR T.SUBJECT_CODE IN ('20070101','20070201','20070301','20170198','20171198'))
            JOIN D_DATE D ON F.DATE_ID=D.ID  
            JOIN D_DATE DD ON D.L_YEAREND_ID=DD.ID
            JOIN D_SALE_MANAGE_RELA M ON F.MANAGE_ID=M.MANAGE_ID  
            WHERE F.ACCT_TYPE IN (1,8) AND F.DATE_ID = ?   ----AND M.THIRD_BRANCH_CODE IN ('966100') AND M.SALE_CODE IN ('9660160','X9660160')
            GROUP BY F.DATE_ID,M.THIRD_BRANCH_CODE,M.THIRD_BRANCH_NAME,M.SALE_CODE,M.SALE_NAME,D.BEG_YEAR_DAYS,DD.YEAR_DAYS,D.BEG_MONTH_DAYS
            """
            sql1="""
            UPDATE YDW.REPORT_MANAGER_DEP SET  PRI_LAST_AVG=?, PUB_LAST_AVG=?, LAST_AVG=?, PRI_MONTH_AVG=?, PUB_MONTH_AVG=?, MONTH_AVG=?, PRI_THIS_AVG=?, PUB_THIS_AVG=?, THIS_AVG=?, FIN_LAST_AVG=?, FIN_THIS_AVG=?, PRI_BAL=?, PUB_BAL=?, FIN_BAL=?,PRI_PDT=?,PUB_PDT=?,LICAI_PDT=?, BAL=?,ORG_NAME=?,SALE_NAME=?,FLAG = 1 WHERE  DATE_ID=?  AND  SALE_CODE=? AND ORG_CODE=?
            """
            sql2="""
            UPDATE YDW.REPORT_MANAGER_DEP SET  PRI_LAST_AVG=?, PUB_LAST_AVG=?, LAST_AVG=LAST_AVG+?,FLAG = 1
            WHERE  DATE_ID=?  AND  SALE_CODE=? AND ORG_CODE=?
            """
            #info("dep.man_dep,sql : \n  %s"%(sql))

            db.cursor.execute(sql,int(stardate),int(stardate),int(stardate),int(stardate))
            row=db.cursor.fetchone()
            resultrow=[]
            while row:
                resultrow.append( list(row) )
                row = db.cursor.fetchone()
            #info("dep.man_dep,sql_update : \n  %s"%(sql1))
            db.cursor.executemany(sql1,resultrow)

            for x in cllist:
                x[3] = stardate
                db.cursor.execute(sql2,x)

            db.conn.commit()
            sql2="""
            MERGE INTO REPORT_MANAGER_DEP R 
            USING V_STAFF_INFO V  ON V.USER_NAME=R.SALE_CODE AND R.DATE_ID =? ---AND R.SALE_NAME IS NULL
            WHEN MATCHED THEN UPDATE SET R.SALE_NAME=V.NAME
            """
            db.cursor.execute(sql2,int(stardate))
            sql3="""
            MERGE INTO REPORT_MANAGER_DEP R 
            USING D_ORG V  ON V.ORG0_CODE=R.ORG_CODE AND R.DATE_ID =? ---AND R.ORG_NAME IS NULL
            WHEN MATCHED THEN UPDATE SET R.ORG_NAME=V.ORG0_NAME
            """
            db.cursor.execute(sql3,int(stardate))
            db.conn.commit()

            sql4="""
            DELETE FROM REPORT_MANAGER_DEP WHERE DATE_ID=? AND FLAG=0 
            """
            db.cursor.execute(sql4,int(stardate))
            db.conn.commit()

            #orgdep.man_dep(stardate,stardate)
            """刷客户经理的佣金报表"""
            month_end_sql="""
            select month_end from D_DATE where ID=?
            """
            db.cursor.execute(month_end_sql,stardate)
            is_month_end=db.cursor.fetchall()
            if is_month_end[0][0]=='Y': 
                info("dep.man_dep,depsal.man_dep_sal")
                depsal.man_dep_sal(etldate)
                #dep_sco.man_dep_sco_new(etldate,etldate) 
 
            print stardate,"完成",datetime.now()- oneday
            info("dep.man_dep 完成")
            stardate=int(util.daycalc(stardate,1))
    finally :
        db.closeDB()

if __name__=='__main__':
    arglen=len(sys.argv)
    print sys.argv 
    d1=datetime.now()
    if arglen ==3:
        stardate=int(sys.argv[1])
        etldate=int(sys.argv[2])
        print stardate,etldate
        man_dep(stardate,etldate)
        print stardate,etldate,"完成",datetime.now()-d1
    else:
        print "please input python %s yyyyMMdd yyyyMMdd"%sys.argv[0]
