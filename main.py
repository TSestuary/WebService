#!/usr/bin/env python
# -*- coding:utf-8 -*-
#===============================================================================
#
# Copyright © 2008-2017 Thundersoft all rights reserved.
#
#     Author: lu tianxiang (scm)
#     E-mail: lutx0528@thundersoft.com
#     Date  : 07/31/2017
#     Function: tornado.web.asynchronous frame 
#-------------------------------------------------------------------------------
#
#                      EDIT HISTORY FOR FILE
#
# This section contains comments describing changes made to the module.
# Notice that changes are listed in reverse chronological order.
#
# when       who           what, where, why
# --------   ---           -----------------------------------------------------
# 07/31/2017 lu tianxiang  init.
# 2017/08/08 zhang lu	   Modularization
#===============================================================================

import switch_cmd
import dbconn

import os
import re
import sys
import json
import time
import uuid
import Queue
import sqlite3
import collections
import threading
import tornado.web
import tornado.ioloop
from datetime import datetime
from datetime import timedelta
from subprocess import PIPE
from subprocess import Popen
from subprocess import check_output
from subprocess import CalledProcessError
from collections import OrderedDict
from itertools import product as cproduct
from string import join as sjoin
from string import split as ssplit
from string import replace as sreplace
from tornado.escape import json_encode

class MainHandler(tornado.web.RequestHandler):
  def get(self):## curl uri
    self.set_header("Content-Type","application/json; charset=UTF-8")
    url_info = "http://<host>:7890"
    self.write('jobs services\n')
    self.finish()

class ControlHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):## curl uri/ctl
    control_queue = self.application.settings.get('control_queue',None)
    command_queue = self.application.settings.get('command_Queue',None)
    if control_queue and not control_queue.empty():
      self.write('{}\n'.format("stoped"))
      self.finish()
    elif command_queue and not command_queue.empty():
      self.write('wait for : {}\n'.format(command_queue.qsize()))
      self.finish()
    else:
      self.write('wait for next polling\n')
      self.finish()
  @tornado.web.asynchronous
  def put(self,status):## curl -X PUT uri/ctl/[start|stop]
    if status and status == 'start':
      self.set_header("Content-Type","application/json; charset=UTF-8")
      control_queue = self.application.settings.get('control_queue',None)
      self.write('{}|'.format(control_queue.qsize()))
      if control_queue and not control_queue.empty():
        switch_cmd._syncStart(control_queue,
          self.application.settings.get('command_queue',None))
      self.write('{}\n'.format("start"))
      self.finish()
    elif status and status == 'stop':
      self.set_header("Content-Type","application/json; charset=UTF-8")
      c = self.application.settings.get('control_queue',None)
      self.write('{}|'.format(c.qsize()))
      if c and c.empty(): c.put("stop")
      if c and c.empty(): c.put("stop")
      self.write('{}|'.format(c.qsize()))
      self.write('{}\n'.format("stop"))
      self.finish()
    else:
      self.set_header("Content-Type","application/json; charset=UTF-8")
      self.write('please use uri/{}\n'.format("[start|stop|status]"))
      self.finish()

class CommandHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):## curl uri/cmd
    map(lambda x:self.write(
      "{}|{}|{}|{}\n".format(x[1],x[2],x[3],x[4])),
      dbconn._query('select * from commands'))
    self.finish()
  @tornado.web.asynchronous
  def put(self,name):## curl -X PUT uri/cmd/[command name]
    self.set_header("Content-Type","application/json; charset=UTF-8")
    command_queue = self.application.settings.get('command_queue',None)
    command_queue.put("{}|".format(name))
    self.finish()
  @tornado.web.asynchronous
  def post(self,name):## curl -X POST uri/cmd/[command name] --data <arg>=<value>
    args = sjoin(map(
      lambda x:'{}={}'.format(x,self.get_argument(x,None)),
      self.request.arguments.keys()),",")
    self.set_header("Content-Type","application/json; charset=UTF-8")
    command_queue = self.application.settings.get('command_queue',None)
    command_queue.put("{}|{}".format(name,args))
    self.finish()

if __name__ == "__main__":
  dbconn._commit('''
    create table if not exists commands(
    uuid text UNIQUE,command text,
    status text,begin text,end text)''')
  Control_Queue = Queue.Queue(1)
  Command_Queue = Queue.Queue(1000)
  switch_cmd._syncStart(Control_Queue,Command_Queue)
  settings = {'control_queue':Control_Queue,'command_queue':Command_Queue}
  application = tornado.web.Application(
    [ (r"/",MainHandler),
      (r"/ctl",ControlHandler),
      (r"/ctl/(.*)",ControlHandler),
      (r"/cmd",CommandHandler),
      (r"/cmd/(.*)",CommandHandler),
    ],**settings)
  application.listen(7890)
  tornado.ioloop.IOLoop.instance().start()
