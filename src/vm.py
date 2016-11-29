#!/usr/bin/env python3

import struct
import sys

class SynacorVM(object):
    def __init__(self):
        self.input = ''
        self.calls = {}
        self.debug_enabled = False

        self.memory = [0 for _ in range(2 ** 15)]
        self.registers = {i: 0 for i in range(32768, 32776)}
        self.stack = []

        self.ops = {
             0: self.op_halt,
             1: self.op_set,
             2: self.op_push,
             3: self.op_pop,
             4: self.op_eq,
             5: self.op_gt,
             6: self.op_jmp,
             7: self.op_jt,
             8: self.op_jf,
             9: self.op_add,
            10: self.op_mult,
            11: self.op_mod,
            12: self.op_and,
            13: self.op_or,
            14: self.op_not,
            15: self.op_rmem,
            16: self.op_wmem,
            17: self.op_call,
            18: self.op_ret,
            19: self.op_out,
            20: self.op_in,
            21: self.op_noop,
        }

    def load(self, path):
        with open(path, 'rb') as f:
            program = f.read()

        self.memory = [word for word, in struct.iter_unpack('<H', program)]

    @staticmethod
    def hex_and_chr(num):
        str = '{:#06x}'.format(num)
        if 0x20 <= num <= 0x7e:
            str += " '{}'".format(chr(num))
        return str

    @staticmethod
    def argc_for(code):
        if code in (0, 18, 21):
            return 0
        elif code in (2, 3, 6, 17, 19, 20):
            return 1
        elif code in (1, 7, 8, 14, 15, 16):
            return 2
        elif code in (4, 5, 9, 10, 11, 12, 13):
            return 3
        return 0

    def debug(self, iptr):
            code = self.memory[iptr]
            if 0 <= code <= 21:
                name = self.ops[code].__name__
                args = [self.memory[iptr+1+i] for i in range(self.argc_for(code))]
            else:
                name = hex(code)
                args = []


            args = ' '.join(map(self.hex_and_chr, args))
            print('\n{reg}\n'
                  '{stack}\n'
                  '{addr:#06x} {name:<7} {args}\n'
                  .format(
                    reg=' '.join(map(self.hex_and_chr, self.registers.values())),
                    stack=' '.join(map(self.hex_and_chr, self.stack)),
                    addr=iptr,
                    name=name,
                    args=args
            ))

    def run(self):
        iptr = 0
        while True:
            if iptr == 0x1571:
                assert self.registers[0x8007] != 0
                iptr = 0x157a
            code = self.memory[iptr]
            iptr = self.ops[code](iptr)
            if iptr == 0: break

    def dis(self):
        iptr = 0
        while iptr < len(self.memory):
            code = self.memory[iptr]
            if 0 <= code <= 21:
                name = self.ops[code].__name__
                args = [self.memory[iptr+1+i] for i in range(self.argc_for(code))]
            else:
                name = '{:#06x}'.format(code)
                args = []

            args = ' '.join(map(self.hex_and_chr, args))
            print('{iptr:#06x} {name:<7} {args}'
                  .format(iptr=iptr, name=name, args=args))

            iptr += 1 + self.argc_for(code)

    def getmem(self, address):
        val = self.memory[address]
        if val >= 32768:
            return self.registers[val]
        return val

    def setmem(self, address, val):
        idx = self.memory[address]
        if idx >= 32768:
            self.registers[idx] = val
        else:
            self.memory[idx] = val

    # instruction handlers
    #

    def op_halt(self, address):
        return 0

    def op_set(self, address):
        val = self.getmem(address + 2)
        self.setmem(address + 1, val)
        return address + 3

    def op_push(self, address):
        val = self.getmem(address + 1)
        self.stack.append(val)
        return address + 2

    def op_pop(self, address):
        assert self.stack, 'pop on empty stack'
        val = self.stack.pop()
        self.setmem(address + 1, val)
        return address + 2

    def op_eq(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, 1 if b == c else 0)
        return address + 4

    def op_gt(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, 1 if b > c else 0)
        return address + 4

    def op_jmp(self, address):
        return self.getmem(address + 1)

    def op_jt(self, address):
        a = self.getmem(address + 1)
        if a != 0:
            return self.getmem(address + 2)
        return address + 3

    def op_jf(self, address):
        a = self.getmem(address + 1)
        if a == 0:
            return self.getmem(address + 2)
        return address + 3

    def op_add(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, (b + c) % 32768)
        return address + 4

    def op_mult(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, (b * c) % 32768)
        return address + 4

    def op_mod(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, (b % c) % 32768)
        return address + 4

    def op_and(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, (b & c) % 32768)
        return address + 4

    def op_or(self, address):
        b = self.getmem(address + 2)
        c = self.getmem(address + 3)
        self.setmem(address + 1, (b | c) % 32768)
        return address + 4

    def op_not(self, address):
        b = self.getmem(address + 2)
        self.setmem(address + 1, (~b) & 0x7fff)
        return address + 3

    def op_rmem(self, address):
        b = self.getmem(address + 2)
        self.setmem(address + 1, self.getmem(b))
        return address + 3

    def op_wmem(self, address):
        a = self.getmem(address + 1)
        b = self.getmem(address + 2)
        self.memory[a] = b
        return address + 3

    def op_call(self, address):
        to = self.getmem(address + 1)
        try: self.calls[to] += 1
        except: self.calls[to] = 1

        self.stack.append(address + 2)
        return to

    def op_ret(self, address):
        if not self.stack:
            return 0
        return self.stack.pop()

    def op_out(self, address):
        a = self.getmem(address + 1)
        print(chr(a), end='')
        return address + 2

    def op_in(self, address):
        while not self.input:
            s = input()

            if s == '.debug':
                self.debug_enabled = True
            elif s == '.calls':
                print(self.calls)
            elif s == '.interdimensional':
                self.registers[0x8007] = int(self.interdimensional)
            else:
                self.input = s + '\n'

        s = self.input[0]
        self.setmem(address + 1, ord(s))
        self.input = self.input[1:]
        return address + 2

    def op_noop(self, address):
        return address + 1

if __name__ == '__main__':
    program = sys.argv[1]

    vm = SynacorVM()
    vm.interdimensional = 1 if len(sys.argv) == 2 else sys.argv[2]
    vm.load(program)
    vm.run()
