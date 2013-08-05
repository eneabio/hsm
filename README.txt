==========
 Hsm 0.1.2
==========

Hsm is a hierarchical state machines library designed for
very large hand written state machines.

Hsm is designed to be concise, i.e. let the user read and write 
state machines very easily.

It defines a custom metaclass to support:
  - *classes* as states
  - *on_xxx methods* as event handler
  - automatically adds send_xxx when an on_xx handler is available
  - @initial_state to define the initial state of a non-leaf state
  - @error_state to define the error_state of a non-leaf state
  - @trace_state(logger) to set the trace logger for a state and all it's children
  
Faster, simpler to write, easier to read the other python hsm frameworks.
  
Check the hsm.test and doc/ for documentation. More formal documentation available soon.

Quick guide
------------



Cheers

*Contributor List*:
 - Fabio N. Filasieno
 - Enea Bionda


