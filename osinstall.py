#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
# Copyright © 2008-2017 Thundersoft all rights reserved.
#		
#	Author: zhang lu (SPD)
#	E-mail: zhanglu0704@thundersoft.com
#	Date  : 08/09/2017
#	Function: board install the operating system
#	Dependence:ipmitool
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 2017/08/09 zhang lu      
#===============================================================================

import dbconn
import function

import os
import commands
import time


################################################################################
#curl -X POST <uri>/cmd/os_install --data NIC_IP=<nic_ip> --data BMC_IP=<bmc_ip>
# --data OS_NAME=<os_name> --data U_NAME=<username>
# NIC_IP
# BMC_IP
# OS_NAME
# U_NAME
################################################################################

@dbconn.cmdlog
def os_install(extend):
  if ('BMC_IP'not in extend )or( extend["BMC_IP"] == ''):
    function.write_log("webCallError","error","(001)cmd:os_install No parameter 'BMC_IP' or 'BMC_IP' parameter value is empty!")
    return
  if ('NIC_IP'not in extend )or( extend["NIC_IP"] == ''):
    function.write_log("webCallError","error","(002): cmd:os_install No parameter 'NIC_IP' or 'NIC_IP' parameter value is empty!")
    return
  if ('OS_NAME' not in extend)or(extend["OS_NAME"] == '' ):
    function.write_log("webCallError","error","(003): cmd:os_install No parameter 'OS_NAME' or 'OS_NAME' parameter value is empty!")
    return
  if ('U_NAME' not in extend)or(extend["U_NAME"] == '' ):
    function.write_log("webCallError","error","(004): cmd:os_install No parameter 'U_NAME' or 'U_NAME' parameter value is empty! ")
    return
  if ('JOBID'not in extend )or( extend["JOBID"] == ''):
    function.write_log("webCallError","error","(005): cmd:os_install No parameter 'JOBID' or 'JOBID' parameter value is empty!")
    return

  nicip=extend["NIC_IP"]
  bmcip=extend["BMC_IP"]
  osname=extend["OS_NAME"]
  username=extend["U_NAME"]
  website_addr=function.get_value("./about/environment.conf","WEBSITE_ADDR")
  cmd='http://'+website_addr+'/cmd/result'
  data={"JOBID":"{}".format(extend["JOBID"]),"RESULT":"","PROGRESS":"","ERROR_INFO":""}

################################################################################
# find The local directory of NFS mounted and ip config file diretory name and 
# ip config file path
################################################################################
  localdir=function.get_value("./about/environment.conf","LOCAL_DIR")
  iplist=function.get_value("./about/environment.conf","IP_LIST")
  if(localdir[len(localdir)-1] == '/'):
    ip_config_path=localdir+iplist+'/'+nicip
  else:
    ip_config_path=localdir+'/'+iplist+'/'+nicip
  
################################################################################
# write OS name and user name into ip config file
################################################################################
  function.change_value(ip_config_path,"SELECT",osname)
  function.change_value(ip_config_path,"USERNAME",username)

################################################################################
# Start automatically install the operating system
################################################################################
  os.environ["BMC_USER"] = function.get_value("./about/environment.conf","BMC_USER")
  os.environ["BMC_PASSWD"] = function.get_value("./about/environment.conf","BMC_PASSWD")
  os.environ["BMC_IP"] = bmcip
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD chassis bootdev pxe")
  if(returnvalue != "Set Boot Device to pxe"):
    function.write_log("sysError","info","(006): cmd:os_install BMC:{} Set Boot Device fail".format(bmcip))
    data["RESULT"]="fail"
    data["ERROR_INFO"]="Set Boot Device fail"
    function.returnsfun(cmd,data)
    return
  
  (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power status")
  if(returnvalue == "Chassis Power is off"):
    (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power on")
    if(state == 0):
      function.change_value(ip_config_path,"PROGRESS","INSTALLING")
      data["RESULT"]="wait"
      data["PROGRESS"]="boot from NIC"
      function.returnsfun(cmd,data)
    else:
      function.write_log("sysError","info","(007): cmd:os_install BMC:{} power on failed".format(bmcip))
      data["RESULT"]="fail"
      data["ERROR_INFO"]="power on failed"
      function.returnsfun(cmd,data)
      return
  elif(returnvalue == "Chassis Power is on"):
    (state,returnvalue)=commands.getstatusoutput("ipmitool -I lanplus -H $BMC_IP -U $BMC_USER -P $BMC_PASSWD power reset")
    if(state == 0):
      function.change_value(ip_config_path,"PROGRESS","INSTALLING")
      data["RESULT"]="wait"
      data["PROGRESS"]="boot from NIC"
      function.returnsfun(cmd,data)
    else:
      function.write_log("sysError","info","(008): cmd:os_install BMC:{} power reset failed".format(bmcip))
      data["RESULT"]="fail"
      data["ERROR_INFO"]="power reset failed"
      function.returnsfun(cmd,data)
      return
  else:
    function.write_log("sysError","info","(009): cmd:os_install BMC:{} get power status failed".format(bmcip))
    data["RESULT"]="fail"
    data["ERROR_INFO"]="power status failed"
    function.returnsfun(cmd,data)
    return

# Determine whether the installation is complete 
  num=0
  while(1):
    progress=function.get_value(ip_config_path,"PROGRESS")
    if progress == "INSTALLING":
      data["RESULT"]="wait"
      data["PROGRESS"]="INSTALLING"
      function.returnsfun(cmd,data)
    elif progress=="INTERRUPTED":
      data["RESULT"]="fail"
      data["PROGRESS"]="INTERRUPTED"
      data["ERROR_INFO"]="OS install had been interrupted "
      function.returnsfun(cmd,data)
      break
    elif progress == "COMPLETE":
      data["RESULT"]="wait"
      data["PROGRESS"]="COMPLETE_REBOOTING"
      function.returnsfun(cmd,data)
      break
    num=num+1
    if num > 40 :
      data["RESULT"]="fail"
      data["PROGRESS"]="INTERRUPTED"
      data["ERROR_INFO"]="TIME OUT"
      function.returnsfun(cmd,data)
      break
    time.sleep(30)

#if time out means installation failed
  if num > 40:
    function.change_value(ip_config_path,"PROGRESS","INTERRUPTED")

#   Determine whether to start successfully 
  if progress == "COMPLETE":
    num=0
    os.environ["NIC_IP"] = nicip
    while (1):
      time.sleep(30)
      (state,returnvalue)=commands.getstatusoutput("ping -c 1 $NIC_IP")
      if state == 0:
        data["RESULT"]="success"
        data["PROGRESS"]="COMPLETE_STATED"
        function.returnsfun(cmd,data)
        break
      else:
        data["RESULT"]="wait"
        data["PROGRESS"]="COMPLETE_REBOOTING"
        function.returnsfun(cmd,data)
      num=num+1
      if num > 20:
        data["RESULT"]="fail"
        data["ERROR_INFO"]="TIME OUT"
        data["PROGRESS"]="COMPLETE_REBOOTING"
        function.returnsfun(cmd,data)
        break

  return
