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
        self._defs = {}
        self._values = {'default':dict()}
        self.profile = 'default'
    def define(self,id,desc="",type="string",group="default",value=None):
        if not id in self._defs.keys():
            self._defs[id] = dict(desc=desc,type=type,group=group,value=value)
        else:
            raise ParameterError('Parameter already defined')
    def createProfile(self,profile):
        if not profile in self._params.keys():
            self._params[profile] = dict()
        else:
            raise ParameterError('Profile already created')
    def selectProfile(self,profile):
        if profile in self._params.keys():
            self.profile = profile
        else:
            raise ParameterError('Profile not found')
            
    def __getattr__(self,id):
        if id in self._params[self.profile].keys():
            return self._params[self.profile][id]['value']
        elif id in self._params['default'].keys():
            return self._params['default'][id]['value']
        else:
            raise ParameterError('Parameter not found')

    def __setattr(self,id,value):
        if id in self._params['default'].keys():
            self._params[self.profile]['value'] = value
        else:
            raise ParameterError('Parameter not found')
