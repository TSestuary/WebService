#!/usr/bin/env python
#-*- coding:utf-8 -*-
#===============================================================================
# Copyright © 2008-2017 Thundersoft all rights reserved.
#
#     Author: lu tianxiang (scm)
#     E-mail: lutx0528@thundersoft.com
#     Date  : 07/31/2017
#     Function:  Handling database related operations .
#-------------------------------------------------------------------------------
#						 EDIT HISTORY FOR FILE
#  This section contains comments describing changes made to the module.
#  Notice that changes are listed in reverse chronological order.
#	
#	when       who           what, where, why
#--------     -----       ------------------------------------------------------
# 07/31/2017 lutianxiang   init
# 2017/08/08 zhang lu      Modularization
#===============================================================================


import os
import uuid
import sqlite3
from datetime import datetime
from datetime import timedelta
from string import join as sjoin


def dbconn(func):
  def _dbconn(sql):
    conn = sqlite3.connect(
#      os.path.join(Utils.current_path(),"cmd.db"))
      os.path.join("./about/db_file/","cmd.db"))
    ret = func(sql,conn)
    conn.close()
    return ret
  return _dbconn

def cmdlog(func):
  def _cmdlog(extend):
    print "command : {}\nargs : {}".format(func.__name__,extend)
    new_extend = extend
    start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _uuid = uuid.uuid3(uuid.NAMESPACE_OID,bytes((func.__name__,start)))
    sql = ['insert into commands']
    sql.append('(uuid,command,status,begin) values (')
    sql.append("'{}','{}','{}','{}')".format(
      _uuid,func.__name__,"working",start))
    _commit(sjoin(sql))
    new_extend['uuid'] = _uuid
    ret = func(new_extend)
    sql = ['update commands set ']
    sql.append("status = 'done',end = '{}' ".format(
      datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')))
    sql.append("where uuid='{}'".format(_uuid))
    _commit(sjoin(sql))
    return ret
  return _cmdlog

@dbconn
def _commit(sql,conn=None):
  cur = conn.cursor()
  cur.execute(sql)
  conn.commit()

@dbconn
def _query(sql,conn=None):
  cur = conn.cursor()
  result = cur.execute(sql).fetchall()
  return result


class Utils(object):
  @staticmethod
  def current_path():
    path = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(path): return path
    if os.path.isfile(path): return os.path.dirname(path)


