# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

"""
iomonitor - module used to monitor file descriptors for events.
Note:
 - on windows works only for sockets.

*monitor_xxx(fd, target_actor)*:
  starts monitoring a fd for events and binds a target actor to a file
  descriptor that will receive the event

*unmonitor_xxx(fd, target_actor)*:
  stops monitoring a fd for events

*update()*:
   - sends "data_arrived" to a monitoring actor if data si available for reading
   - sends "data_arrived" to a monitoring actor if data has been sent
   - sends "data_except"  to a monitoring an error has occurred

"""

import actor
import select

__all__ = [ "monitor", "monitor_incoming", "monitor_outgoing", "monitor_except",
            "unmonitor", "unmonitor_incoming", "unmonitor_outgoing", "unmonitor_except",
            "update"
            ]

rlist = []
wlist = []
xlist = []

rlist_index = {}
wlist_index = {}
xlist_index = {}

state_index = {}

READ_EVT   = 0
WRITE_EVT  = 1
EXCEPT_EVT = 2

def _monitor_event(fd, target_actor, list, list_index, evt):
	#is it registered ?
	if state_index.has_key(fd):
		index_vec = state_index[fd]
		#is it already monitored ?
		if index_vec[evt] == -1:
			#not monitored
			index = list.__len__()
			index_vec[evt] = index
			assert fd is not None
			list.append(fd)
			#already monitored
			#do nothing
		return

	#Not registered
	index_vec = [-1, -1, -1] #Create index vector
	state_index[fd] = index_vec
	index_vec[evt] = list.__len__()
	state_index[fd] = index_vec
	assert fd is not None
	list.append(fd)
	list_index[fd] = target_actor
	return

def _unmonitor_event(fd, fdlist, list_index, evt):
	if list_index.has_key(fd):
		index_vec = state_index[fd]
		if index_vec[evt] == -1:
			#registered but not monitored
			#do nothing
			return
		list_len = fdlist.__len__()
		index = index_vec[evt]
		if list_len != index:
			#it the last one! just pop it ...
			fdlist.pop()
			del list_index[fd]
			#check if we need to clear the state index
			if index_vec[0] == -1 and index_vec[1] == -1 and index_vec[2] == -1:
				del state_index[fd]
			return
		last = fdlist.pop()
		fdlist[index] = last
		#check if we need to clear the state index
		if index_vec[0] == -1 and index_vec[1] == -1 and index_vec[2] == -1:
			del state_index[fd]

def monitor(fd, target_actor):
	print "monitor %s" %fd
	print "before rlist: %s" % rlist
	print "before wlist: %s" % wlist
	print "before xlist: %s" % xlist
	_monitor_event(fd, target_actor, rlist, rlist_index, READ_EVT)
	_monitor_event(fd, target_actor, wlist, wlist_index, WRITE_EVT)
	_monitor_event(fd, target_actor, xlist, xlist_index, EXCEPT_EVT)
	print "after rlist: %s" % rlist
	print "after wlist: %s" % wlist
	print "after xlist: %s" % xlist

def monitor_incoming(fd, target_actor):
	print "monitor_incoming %s" %fd
	print "before rlist: %s" % rlist
	_monitor_event(fd, target_actor, rlist, rlist_index, READ_EVT)
	print "after rlist: %s" % rlist

def monitor_outgoing(fd, target_actor):
	print "monitor_outgoing %s" %fd
	print "before wlist: %s" % wlist
	_monitor_event(fd, target_actor, wlist, wlist_index, WRITE_EVT)
	print "after wlist: %s" % wlist

def monitor_except(fd, target_actor):
	print "monitor_except %s" %fd
	print "before xlist: %s" % xlist
	_monitor_event(fd, target_actor, xlist, xlist_index, EXCEPT_EVT)
	print "after xlist: %s" % xlist

def unmonitor(fd):
	print "unmonitor %s" %fd
	print "before rlist: %s" % rlist
	print "before wlist: %s" % wlist
	print "before xlist: %s" % xlist
	_unmonitor_event(fd, rlist, rlist_index, READ_EVT)
	_unmonitor_event(fd, wlist, wlist_index, WRITE_EVT)
	_unmonitor_event(fd, xlist, xlist_index, EXCEPT_EVT)
	print "after rlist: %s" % rlist
	print "after wlist: %s" % wlist
	print "after xlist: %s" % rlist

def unmonitor_incoming(fd):
	print "unmonitor_incoming %s" %fd
	print "before rlist: %s" % rlist
	_unmonitor_event(fd, rlist, rlist_index, READ_EVT)
	print "after rlist: %s" % rlist

def unmonitor_outgoing(fd):
	print "unmonitor_outgoing %s" %fd
	print "before wlist: %s" % wlist
	_unmonitor_event(fd, wlist, rlist_index, WRITE_EVT)
	print "after wlist: %s" % wlist

def unmonitor_except(fd):
	print "unmonitor_except %s" %fd
	print "before wlist: %s" % xlist
	_unmonitor_event(fd, xlist, rlist_index, EXCEPT_EVT)
	print "after wlist: %s" % xlist

def update(timeout = 0):

	rl, wl, xl = select.select(rlist, wlist, xlist, timeout)

	for fd in rl:
		target = rlist_index[fd]
		target.send_data_incoming(fd)

	for fd in wl:
		target = wlist_index[fd]
		target.send_data_outgoing(fd)

	for fd in xl:
		target = xlist_index[fd]
		target.send_data_except(fd)
