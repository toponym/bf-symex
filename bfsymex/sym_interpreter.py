"""Interpreter Class"""
import sys
from .byte import ConcreteByte, SymbolicByte
from .symbolic_memory import SymbolicMemory
from z3 import BitVecNumRef, BitVecVal

class StackError(Exception):
    """Interpreter Stack Errors"""

class UnexpectedSymbolicError(Exception):
    """Interpreter Error when Value should be Concrete """

#TODO abstract z3 objects away?
class SymbolicInterpreter:
    """Symbolic Brainfuck Interpreter"""

    MEM_SIZE = 30000

    def __init__(self, instrs: list):
        self.instrs = instrs
        self.memory: SymbolicMemory = SymbolicMemory(SymbolicInterpreter.MEM_SIZE)
        self.mem_ptr = 0
        self.pc = 0
        self.pc_stack = []

    def __repr__(self):
        string = f"PC: {self.pc}\n" \
                    f"PC Stack:{self.pc_stack}\n" \
                    f"Memory Ptr: {self.mem_ptr}\n" \
                    f"Memory: {self.memory}\n"
        return string

    def interpret(self) -> None:
        """Interpret instructions"""
        while True:
            if self.pc >= len(self.instrs):
                break
            instr = self.fetch()
            # no decoding necessary!
            self.execute(instr)

    def fetch(self) -> str:
        """Get next instruction"""
        return self.instrs[self.pc]

    def execute(self, instr: str):
        """Execute instruction"""
        match instr:
            case ">":
                self.inc_mem_ptr()
            case "<":
                self.dec_mem_ptr()
            case "+":
                self.inc_mem()
            case "-":
                self.dec_mem()
            case "[":
                self.enter_loop()
            case "]":
                self.exit_loop()
            case ",":
                self.read()
            case ".":
                self.write()
            case _:
                self.nop()

    def inc_mem_ptr(self):
        self.mem_ptr += 1
        self.pc += 1

    def dec_mem_ptr(self):
        self.mem_ptr -= 1
        self.pc += 1

    def inc_mem(self):
        byte = self.memory.get(self.mem_ptr)
        self.memory.set(self.mem_ptr, byte + 1)
        self.pc += 1

    def dec_mem(self):
        byte = self.memory.get(self.mem_ptr)
        self.memory.set(self.mem_ptr, byte - 1)
        self.pc += 1

    def enter_loop(self):
        # enter loop if current memory nonzero, otherwise skip
        # TODO add branching
        mem_byte = self.memory.get(self.mem_ptr)
        if not isinstance(mem_byte, BitVecNumRef):
            # can't handle branching from Symbolic bytes yet
            raise NotImplementedError("Have not implemented branching")
        mem_byte_num = mem_byte.as_long()
        #print(f"[DEBUG] Branch pc: {self.pc} byte val: {mem_byte_num}")
        if mem_byte_num != 0:
            self.pc_stack.append(self.pc)
            self.pc += 1
        else:
            loop_count = 1
            self.pc += 1
            while loop_count != 0:
                loop_instr = self.fetch()
                if loop_instr == "]":
                    loop_count -= 1
                if loop_instr == "[":
                    loop_count += 1
                self.pc += 1

    def exit_loop(self):
        # TODO add branching
        if len(self.pc_stack) == 0:
            raise StackError("Empty stack for jump")
        mem_byte = self.memory.get(self.mem_ptr)
        if not isinstance(mem_byte, BitVecNumRef):
            # can't handle branching from Symbolic bytes yet
            raise NotImplementedError
        mem_byte_num = mem_byte.as_long()
        # exit loop if current memory cell is zero
        if mem_byte_num == 0:
            self.pc_stack.pop()
            self.pc += 1
        else:
            self.pc = self.pc_stack[-1] + 1

    def read(self):
        # TODO actually read input
        # assumes ascii encoding
        #char = sys.stdin.read(1)
        #if char == "\n":
        #    char = "\0"
        char = "\0"
        val = ord(char)
        byte = BitVecVal(val, 8)
        self.memory.set(self.mem_ptr, byte)
        self.pc += 1

    def write(self):
        #TODO Handle SymbolicByte
        val = self.memory.get(self.mem_ptr).as_long()
        char = chr(val)
        sys.stdout.write(char)
        self.pc += 1
    
    def nop(self):
        self.pc += 1