# py/pyext - python script objects for PD and MaxMSP
#
# Copyright (c) 2002-2005 Thomas Grill (gr@grrrr.org)
# For information on usage and redistribution, and for a DISCLAIMER OF ALL
# WARRANTIES, see the file, "license.txt," in this distribution.
#

"""This is an example script for the py/pyext object's send/receive functionality.

You can:
- bind


There are several classes exposing py/pyext features:
- ex1: A class receiving messages and sending them out again
- ex2: A class receiving messages and putting them out to an outlet
- ex3: Do some PD scripting

"""

try:
	import pyext
except:
	print "ERROR: This script must be loaded by the PD/Max pyext external"


from time import sleep
import random

#################################################################

def recv_gl(arg):
	"""This is a global receive function, it has no access to class members."""
	print "GLOBAL",arg

class ex1(pyext._class):
	"""Example of a class which receives and sends messages

	It has two creation arguments: a receiver and a sender name.
	There are no inlets and outlets.
	Python functions (one global function, one class method) are bound to PD's or Max/MSP's receive symbols.
	The class method sends the received messages out again.
	"""


	# no inlets and outlets
	_inlets=1
	_outlets=0

	recvname=""
	sendname=""

	def recv(self,*arg):
		"""This is a class-local receive function, which has access to class members."""

		# print some stuff
		print "CLASS",self.recvname,arg

		# send data to specified send address
		self._send(self.sendname,arg)


	def __init__(self,*args):
		"""Class constructor"""

		# store sender/receiver names
		if len(args) >= 1: self.recvname = args[0]
		if len(args) >= 2: self.sendname = args[1]

                self.bind_1()

        def bind_1(self):
		# bind functions to receiver names
		# both are called upon message
		self._bind(self.recvname,self.recv)
		self._bind(self.recvname,recv_gl)

        def unbind_1(self):
		self._unbind(self.recvname,self.recv)
		self._unbind(self.recvname,recv_gl)

	def __del__(self):
		"""Class destructor"""

		# unbinding is automatically done at destruction
		pass


#################################################################

class ex2(pyext._class):
	"""Example of a class which receives a message and forwards it to an outlet

	It has one creation argument: the receiver name.
	"""


	# define inlets and outlets
	_inlets=0
	_outlets=1

	recvname=""

	def recv(self,*arg):
		"""This is a class-local receive function"""

		# send received data to outlet
		self._outlet(1,arg)


	def __init__(self,rname):
		"""Class constructor"""

		# store receiver names
		self.recvname = rname

		# bind function to receiver name
		self._bind(self.recvname,self.recv)


#################################################################

from math import pi,sin
from cmath import exp
from random import random,randint
import numpy as np

class hello(pyext._class):
	"""Example of a class which does some object manipulation by scripting"""


	# define inlets and outlets
	_inlets=1
	_outlets=0

	def __init__(self):
		"""Class constructor"""

	def bang_1(self):
		"""Do some scripting - PD only!"""
		print "hi"

class hellosig(pyext._class):

	t = 0.0
	f = 0.0

	def bang_3(self):
		print "SR:",self._samplerate(),"BS:",self._blocksize(),"F:",self.f

	def _dsp(self):
        # if _dsp is present it must return True to enable DSP
		return pyext._arraysupport()

	def _signal(self):
		# not great, since
		# only allow f to change once per block
		self.f = self._invec(0)[0]
		d = self.f*2.0*pi*(self._blocksize()/self._samplerate())

		x = np.linspace(self.t,self.t+d,self._blocksize()+1)[:-1]

		self._outvec(0)[:] = np.sin(x)
		# self._outvec(0)[:] = np.random.random(self._blocksize())
		# self._outvec(0)[:] = 1-np.mod(x,2*np.pi)/(2*np.pi)

		self.t += d
		# print(np.sin(x))

	def __signal(self):
		# a bit better since we can change f freely
		# but quite a bit more expensive for some reason
		for i in range(0, self._blocksize()):
			f = self._invec(0)[i]
			d = (f / self._samplerate()) * 2.0 * pi
			self.t += d
			self._outvec(0)[i] =  sin(self.t)
			# not strictly necessary
			if self.t > 2.0*pi:
			  self.t -= 2.0*pi
