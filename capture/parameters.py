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

class Parameters(object):
    def __init__(self):
        # id, name, desc, type, group, profile
        self._defs = {}
        self._values = {'default':dict()}
        self._profile = 'default'
    def define(self,id,desc="",type="string",group="default",default=None):
        if not id in self._defs.keys():
            self._defs[id] = dict(desc=desc,type=type,group=group,default=default)
            self._values['default'][id] = default
        else:
            raise ParameterError('Parameter already defined')
    def createProfile(self,profile):
        if not profile in self._values.keys():
            self._values[profile] = dict()
        else:
            raise ParameterError('Profile already created')
    def selectProfile(self,profile='default'):
        if profile in self._values.keys():
            self._profile = profile
        else:
            raise ParameterError('Profile not found')
    def currentProfile(self):
        return self._profile
    def defs(self,id):
        if id in self._defs.keys():
            return self._defs[id]            
        else:
            raise ParameterError('Parameter not found')
            
    def __getattr__(self,id):
        if id in ['_defs','_values','_profile']:
            super(Parameters,self).__getattr__(id)
        if id in self._values[self._profile].keys():
            return self._values[self._profile][id]
        elif id in self._values['default'].keys():
            return self._values['default'][id]
        else:
            raise ParameterError('Parameter not found')

    def __setattr__(self,id,value):
        if id in ['_defs','_values','_profile']:
            super(Parameters,self).__setattr__(id,value)
        elif id in self._values['default'].keys():
            
            self._values[self._profile][id] = value
        else:
            raise ParameterError('Parameter not found')
