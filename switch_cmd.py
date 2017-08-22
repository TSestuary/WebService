#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
# Copyright © 2008-2017 Thundersoft all rights reserved.
#
#     Author: lu tianxiang (scm)
#     E-mail: lutx0528@thundersoft.com
#     Date  : 07/31/2017
#     Function:	creat a new thread,processing commands and parameters.
#				Judgement command and Perform the corresponding function.
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 07/31/2017 lu tianxiang  init
# 2017/08/08 zhang lu      Modularization
#===============================================================================

import test
import power
import osinstall

import threading

def default(extend):
  pass

##Judgment command and Perform corresponding functions
def commadExecute(command,extend={}):
  if command == 'test': test.test(extend)
  elif command == 'power':power.power_operation(extend)
  elif command == 'os_install':osinstall.os_install(extend)
  else: default(extend)

##creat a new thread
def commandProcess(target,extend={}):
  t = threading.Thread(target=(commadExecute),args=(target,extend))
  t.setDaemon(True)
  t.start()
  t.join(1)

##Command processing
def CommandTrigger(control_queue,command_queue):
  while control_queue.empty():
    while not command_queue.empty():
      cmd_str = command_queue.get()
      cmd = cmd_str.split('|')[0]
      args = cmd_str.split('|')[1]
      extend = {}
      if len(args) != 0:
        for i in args.split(','):
          extend[i.split('=')[0]]=i.split('=')[1]
      commandProcess(cmd,extend)

def _syncStart(control_queue,command_queue):
  if control_queue and not control_queue.empty():
    print 'last action : {}'.format(control_queue.get())
  t = threading.Thread(target=CommandTrigger,
    args=(control_queue,command_queue))
  t.setDaemon(True)
  t.start()
  t.join(1)

