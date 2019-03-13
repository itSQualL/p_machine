Take a look to the branches to see the different implementations.

Remember to configure `p_machine/states` dictionaries config.

# PMachine
`p_machine` implements a simple automata that receives an initial state
that must implements `run` method and `next` method from `AbstractState`
class.

First runs `run` method and then `next` method, if `next` returns `None`
it stops.

