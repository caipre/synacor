#!/usr/bin/env python3

import struct
import sys
import enum

@enum.unique
class Opcode(enum.Enum):
    op_halt = 0
    op_set  = 1
    op_push = 2
    op_pop  = 3
    op_eq   = 4
    op_gt   = 5
    op_jmp  = 6
    op_jt   = 7
    op_jf   = 8
    op_add  = 9
    op_mult = 10
    op_mod  = 11
    op_and  = 12
    op_or   = 13
    op_not  = 14
    op_rmem = 15
    op_wmem = 16
    op_call = 17
    op_ret  = 18
    op_out  = 19
    op_in   = 20
    op_noop = 21

class SynacorVM(object):
    INT_MAX = (2 ** 15) - 1

    def __init__(self):
        self.pc = 0
        self.mem = []
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]

        self.ops = {
            Opcode.op_out: self.op_out,
        }

    def load(self, path):
        with open(path, 'rb') as f:
            data = f.read()

        for v, in struct.iter_unpack('<H', data):
            self.mem.append(v)

    def fetch(self):
        return self.mem[self.pc]

    def decode(self, inst):
        for code in Opcode:
            if inst == code.value:
                return code
        assert False, 'invalid instruction: {:#x}'.format(inst)

    def set_pc(self, to=1):
        if to is None:
            to = self.pc + 1
        assert 0 <= to < len(self.mem), 'pc out of bounds: {:#x}'.format(to)
        self.pc = to
        return self.mem[self.pc]

    def advance(self, by=1):
        return self.set_pc(self.pc + by)

    def run(self):
        while True:
            args = []

            inst = self.fetch()
            code = self.decode(inst)
            self.advance()

            #print(inst, code)

            if code == Opcode.op_halt:
                break
            elif code == Opcode.op_noop:
                continue
            elif code == Opcode.op_out:
                args = [ self.fetch() ]
            else:
                raise Exception

            self.ops[code](*args)

            for _ in range(len(args)):
                self.advance()

    def op_out(self, character):
        print(chr(character), end='')


if __name__ == '__main__':
    program = sys.argv[1]

    vm = SynacorVM()
    vm.load(program)
    vm.run()
