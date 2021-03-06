#-*- coding: utf-8 -*-
"""
    yinsho.services
    #####################

    yinsho services package
"""
from .idda import IddaService


from .users import UsersService
from .permission import PermissionService
# from .auditsale import AuditsaleService
from .nxmanagement import NXBranchService
from .net import NetService
from .performance import PerformanceService
from .targetpermission import TargetService
from .contract_check import Contract_checkService
from .con_check import Con_checkService
from .pos_input import Pos_inputService
from .atm_input import Atm_inputService
from .branchmanagepermission import BranchmanageService
from .bgu import BguService
from .bgs import BgsService
from .parameterpermission import ParameterService
from .hand_input import HandInputService
from .bank_input import BankInputService
from .large_loss import Large_lossService
from .depappointservice import DepappointService
from .parasetpermission import ParasetService
from .basicsalary import BasicSalaryService
from .dkgsgxxzpermission import DkgsgxxzService
from .gsgxck import GsgxckService
from .gsgxdk import GsgxdkService
from .cdgggx import CdgggxService
from .staffrelation import UserRelationService
from .dict_data import DictDataService
from .eduallowance import EduAllowanceService
from .position import poConService
from .t_para import TParaService
from .adjusttype import AdjusttypeS
from .monsalary import monsalaryService
from .dkkhxdh import DkkhxdhService
from .reportmag import reportmagService
from .accthk import AccthkService
from .custhk import CusthkService
from .m_manager_add_sco import ManagerAddScoService
from .custHookMag import custHookMagService 
from .dep_stock_mtf_input import DepstockmtfinputService 
from .village_input import * 
from .loan_efile_input import Loan_Input
from .dep_stock_mtf_input import DepstockmtfinputService
from .mbox import MboxService
from .postmanagepermission import PostmanageService 
from .staff_sal_hzinput import Staff_sal_hzinputService
from .staff_sal_input import Staff_sal_inputService
from .staff_sal_count import staff_sal_countService
from .man_gradejdg import *
from .userreport import *
from .org_level import *
from .teller_level import *
from .branch_grade_report import *
from .delegate_hand import *
from .delegate_form import *
from .user_level import *
from .ChooseService import ChooseService
from .handmain import *
from .burank import *
from .bank_pe_input import *
from .international_level import * 
from .ebills_manager import Ebills_ManagerService
from .counter_fine_amount import CounterFineAmountService
from .hall_manager_hander import hallManagerHander
from .count_exam_basevol import countExamBasevol
from .teller_Volume_Adjust import teller_Ajust_base
