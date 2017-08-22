#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
#Copyright © 2008-2017 Thundersoft all rights reserved.
#		
#	Author: zhang lu (SPD)
#	E-mail: zhanglu0704@thundersoft.com
#	Date  : 08/07/2017
#	Function: board power operation
#	Dependence:ipmitool
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 2017/08/08 zhang lu      Modularization
# 2017/08/09 zhang lu      Integration power_on/off/... becomes one function power_operation
# 2017/08/14 zhang lu      Increased interrupts associate with install OS
# 2017/08/15 zhang lu      Added a test in power status that returns information from Server to Web
# 2017/08/16 zhang lu      useing Standard library of Python instead of curl 
#===============================================================================

import dbconn
import function

import os
import commands
import time

######################################################################################################
# board power operation	(status/on/off/reset/)
# curl -X POST http://web_service_ip:7890/cmd/power --data OPERATE=on/off/status/reset 
# --data BMC_IP=<bmc_ip> --data NIC_IP=<nic_ip> --data JOBID=<jobid>
# OPERATE=status	for check board power state
# OPERATE=on	for board power on
# OPERATE=off	for board power off
# OPERATE=reset for board power reboot
######################################################################################################
@dbconn.cmdlog
def power_operation(extend):
  if ('BMC_IP'not in extend )or( extend["BMC_IP"] == ''):
    function.write_log("webCallError","error","(001)cmd:power No parameter 'BMC_IP' or 'BMC_IP' parameter value is empty!")
    return
  if ('OPERATE' not in extend)or(extend["OPERATE"] not in ["status","on","off","reset"] ):
    function.write_log("webCallError","error","(002): cmd:power No parameter 'OPERATE' or 'OPERATE' parameter value is can't to be distinguish.")
    return
  if ('NIC_IP'not in extend )or( extend["NIC_IP"] == ''):
    function.write_log("webCallError","error","(003): cmd:power No parameter 'NIC_IP' or 'NIC_IP' parameter value is empty!")
    return
  if ('JOBID'not in extend )or( extend["JOBID"] == ''):
    function.write_log("webCallError","error","(004): cmd:power No parameter 'JOBID' or 'JOBID' parameter value is empty!")
    return

  os.environ["BMC_IP"] = extend["BMC_IP"]
  os.environ["BMC_USER"] = function.get_value("./about/environment.conf","BMC_USER")
  os.environ["BMC_PASSWD"] = function.get_value("./about/environment.conf","BMC_PASSWD")
  website_addr=function.get_value("./about/environment.conf","WEBSITE_ADDR")
  cmd='http://'+website_addr+'/cmd/result'

################################################################################
# find The local directory of NFS mounted and ip config file diretory name and 
# ip config file path
################################################################################
  localdir=function.get_value("./about/environment.conf","LOCAL_DIR")
  iplist=function.get_value("./about/environment.conf","IP_LIST")
  if(localdir[len(localdir)-1] == '/'):
    ip_config_path=localdir+iplist+'/'+extend["NIC_IP"]
  else:
    ip_config_path=localdir+'/'+iplist+'/'+extend["NIC_IP"]

# Determine command parameters
  if extend["OPERATE"] == "status":power_status(ip_config_path,extend["NIC_IP"],extend["JOBID"],cmd)
  elif extend["OPERATE"] == "on":power_on(ip_config_path,extend["JOBID"],cmd)
  elif extend["OPERATE"] == "off":power_off(ip_config_path,extend["JOBID"],cmd)
  elif extend["OPERATE"] == "reset":power_reset(ip_config_path,extend["JOBID"],cmd)
  else:function.write_log("webCallError","error","Error(003): parameter 'OPERATE' can't to be distinguish.")

  return
##############################################################################
#check board power state
#
##############################################################################
def power_status(ip_config_path,nicip,jobid,cmd):
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power status")
  board_info1=function.get_value(ip_config_path,"PLATFORM")
  board_info2=function.get_value(ip_config_path,"SELECT")
  board_info3=function.get_value(ip_config_path,"USERNAME")
  board_info4=function.get_value(ip_config_path,"PROGRESS")
  data={"PLATFORM":'{}'.format(board_info1),"OS":'{}'.format(board_info2),"USERNAME":'{}'.format(board_info3),\
	  "PROGRESS":'{}'.format(board_info4),"POWER_STATUS":'{}'.format(returnvalue),"SYSTEM_STATUS":"","JOBID":'{}'.format(jobid),"RESULT":"","ERROR_INFO":""}
  if state != 0:
    function.write_log("sysError","error","(005): cmd:power status faile!")
    data["RESULT"]="fail"
    data["ERROR_INFO"]=returnvalue
    function.returnsfun(cmd,data)
    return
  else : 
    pass

#  Determines whether the system is started 
  if returnvalue == "Chassis Power is on":
    os_status_fun(nicip,cmd,data,ip_config_path)
  else:
    data["RESULT"]="success"
    data["SYSTEM_STATUS"]="DOWN"
    function.returnsfun(cmd,data)
  return

#############################################################################
#board power on
#if power on when OS installation is interrupted 
############################################################################
def power_on(ip_config_path,jobid,cmd):
  data={"POWER_STATUE":"","PROGRESS":"","JOBID":'{}'.format(jobid),"RESULT":"","ERROR_INFO":""}
  data["PROGRESS"]=function.get_value(ip_config_path,"PROGRESS")
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power on")
  data["POWER_STATUE"]=returnvalue
  if state != 0 :
    function.write_log("sysError","error","(006): cmd:power on faile!")
    data["RESULT"]="fail"
    data["ERROR_INFO"]=returnvalue
  else:
    data["RESULT"]="success"
  function.returnsfun(cmd,data)
  return

############################################################################
# board power off 
# if power-off when OS is installing change "PROGRESS" to "INTERRUPTED"
############################################################################
def power_off(ip_config_path,jobid,cmd):
  data={"POWER_STATUE":"","PROGRESS":"","JOBID":'{}'.format(jobid),"RESULT":"","ERROR_INFO":""}
  if function.get_value(ip_config_path,"PROGRESS") == "INSTALLING" :
    function.change_value(ip_config_path,"PROGRESS","INTERRUPTED")
    data["PROGRESS"]="INTERRUPTED"
  else:data["PROGRESS"]="COMPLETE"
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power off")
  data["POWER_STATUE"]=returnvalue
  if state != 0 :
    function.write_log("sysError","error","(007): cmd:power off faile!")
    data["RESULT"]="fail"
    data["ERROR_INFO"]=returnvalue
  else:
    data["RESULT"]="success"
  function.returnsfun(cmd,data)
  return

##############################################################################
#board power reset
# if power reset when OS is installing change "PROGRESS" to "INTERRUPTED"
##############################################################################
def power_reset(ip_config_path,jobid,cmd):
  data={"POWER_STATUE":"","PROGRESS":"","JOBID":'{}'.format(jobid),"RESULT":"","ERROR_INFO":""}
  if function.get_value(ip_config_path,"PROGRESS") == "INSTALLING" :
    function.change_value(ip_config_path,"PROGRESS","INTERRUPTED")
    data["PROGRESS"]="INTERRUPTED"
  else:data["PROGRESS"]="COMPLETE"
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power reset")
  data["POWER_STATUE"]=returnvalue
  if state != 0 :
    function.write_log("sysError","error","(008): cmd:power reset faile!")
    data["RESULT"]="fail"
    data["ERROR_INFO"]=returnvalue
  else:
    data["RESULT"]="success"
  function.returnsfun(cmd,data)
  return


###############################################################################
# By way of Ping to check OS status ,set timeout is 10 mins
###############################################################################
def os_status_fun(nicip,cmd,data,ip_config_path) :
  num=0
  os.environ["NIC_IP"] = nicip
  while (1):
    (state,returnvalue)=commands.getstatusoutput("ping -c 1 $NIC_IP")
    if state == 0:
      data["RESULT"]="success"
      data["SYSTEM_STATUS"]="START_UP"
      function.returnsfun(cmd,data)
      break
    else:
      data["SYSTEM_STATUS"]="BOOTING"
      data["RESULT"]="wait"
      function.returnsfun(cmd,data)
    time.sleep(30)
    num=num+1
    if num > 20:
      data["RESULT"]="fail"
      data["ERROR_INFO"]="TIME OUT"
      data["SYSTEM_STATUS"]="TIME_OUT"
      function.returnsfun(cmd,data)
      break
    (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power status")
    if (state == 0 ) and (returnvalue == "Chassis Power is off"):
      data["RESULT"]="success"
      data["SYSTEM_STATUS"]="DOWN"
      data["POWER_STATUS"]=returnvalue
      function.returnsfun(cmd,data)
      break;
    elif (state == 0 ) and (returnvalue == "Chassis Power is on"):
      continue
    else:
      function.write_log("sysError","error","(005): cmd:power status faile!")
      data["RESULT"]="fail"
      data["ERROR_INFO"]=returnvalue
      function.returnsfun(cmd,data)
      break
  return
