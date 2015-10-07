class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ParameterError(Error):
    """Exception raised for errors in the input.

    Attributes:
        name -- name of parameter
        msg  -- explanation of the error
    """

    def __init__(self,msg):
        self.msg = msg

class Parameters:
    def __init__(self):
        # id, name, desc, type, group, profile
        self._params = {}
    def define(self,id,desc="",type="string",group="default",profile="default",value=None):
        if not id in self._params.keys():
            self._params[id] = dict(desc=desc,type=type,group=group,profile=profile,value=value)
        else:
            raise ParameterError('Parameter already defined')
    def __getattr__(self,id):
        return self._params[id]['value']
    def __setattr(self,id,value):
        self._params[id]['value'] = value

