# -*- coding: utf-8 -*-

from threading import Thread
import json


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ParameterError(Error):
    """Exception raised for errors in the input.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self,msg):
        self.msg = msg

class Properties(object):
    def __init__(self,parameters,profile):
        self._parameters = parameters
        self._profile = profile
    def __getattr__(self,name):
        if name in ['_parameters','_profile']:
            return super(Properties,self).__getattr__(name)
        elif name == '_all_':
            return self._parameters.getProfile(self._profile)
        elif name in self._parameters._values[self._profile].keys():
            return self._parameters._values[self._profile][name]
        elif name in self._parameters._values['default'].keys():
            return self._parameters._values['default'][name]
        else:
            raise ParameterError('Parameter not found')

    def __setattr__(self,name,value):
        if name in ['_parameters','_profile']:
            super(Properties,self).__setattr__(name,value)
        elif name == '_all_':
            self._parameters.setProfile(self._profile,value)
        elif name in self._parameters._values['default'].keys():
            self._parameters._values[self._profile][name] = value
            if name in self._parameters._hooks.keys():
                self._parameters.executeHooks(name)
        else:
            raise ParameterError('Parameter not found')
            
    

class Parameters(object):
    def __init__(self,defs={},values={'default':dict()}):
        # id, name, desc, type, group, profile
        self._defs = defs
        self._values = values
        self._hooks = dict()
    
            
    def setHook(self,id,hook,execute=False):
        if id in self._defs.keys():
            self._hooks[id] = self._hooks.get(id,[]) + [hook]
            if execute:
                Thread(target=hook).start()
        else:
            raise ParameterError('Parameter not found')
    def executeHooks(self,name):
        if name in self._hooks.keys():
            for hook in self._hooks[name]:
                Thread(target=hook).start()
    def save(self,filename):
        try:
            with open(filename,'w+') as f:
                f.write(json.dumps(dict(defs=self._defs,values=self._values),sort_keys=True,
                  indent=4, separators=(',', ': ')))
        except:
            raise ParameterError('unable to save parameters!')
            
    def load(self,filename):
        with open(filename,'r') as f:
            data = json.load(f)
        for id,value in data['defs'].iteritems():
            if id in self._defs.keys():
                self._defs[id] = value
                
        for profile in data['values'].keys():
             if not profile in self._values.keys():
                self.createProfile(profile)
             prof = self.profile(profile)
             for id,value in data['values'][profile].iteritems():
                   setattr(prof,id,value)
        #raise ParameterError('unable to load parameters')
            
    def define(self,id,desc="",type="string",group="default",default=None):
        self._defs[id] = dict(desc=desc,type=type,group=group,default=default)
        if not id in self._values.keys():
            self._values['default'][id] = default
            
    def createProfile(self,profile):
        if not profile in self._values.keys():
            self._values[profile] = dict()
        else:
            raise ParameterError('Profile already created')

    def profile(self,profile="default"):
        if profile in self._values.keys():
            return Properties(self,profile)
        else:
            raise ParameterError('Profile not found')

    def getProfile(self,profile="default"):
        if profile in self._values.keys():
            dp = self._values['default']
            cp = self._values[profile]
            return dict((k,cp[k] if k in cp.keys() else dp[k]) for k in self._defs.keys())
        else:
            raise ParameterError('Profile not found')

    def setProfile(self,profile,properties):
        if profile in self._values.keys():
            dp = self._values['default']
            cp = self._values[profile]
            for k,v in properties.iteritems():
                if k in cp.keys():
                    if v != dp[k]:
                        cp[k] = v
                    elif profile != 'default':
                        del cp[k]
                else:
                    if v!= dp[k]:
                        cp[k] = v
                self.executeHooks(k)
    def getDefs(self):
        return self._defs
                                    
    def defs(self,id):
        if id in self._defs.keys():
            return self._defs[id]            
        else:
            raise ParameterError('Parameter not found')
            

