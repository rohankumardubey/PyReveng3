#!/usr/bin/env python
#
# Copyright (c) 2012-2021 Poul-Henning Kamp <phk@phk.freebsd.dk>
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

'''
   Third quarter of the IOC EEPROM
   -------------------------------
'''

import os

from pyreveng import mem, data

import ioc_utils
import ioc_hardware
import ioc_eeprom_exports

NAME = "IOC_EEPROM_PART3"
BASE = 0x80004000
SIZE = 0x2000

FILENAME = os.path.join(os.path.split(__file__)[0], "IOC_EEPROM.bin")
#######################################################################

class IocEepromPart3(ioc_utils.IocJob):
    ''' Third quarter of IOC EEPROM image '''

    def __init__(self, **kwargs):
        super().__init__(BASE, BASE+SIZE, name=NAME, **kwargs)

    def default_image(self):
        ''' Load default image '''
        self.map(mem.Stackup((FILENAME,)), offset=0x2000)

    def config_cx(self):
        ''' Add global symbol sets etc. '''
        cx = self.cx
        ioc_eeprom_exports.add_flow_check(cx)
        ioc_eeprom_exports.add_symbols(cx.m)
        ioc_hardware.add_symbols(cx.m)

    def round_0(self):
        ''' Things to do before the disassembler is let loose '''

    def round_1(self):
        ''' Let the disassembler loose '''
        cx = self.cx
        for a in range(0x80004000, 0x80004008, 4):
            cx.disass(a)

    def round_2(self):
        ''' Spelunking in what we alrady found '''
        cx = self.cx
        ioc_eeprom_exports.add_exports(
             cx.m,
             ioc_eeprom_exports.IOC_EEPROM_PART3_EXPORTS
        )

    def round_0_232718caeffce073(self):
        ''' Things to do before the disassembler is let loose '''
        cx = self.cx

        for a in (
            0x80004afe,
            0x80004b42,
            0x80004b68,
            0x80004ece,
            0x80004eeb,
            0x80004f17,
            0x80004f2c,
            0x80004f40,
            0x80004f56,
            0x80004f74,
            0x80004f8a,
            0x80004f95,
            0x80004fac,
        ):
            data.Txt(cx.m, a, splitnl=True)

    def round_1_232718caeffce073(self):
        ''' Let the disassembler loose '''
        cx = self.cx

        for a, b in (
            (0x800040a0, None),
            (0x80004498, None),
            (0x800044a4, None),
            (0x800044c8, None),
            (0x800044f8, None),
            (0x80004510, None),
            (0x8000456c, None),
            (0x80004578, None),
            (0x80004648, None),
            (0x800046aa, None),
            (0x800046c2, None),
            (0x800046d0, None),
            (0x80004730, None),
            (0x80004862, None),
            (0x80004912, None),
            (0x80004ad2, None),
            (0x80004ae8, None),
            (0x80004b10, None),
            (0x80004b8c, None),
            (0x80004cd0, None),
        ):
            cx.disass(a)
            cx.m.set_line_comment(a, "MANUAL")
            if b:
                cx.m.set_label(a, b)


#######################################################################

def example():
    ''' Follow the example protocol '''
    return IocEepromPart3().example()

#######################################################################

if __name__ == '__main__':
    ioc_utils.mainfunc(__file__, example, IocEepromPart3)
