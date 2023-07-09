"""Interpreter Class"""
import sys
import copy
from .byte import ConcreteByte, SymbolicByte
from .symbolic_memory import SymbolicMemory
from z3 import BitVecNumRef, BitVecVal, BitVec, BoolVal, And

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
        self.input_byte_counter = 0
        self.done = False
        self.successors = []
        self.path_constraint = BoolVal(True)

    def __repr__(self):
        string = f"PC: {self.pc}\n" \
                    f"PC Stack:{self.pc_stack}\n" \
                    f"Memory Ptr: {self.mem_ptr}\n" \
                    f"Memory: {self.memory}\n"
        return string

    def run(self) -> list:
        """Execute insructions until done or successors generated"""
        while len(self.successors) == 0 and not self.done:
            if self.pc >= len(self.instrs):
                self.done = True
            else:
                instr = self.fetch()
                self.execute(instr)
        return self.successors
        

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
                self.start_loop()
            case "]":
                self.end_loop()
            case ",":
                self.read()
            case ".":
                self.write()
            case _:
                self.nop()

    def inc_mem_ptr(self):
        """Implement '<': increment memory pointer"""
        self.mem_ptr += 1
        self.pc += 1

    def dec_mem_ptr(self):
        """Implement '>': decrement memory pointer"""
        self.mem_ptr -= 1
        self.pc += 1

    def inc_mem(self):
        """Implement '+': incremenet memory at memory pointer"""
        byte = self.memory.get(self.mem_ptr)
        self.memory.set(self.mem_ptr, byte + 1)
        self.pc += 1

    def dec_mem(self):
        """Implement '-': decrement memory at memory pointer"""
        byte = self.memory.get(self.mem_ptr)
        self.memory.set(self.mem_ptr, byte - 1)
        self.pc += 1

    def skip_loop(self):
        """Skip instructions until after loop"""
        loop_count = 1
        self.pc += 1
        while loop_count != 0:
            loop_instr = self.fetch()
            if loop_instr == "]":
                loop_count -= 1
            if loop_instr == "[":
                loop_count += 1
            self.pc += 1
    
    def enter_loop(self):
        """Enter loop by updating PC stack and PC"""
        self.pc_stack.append(self.pc)
        self.pc += 1

    def repeat_loop(self):
        """Repeat loop by going to first instruction inside it"""
        self.pc = self.pc_stack[-1] + 1
    
    def exit_loop(self):
        """Exit loop by simply incrementing PC"""
        self.pc += 1

    def start_loop(self):
        """Implement '[': start of loop
        
        Enter loop if memory pointed to is nonzero, otherwise skip
        """
        mem_byte = self.memory.get(self.mem_ptr)
        if not isinstance(mem_byte, BitVecNumRef):
            # set up successors if branching on symbolic condition
            # TODO handle constraint being set from symbolic to constant
            succ0 = copy.deepcopy(self)
            constraint = succ0.path_constraint
            succ0.path_constraint = And(constraint, mem_byte == 0)
            succ0.skip_loop()
            succ1 = copy.deepcopy(self)
            constraint = succ1.path_constraint
            succ1.path_constraint = And(constraint, mem_byte != 0)
            succ1.enter_loop()
            self.successors = [succ0, succ1]
        else:
            mem_byte_num = mem_byte.as_long()
            if mem_byte_num != 0:
                self.enter_loop()
            else:
                self.skip_loop()

    def end_loop(self):
        """Implement ']': end of loop
        
        Repeat loop if current memory cell is non-zero
        """
        if len(self.pc_stack) == 0:
            raise StackError("Empty stack for jump")
        mem_byte = self.memory.get(self.mem_ptr)
        if not isinstance(mem_byte, BitVecNumRef):
            succ0 = copy.deepcopy(self)
            constraint = succ0.path_constraint
            succ0.path_constraint = And(constraint, mem_byte == 0)
            succ0.exit_loop()
            succ1 = copy.deepcopy(self)
            constraint = succ1.path_constraint
            succ1.path_constraint = And(constraint, mem_byte != 0)
            succ1.repeat_loop()
            self.successors = [succ0, succ1]
        else:
            mem_byte_num = mem_byte.as_long()
            # exit loop if current memory cell is zero
            if mem_byte_num == 0:
                self.exit_loop()
            else:
                self.repeat_loop()

    def read(self):
        """Implement ',': read one (ASCII) character"""
        # TODO actually read input
        var_name = f"input_{self.input_byte_counter}"
        input_byte = BitVec(var_name, SymbolicByte.BYTE_SIZE)
        self.memory.set(self.mem_ptr, input_byte)
        self.pc += 1

    def write(self):
        """Implement '.': print one (ASCII) character"""
        val = self.memory.get(self.mem_ptr).as_long()
        char = chr(val)
        sys.stdout.write(char)
        self.pc += 1
    
    def nop(self):
        """Implement NOP, used for characters that aren't valid instructions"""
        self.pc += 1