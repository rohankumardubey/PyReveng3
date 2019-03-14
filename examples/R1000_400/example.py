#!/usr/bin/env python
#
# Copyright (c) 2012-2014 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

from __future__ import print_function

import os
from pyreveng import job, mem, listing, data, code, assy, pil
import pyreveng.cpu.m68020 as m68020

def mem_setup():
	o = 1<<31
	m = mem.byte_mem(o, o | 0x8000)

	filename=os.path.join(os.path.dirname(__file__), "IOC_EEPROM.bin")

	# The PCB layout swaps the top two address lines to the EEPROM
	for oo, lo, hi in (
		(0x0000, 0x0000, 0x2000),
		(0x4000, 0x2000, 0x4000),
		(0x2000, 0x4000, 0x6000),
		(0x6000, 0x6000, 0x8000),
	):
		m.load_binfile(
			first = o + oo,
			step = 0x1,
			filename=filename,
			lo = lo,
			hi = hi);
	return m

my68k20_instructions = """
#               src,dst         ea      |_ _ _ _|_ _ _v_|_ _v_ _|_v_ _ _|_ _ _ _|_ _ _ _|_ _ _ _|_ _ _ _|

INLTXT		inltxt		0	|0 1 0 0 1 1 1 0 1 0 0 1 0 1 1 0| a1            | a2            |
"""

class my68k20_ins(m68020.m68020_ins):

	def assy_inltxt(self, pj):
		y = data.Txt(pj, self.lo + 2, label=False)
		pj.todo(y.hi, self.lang.disass)
		raise assy.Invalid("Inline text hack")

class my68k20(m68020.m68020):
	def __init__(self, lang="my68k20"):
		super().__init__(lang)
		self.it.load_string(my68k20_instructions)
		self.myleaf = my68k20_ins

def inline_text(pj, ins):
	if not ins.dstadr in (
		0x8000001c,
		0x800000e2,
		0x80002028,
		0x80002aa8,
	):
		return
	if ins.lo == 0x8000001c:
		return
	y = data.Txt(pj, ins.hi, label=False)
	pj.todo(y.hi, ins.lang.disass)

def setup():
	m = mem_setup()

	pj = job.Job(m, "R1000_400")
	cpu = my68k20()
	cpu.set_adr_mask(0x7fffffff)
	cpu.flow_check.append(inline_text)
	cpu.trap_returns[0] = True
	return pj, cpu


#######################################################################

def task(pj, cpu):

	#cpu.vectors(pj, hi=0x28)
	pj.todo(0x80000024, cpu.disass)
	for a in (
		0x80000072,
		0x80000156,
		0x800001c4,
		0x80000314,
		0x80000374,
		0x80000552,
		0x80002a24,
		0x80002a2c,
		0x800033ce,
		0x80003690,
		0x80004afe,
		0x80004b42,
		0x80004b68,
		0x80007e0b,
	):
		data.Txt(pj, a, label=False)

	def txts(a, b, align=2):
		while a < b:
			y = data.Txt(pj, a, label=False, align=align)
			a = y.hi

	txts(0x800010cc, 0x80001122)
	txts(0x80001bb0, 0x80001bc2)
	txts(0x8000221c, 0x800024a8)
	txts(0x80002c14, 0x80002e04, align=1)
	txts(0x80004ece, 0x80004fbf, align=1)
	txts(0x800027ee, 0x800028ca, align=1)

	for a in (
		0x8000000c,
		0x80000010,
		0x80000014,
		0x80000018,
		0x8000001c,
		0x80000020,
		0x800001f6,
		0x80000208,
		0x8000021a,
		0x80001524,
		0x80001566,
		0x800015a8,
		0x80001628,
		0x800016c2,
		0x800027ca,
		0x80002bbe,
		0x80002bc4,
		0x800040a0,
	):
		pj.todo(a, cpu.disass)

	for a in range(0x80002000, 0x80002074, 4):
		pj.todo(a, cpu.disass)

	for a in range(0x8000310e, 0x80003122, 4):
		cpu.codeptr(pj, a)

	for a in range(0x800038ce, 0x800038ee, 4):
		cpu.codeptr(pj, a)

	for a in range(0x80004000, 0x80004008, 4):
		pj.todo(a, cpu.disass)

	for a in range(0x800043aa, 0x80004492, 6):
		y = data.Const(pj, a, a + 4, func=pj.m.bu32, size=4)
		z = data.Const(pj, y.hi, y.hi + 2, func=pj.m.bu16, size=2)
		w = pj.m.bu16(a + 4)
		w >>= 4
		w &= 0xffe
		d = 0x800043aa + w
		pj.todo(d, cpu.disass)


	for a in range(0x80004a7a, 0x80004a98, 4):
		d = pj.m.bu32(a)
		data.Dataptr(pj, a, a + 4, d)
		data.Txt(pj, d, align=1)

	for a in range(0x800036e8, 0x800036fc, 4):
		d = pj.m.bu32(a)
		data.Dataptr(pj, a, a + 4, d)
		data.Txt(pj, d)

	data.Const(pj, 0x80001ffa, 0x80002000)
	data.Const(pj, 0x80003ffa, 0x80004000)
	data.Const(pj, 0x80005ffa, 0x80006000)
	data.Const(pj, 0x80007dfa, 0x80007e00)

	while pj.run():
		pass

	return

#######################################################################

if __name__ == '__main__':
	pj, cx = setup()
	task(pj, cx)
	code.lcmt_flows(pj)
	listing.Listing(pj, ncol=8, pil=False)