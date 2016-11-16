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

    @staticmethod
    def args_for(code):
        args = {
            Opcode.op_halt: 0,
            Opcode.op_set: 2,
            Opcode.op_push: 1,
            Opcode.op_pop: 1,
            Opcode.op_eq: 3,
            Opcode.op_gt: 3,
            Opcode.op_jmp: 1,
            Opcode.op_jt: 2,
            Opcode.op_jf: 2,
            Opcode.op_add: 3,
            Opcode.op_mult: 3,
            Opcode.op_mod: 3,
            Opcode.op_and: 3,
            Opcode.op_or: 3,
            Opcode.op_not: 2,
            Opcode.op_rmem: 2,
            Opcode.op_wmem: 2,
            Opcode.op_call: 1,
            Opcode.op_ret: 0,
            Opcode.op_out: 1,
            Opcode.op_in: 1,
            Opcode.op_noop: 0,
        }

        return args[code]

class SynacorVM(object):
    INT_MAX = (2 ** 15) - 1
    REG_MAX = (2 ** 15) + 7

    def __init__(self):
        self.halt = False
        self.ip = 0
        self.stack = []
        self.mem = []
        self.reg = {i: 0 for i in range(SynacorVM.INT_MAX + 1,
                                              SynacorVM.REG_MAX + 1)}
        self.ops = {op: self.__getattribute__(op.name) for op in Opcode}

    @staticmethod
    def hex_and_char(x):
        s = '{:#06x}'.format(x)
        if 0x20 <= x <= 0x7e:
            s += " '" + chr(x) + "'"
        return s

    def dump(self, code, *args):
        print('{ip:#05x} [{reg}] {op:7} {args} <{stack}>'.format(
            ip=self.ip - 1,
            reg=' '.join(map(SynacorVM.hex_and_char, self.reg.values())),
            op=code.name,
            args=' '.join(map(SynacorVM.hex_and_char, args)),
            stack=' '.join(map(SynacorVM.hex_and_char, self.stack))))

    def load(self, path):
        with open(path, 'rb') as f:
            data = f.read()

        for v, in struct.iter_unpack('<H', data):
            self.mem.append(v)

    def fetch(self, offset=0):
        return self.mem[self.ip + offset]

    def decode(self, inst):
        for code in Opcode:
            if inst == code.value:
                return code
        assert False, 'invalid instruction: {:#x}'.format(inst)

    def set_ip(self, to=None):
        if to is None:
            to = self.ip + 1
        assert 0 <= to < len(self.mem), 'ip out of bounds: {:#x}'.format(to)
        self.ip = to
        return self.mem[self.ip]

    def advance(self, by=1):
        return self.set_ip(self.ip + by)

    def run(self):
        while not self.halt:
            inst = self.fetch()
            code = self.decode(inst)
            self.advance()

            args = [ self.fetch(i) for i in range(Opcode.args_for(code)) ]

            self.dump(code, *args)

            self.ops[code](*args)

            # jumps manage ip themselves
            if code in [Opcode.op_jmp, Opcode.op_jt, Opcode.op_jf]:
                continue

            # call and ret manage ip themselves
            if code in [Opcode.op_call, Opcode.op_ret]:
                continue

            self.advance(Opcode.args_for(code))

    def is_reg(self, addr):
        return SynacorVM.INT_MAX < addr <= SynacorVM.REG_MAX

    def dereg(self, addr):
        if self.is_reg(addr):
            return self.reg[addr]
        else:
            return addr

    def set(self, addr, val):
        if self.is_reg(addr):
            self.reg[addr] = val
        else:
            self.mem[addr] = val

    def op_halt(self):
        self.halt = True

    def op_set(self, reg, val):
        assert self.is_reg(reg)
        self.reg[reg] = val

    def op_push(self, val):
        val = self.dereg(val)
        self.stack.append(val)

    def op_pop(self, dst):
        assert self.stack
        self.set(dst, self.stack.pop())

    def op_eq(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, 1 if left == right else 0)

    def op_gt(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, 1 if left > right else 0)

    def op_jmp(self, dst):
        dst = self.dereg(dst)
        self.set_ip(dst)

    def op_jt(self, val, dst):
        val = self.dereg(val)
        dst = self.dereg(dst)
        if val != 0:
            self.set_ip(dst)
        else:
            self.advance(2)

    def op_jf(self, val, dst):
        val = self.dereg(val)
        dst = self.dereg(dst)
        if val == 0:
            self.set_ip(dst)
        else:
            self.advance(2)

    def op_add(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, (left + right) % (SynacorVM.INT_MAX + 1))

    def op_mult(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, (left * right) % (SynacorVM.INT_MAX + 1))

    def op_mod(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, left % right)

    def op_and(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, left & right)

    def op_or(self, dst, left, right):
        left = self.dereg(left)
        right = self.dereg(right)
        self.set(dst, left | right)

    def op_not(self, dst, val):
        val = self.dereg(val)
        self.set(dst, (~val) & 0x7fff)

    def op_rmem(self, dst, src):
        src = self.dereg(src)
        self.set(dst, self.mem[src])

    def op_wmem(self, dst, src):
        dst = self.dereg(dst)
        src = self.dereg(src)
        self.set(dst, src)

    def op_call(self, fn):
        self.stack.append(self.ip + 1)
        self.ip = self.dereg(fn)

    def op_ret(self):
        self.set_ip(self.stack.pop())

    def op_out(self, c):
        #print(chr(c), end='')
        pass

    def op_in(self, dst):
        s = input('synacor.vm: ')
        for c in map(ord, s):
            self.set(dst, c)
            dst += 1

    def op_noop(self):
        pass

if __name__ == '__main__':
    program = sys.argv[1]

    vm = SynacorVM()
    vm.load(program)
    vm.run()
