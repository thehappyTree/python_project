# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import User,BranchInfo,CarInfo,AmbangInfo,MajorInfo,AssistInfo, Branch,CashboxaplInfo
# Register your models here.
admin.site.register(User)
admin.site.register(CarInfo)
admin.site.register(AmbangInfo)
admin.site.register(MajorInfo)
admin.site.register(AssistInfo)
admin.site.register(Branch)
admin.site.register(CashboxaplInfo)
