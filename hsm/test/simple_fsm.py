import hsm
from hsm import actor
from hsm import runtime

class Machine(actor.TopState):
    def _error(self):
	self.transition(ErrorState)
	
@actor.initial_state
class Off(Machine):
    def on_start(self):
	self.transition(On)
	
class On(Machine):
    def on_stop(self):
	    self.transition(Off) 
	    
class ErrorState(Machine):
    def on_error(self):
	print "Error"

if __name__ == '__main__':
    print "test simple fsm"
    mac = Machine()
    st = mac.get_state()
    assert(Off == st)
    mac.send_start()
    runtime.dispatch_all_msg()
    st = mac.get_state()
    assert(On == st)