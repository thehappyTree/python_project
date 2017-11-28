# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from hoapp.models import *
from django.db import transaction
import traceback
from datetime import datetime
#网点申请钱箱列表index
@login_required
def aplbox_manage(request): 
    branch_id = request.user.branch_id
    print branch_id 
    aplboxs_obj = CashboxaplInfo.objects.filter( is_active = '1' ).filter( branch_id = branch_id ).all()
    branch = Branch.objects.get( id=branch_id )
    for a in aplboxs_obj:
        print len(a.cashboxs.all())
    #aplboxs = [{'id' : ap.id, 'date' : ap.date, 'branch_name': branch.name, 'cashbox' : len(ap.cashboxs), 'instock_nu' : ap.package_num, 'apl_status':ap.apl_status}  for ap in aplboxs_obj]
    aplboxs = [{'id' : ap.id, 'date' : ap.date, 'branch_name': branch.name, 'cashboxs':len(ap.cashboxs.all()), 'instock_nu' : ap.package_num, 'apl_status':ap.apl_status}  for ap in aplboxs_obj]
    print aplboxs
    return render_to_response('teller/approvalbox/aplboxmanage.html',{'aplboxs':aplboxs})


@login_required
def get_cashbox(request):
    if request.method == 'GET':
        try:
            branch_id= request.user.branch_id
            print branch_id
            cashboxs_obj = Cashbox.objects.filter( is_active='1').filter(branch_id=branch_id ).all() #过滤掉本行
            cashboxs = [[cb.id, cb.serial,cb.status] for cb in cashboxs_obj]
            if cashboxs is None:
                data = {
                        'is_success' : False
                        }
            data = {
                    'is_success' : True,
                    'cashboxs' : cashboxs
                    }
        except Exception,e :
            tranceback.print_exc()
            data = {
                    'is_success' : False
                    }
        return JsonResponse(data)

@login_required
def apl_box(request):
    if request.method == 'POST':
        print '=============='
        aplboxs = []
        form = request.POST
        date = form.get('date')
        date = datetime.strptime(date, "%Y-%m-%d")
        instock_nu = form.get('instock_nu')
        cids = form.get('cids')
        branch_id = request.user.branch_id
        branch = Branch.objects.get( id=branch_id )
        sid = transaction.savepoint()
        cids_list = cids.split('-')
        try:
            #cli = CashboxaplInfo.objects.create( date=date, branch=branch, package_num=instock_nu, apl_status=CashboxaplInfo.WCHECK,is_active='1')           
            cli = CashboxaplInfo(date=date, branch=branch, package_num=instock_nu, apl_status=CashboxaplInfo.WCHECK,is_active='1')           
            cli.save()
            for a in cids_list:
                cash = Cashbox.objects.get( id = a )
                cash.status = Cashbox.TOKEN
                cash.save()
                cli.cashboxs.add(cash)
            cli.save()
            data = { 'is_success' : True }
            transaction.commit()
        except Exception,e:
            data = {
                    'is_success': False
                    }
            traceback.print_exc()
            transaction.savepoint_rollback(sid)
        return JsonResponse(data)


@login_required
def recheck(request):
    print '======================'
    if request.method == 'GET':
        apl_id = request.GET.get('apl_id')
        sid = transaction.savepoint()
        try:
            cbl = CashboxaplInfo.objects.get( id = apl_id )
            print cbl
            if cbl is not None:
                cbl.apl_status = CashboxaplInfo.APPLED
                cbl.save()
                data = {
                        'is_success' : True
                        }
        except Exception, e:
            data = {
                    'is_success': False
                    }
            tracback.print_exc()
            transaction.savepoint_rollback(sid)
        else:
            transaction.commit()
        print data
        return JsonResponse(data)

