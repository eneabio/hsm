# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

"""
iomonitor - monitor file descriptors for io events.
Note:
 - on windows works only for sockets.

*monitor_xxx(fd, target_actor)*:
  starts monitoring a fd for events and binds a target actor to a file
  descriptor. The *target_actor* will receive the events when data is available, 
  data has been sent or an exception has occurred on the fd.

*unmonitor_xxx(fd)*:
  stops monitoring a fd for events

*update()*:
   - sends "data_arrived" to a monitoring actors if data si available for reading
   - sends "data_sent"    to a monitoring actors if data has been sent
   - sends "data_except"  to a monitoring actors an error has occurred on the bound fd

"""

import select

__all__ = ["monitor", "monitor_incoming", "monitor_outgoing", "monitor_except",
           "unmonitor", "unmonitor_incoming", "unmonitor_outgoing", "unmonitor_except",
           "update", "reset"
]

rlist = []
wlist = []
xlist = []

rlist_index = {}
wlist_index = {}
xlist_index = {}

state_index = {}

READ_EVT = 0
WRITE_EVT = 1
EXCEPT_EVT = 2


def reset():
    global rlist
    global wlist
    global xlist
    global rlist_index
    global wlist_index
    global xlist_index
    global state_index

    rlist = []
    wlist = []
    xlist = []
    rlist_index = {}
    wlist_index = {}
    xlist_index = {}
    state_index = {}


def _monitor_event(fd, target_actor, fdlist, list_index, evt):
    assert fd is not None
    #is it registered ?
    if state_index.has_key(fd):
        index_vec = state_index[fd]
        #is it already monitored ?
        if index_vec[evt] == -1:
            #not monitored
            index = fdlist.__len__()
            index_vec[evt] = index
            fdlist.append(fd)
            list_index[fd] = target_actor

        #already monitored
        #do nothing
        return

    #Not registered
    index_vec = [-1, -1, -1] #Create index vector
    state_index[fd] = index_vec
    index_vec[evt] = fdlist.__len__()
    fdlist.append(fd)
    list_index[fd] = target_actor
    return


def _unmonitor_event(fd, fdlist, list_index, evt):
    if not fdlist:
        return # nothing is being monitored
    if list_index.has_key(fd):
        index_vec = state_index[fd]
        index = index_vec[evt]
        if index == -1:
            #registered but not monitored
            #do nothing
            return
        list_len = fdlist.__len__()
        assert index < list_len
        if list_len - 1 == index:
            #it the last one! just pop it ...
            fdlist.pop()
            del list_index[fd]
            state_index[fd][evt] = -1
        else:
            # pop not the last one
            last = fdlist.pop()
            last_vec_index = state_index[last]
            deleted_vec_index = state_index[fd]
            deleted_pos = deleted_vec_index[evt]
            last_vec_index[evt] = deleted_pos
            fdlist[index] = last
            del list_index[fd]
            #check if we need to clear the state index
        if index_vec[0] == -1 and index_vec[1] == -1 and index_vec[2] == -1:
            del state_index[fd]


def monitor(fd, target_actor):
    _monitor_event(fd, target_actor, rlist, rlist_index, READ_EVT)
    _monitor_event(fd, target_actor, wlist, wlist_index, WRITE_EVT)
    _monitor_event(fd, target_actor, xlist, xlist_index, EXCEPT_EVT)
    return


def monitor_incoming(fd, target_actor):
    _monitor_event(fd, target_actor, rlist, rlist_index, READ_EVT)


def monitor_outgoing(fd, target_actor):
    _monitor_event(fd, target_actor, wlist, wlist_index, WRITE_EVT)


def monitor_except(fd, target_actor):
    _monitor_event(fd, target_actor, xlist, xlist_index, EXCEPT_EVT)


def unmonitor(fd):
    _unmonitor_event(fd, rlist, rlist_index, READ_EVT)
    _unmonitor_event(fd, wlist, rlist_index, WRITE_EVT)
    _unmonitor_event(fd, xlist, rlist_index, EXCEPT_EVT)


def unmonitor_incoming(fd):
    _unmonitor_event(fd, rlist, rlist_index, READ_EVT)


def unmonitor_outgoing(fd):
    _unmonitor_event(fd, wlist, rlist_index, WRITE_EVT)


def unmonitor_except(fd):
    _unmonitor_event(fd, xlist, rlist_index, EXCEPT_EVT)


def update(timeout=0):
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