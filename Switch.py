# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015	    												

from Message import *
from StpSwitch import *

class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):    
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)
        
        #TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.
        self.data = dict()
        self.data['root'] = idNum
        self.data['distance'] = 0
        self.data['actives'] = set()
        self.data['passthru'] = idNum 
        self.data['ispassthru'] = False

        self.linkdata = dict()
        for l in self.links:
            self.linkdata[l] = dict()
            self.linkdata[l]['root'] = None
            self.linkdata[l]['distance'] = None
            self.linkdata[l]['ispassthru'] = None


    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	#      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)

        for l in self.links:
            m = Message(self.switchID,0,self.switchID,l,False)
            self.send_message(m)

        return
        
    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

        '''
        Implementation:

        As messages arrive, update the info structures that contain the information for the 
        node's neighbors. After the information is updated, update the node's information
        accordingly. Then, as the root or passthru changed send messages reflecting the
        change to its neighbor's
        '''

        self.linkdata[message.origin]['root'] = message.root
        self.linkdata[message.origin]['distance'] = message.distance
        self.linkdata[message.origin]['ispassthru'] = message.pathThrough

        rootChanged = False
        passThruChanged = False
        isPassThruChanged = False

        ispassthru = self.data['ispassthru']

        for l in self.links:
            if self.linkdata[l]['root'] is None:
                continue;
            if self.linkdata[l]['root'] < self.data['root']:
                self.data['root'] = self.linkdata[l]['root']
                self.data['distance'] = self.linkdata[l]['distance']+1
                self.data['passthru'] = l
                rootChanged = True
            if self.linkdata[l]['root'] == self.data['root'] and self.linkdata[l]['distance'] + 1 < self.data['distance']:
                self.data['distance'] = self.linkdata[l]['distance']+1
                self.data['passthru'] = l
                passThruChanged = True
            if self.linkdata[l]['root'] == self.data['root'] and self.linkdata[l]['distance'] + 1 == self.data['distance'] and l < self.data['passthru']:
                self.data['passthru'] = l
                passThruChanged = True

        for l in self.links:
            if l == self.data['root']:
                self.data['actives'].add(l)
            elif l == self.data['passthru']:
                self.data['actives'].add(l)
            elif self.linkdata[l]['ispassthru']:
                self.data['actives'].add(l)
            elif not self.linkdata[l]['ispassthru'] and l in self.data['actives']:
                self.data['actives'].remove(l)

        if rootChanged or passThruChanged:
            for l in self.links:
                ispassthru = self.data['passthru'] == l
                m = Message(self.data['root'],self.data['distance'],self.switchID,l,ispassthru)
                self.send_message(m)
        

        return
        
    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.
        
        self.data['actives'] = sorted(self.data['actives'])
        log = ""

        for a in self.data['actives']:
            log += str(self.switchID) + " - " + str(a) + ", "
        
        if len(log) > 0:
            log = log[:-2]


        return log
