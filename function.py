#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
#Copyright © 2008-2017 Thundersoft all rights reserved.
#		
#	Author: zhang lu (SPD)
#	E-mail: zhanglu0704@thundersoft.com
#	Date  : 2017/08/09
#	Function:For the configuration file to operate
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 2017/08/09 zhang lu     init
#===============================================================================

import os
import sys
import json
import urllib2
import logging
import logging.config


###########################################################################
#function:extract value of parameter from config file 
#Similar to  |grep 
###########################################################################
def get_value(filename,parameter):
  data=''
  f=open(filename,'r')
  info=f.readlines()
  f.close()
  for line in info:
    if(line.find(parameter) == 0):
      parameter+='='
      break
  for i in range(len(parameter),len(line) ):
    if line[i] != '\n':
      data+=line[i]
	  
  return data

###########################################################################
#function:exchange value of parameter in ip config file
#Similar to  sed -i 
###########################################################################
def change_value(filename,parameter,value):
  i=0
  f=open(filename,'r')
  info=f.readlines()
  f.close()
  for line in info:
    if(line.find(parameter) == 0):
      line = '%s=%s' % (parameter,value)+'\n'
      info[i]=line
      break
    i=i+1
  with open(filename, 'r+') as f:
    f.writelines(info)
  
	
############################################################################
# function:useing Standard library of Python instead of curl to request info
#          from server to web
############################################################################
def returnsfun(cmd,data):
  req = urllib2.Request(cmd)
  req.add_header('Content-Type', 'application/json')
  response = urllib2.urlopen(req, json.dumps(data))
  print "---------------------------returns----------------------------------"
  print response.read()
  print "-------------------------returns end--------------------------------"
  return


############################################################################
# function：use logger in ./about/logger.conf to write log info 
############################################################################
def write_log(loggerName,level,message):
  logging.config.fileConfig("./about/logger.conf")
  logger = logging.getLogger(loggerName)

  if level == "debug":logger.debug(message)
  elif level == "info":logger.info(message)
  elif level == "warning":logger.warning(message)
  elif level == "error":logger.error(message)
  else:print "ERROR :in function.write_log() no such level !"

  return
