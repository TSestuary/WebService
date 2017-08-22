#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
#Copyright © 2008-2017 Thundersoft all rights reserved.
#		
#	Author: zhang lu (SPD)
#	E-mail: zhanglu0704@thundersoft.com
#	Date  : 08/07/2017
#	Function: for test API,just print command and parmater information.
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 2017/08/08 zhang lu      Modularization
# 2017/08/15 zhang lu      Added a test that returns information from Server to Web
# 2017/08/16 zhang lu      useing Standard library of Python instead of curl 
#===============================================================================
import dbconn
import function

import time
import os
import commands

@dbconn.cmdlog
def test(extend):
  print "=======================parameter list==============================="
#  time.sleep(4)
#  update_cmd_status(extend['uuid'],'P01')
#  time.sleep(4)
#  update_cmd_status(extend['uuid'],'P02')
#  time.sleep(4)
#  update_cmd_status(extend['uuid'],'P03')
#  time.sleep(4)
#  update_cmd_status(extend['uuid'],'P04')
  
  for par in extend:
    print "{}:{}".format(par,extend[par])

#  The old method: using the curl command to call web API
#  os.environ["WEBSITE_ADDR"]=function.get_value("./about/environment.conf","WEBSITE_ADDR")
#  os.environ["JOBID"] = extend["JOBID"]
#  (state,returnvalue)=commands.getstatusoutput("curl -H \"Content-Type:application/json\" -X POST http://$WEBSITE_ADDR/cmd/result --data '{\"CMD\":\"test\",\"JOBID\":\"'$JOBID'\"}'")
#  print state,returnvalue

#  Standard library of Python to call web API
  data = {"CMD":"test","JOBID":'{}'.format(extend["JOBID"])}
#  data["JOBID"]=extend["JOBID"]
  website_addr=function.get_value("./about/environment.conf","WEBSITE_ADDR")
  cmd='http://'+website_addr+'/cmd/result'
  function.returnsfun(cmd,data)

  print "===========================the end=================================="
  return

def update_cmd_status(uuid,status='wait'):
  dbconn._commit(
    "update commands set status = '{}' where uuid='{}'".format(status,uuid))
