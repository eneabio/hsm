import hsm
from hsm import actor
from hsm import runtime

class Machine(actor.TopState):
    def __init__(self):
	self._error = None
    def on_error(self, error):
	self._error = error
	self.transition(ErrorState)

@actor.initial_state
class Off(Machine):
    def on_start(self):
	self.transition(On)

class On(Machine):
    def on_stop(self):
	self.transition(Off) 
	    
@actor.initial_state
class WaitCommand(On):
    def on_start_server(self):
	self.transition(WaitConnection) 

class WaitConnection(On):
    def on_stop_server(self):
	self.transition(WaitCommand)

class ErrorState(Machine):
    def _enter(self):   
	print "enter %s State, error code = %s" % (self.__class__.__name__, self._error)  
	
if __name__ == '__main__':

    print "test simple hsm"
    mac = Machine()
    st = mac.get_state()
    assert(Off == st)
    mac.send_start()
    runtime.dispatch_all_msg()
    st = mac.get_state()
    assert(WaitCommand == st)
    mac.send_error("ERROR 404")
    runtime.dispatch_all_msg()
    st = mac.get_state()
    assert(ErrorState == st)    