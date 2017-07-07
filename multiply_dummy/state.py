"""
define state vector
"""


class State(object):

    def __init__(self, **kwargs):
        self.state = kwargs.get('state', None)
        assert self.state is not None


class TargetState(State):

    def __init__(self, **kwargs):
        super(TargetState, self).__init__(**kwargs)
