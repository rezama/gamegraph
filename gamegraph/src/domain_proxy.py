'''
Created on Sep 17, 2011

@author: reza
'''
from domain import MiniGammonState, NannonState, MidGammonState,\
    NohitGammonState

class DomainProxy(object):
    
    @classmethod
    def load_domain_state_class_by_name(cls, domain_name):
        print 'Loading Domain: %s' % domain_name
        print 
        result = None
        if domain_name == MiniGammonState.DOMAIN_NAME:
            result = MiniGammonState
        elif domain_name == NannonState.DOMAIN_NAME:
            result = NannonState
        elif domain_name == MidGammonState.DOMAIN_NAME:
            result = MidGammonState
        elif domain_name == NohitGammonState.DOMAIN_NAME:
            result = NohitGammonState
        return result

#class DomainProxy(object):
#    
#    @classmethod
#    def load_domain_by_name(cls, domain_name):
#        print 'Loading Domain: %s' % domain_name
#        print 
#        result = None
#        if domain_name == DomainMiniGammon.name:
#            result = DomainMiniGammon
#        elif domain_name == DomainNannon.name:
#            result = DomainNannon
#        elif domain_name == DomainMidGammon.name:
#            result = DomainMidGammon
#        elif domain_name == DomainNohitGammon.name:
#            result = DomainNohitGammon
#        return result
#
#class DomainMiniGammon(object):
#    name = 'minigammon'
#    DieClass = MiniGammonDie
#    StateClass = MiniGammonState
#    ActionClass = MiniGammonAction
#    AgentClass = MiniGammonAgent
#    AgentRandomClass = MiniGammonAgentRandom
#    AgentNeuralClass = MiniGammonAgentNeural
#
#
#class DomainNannon(object):
#    name = 'nannon'
#    DieClass = NannonDie
#    StateClass = NannonState
#    ActionClass = NannonAction
#    AgentClass = NannonAgent
#    AgentRandomClass = NannonAgentRandom
#    AgentNeuralClass = NannonAgentNeural
#    
#class DomainMidGammon(object):
#    name = 'midgammon'
#    DieClass = MidGammonDie
#    StateClass = MidGammonState
#    ActionClass = MidGammonAction
#    AgentClass = MidGammonAgent
#    AgentRandomClass = MidGammonAgentRandom
#    AgentNeuralClass = MidGammonAgentNeural
#
#class DomainNohitGammon(object):
#    name = 'nohitgammon'
#    DieClass = NohitGammonDie
#    StateClass = NohitGammonState
#    ActionClass = NohitGammonAction
#    AgentClass = NohitGammonAgent
#    AgentRandomClass = NohitGammonAgentRandom
#    AgentNeuralClass = NohitGammonAgentNeural

