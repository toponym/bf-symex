"""Interpreter Class"""
import sys

class MemoryAccessError(Exception):
    """Interpreter Memory Access Errors"""

class StackError(Exception):
    """Interpreter Stack Errors"""

class Interpreter:
    """Brainfuck Interpreter"""
    def __init__(self, instrs: list):
        self.instrs = instrs
        self.memory = []
        self.mem_ptr = 0
        self.pc = 0
        self.pc_stack = []

    def memory_guard(self):
        """Ensure memory pointer is nonnegative and accessing a memory cell that exists"""
        if self.mem_ptr < 0:
            raise MemoryAccessError(f"Negative memory pointer: {self.mem_ptr}")
        if self.mem_ptr >= len(self.memory):
            cells_to_add = self.mem_ptr-len(self.memory)+1
            self.memory.extend([0]*cells_to_add)

    def __repr__(self):
        string = f"PC: {self.pc}\n" \
                    f"PC Stack:{self.pc_stack}\n" \
                    f"Memory Ptr: {self.mem_ptr}\n" \
                    f"Memory: {self.memory}\n"
        return string

    def interpret(self) -> None:
        """Interpret instructions"""
        while self.pc < len(self.instrs):
            instr = self.fetch()
            self.memory_guard()
            # no decoding necessary!
            self.execute(instr)

    def fetch(self) -> str:
        """Get next instruction"""
        return self.instrs[self.pc]

    def execute(self, instr: str):
        """Execute instruction"""
        match instr:
            case ">":
                self.mem_ptr += 1
                self.pc += 1
            case "<":
                self.mem_ptr -= 1
                self.pc += 1
            case "+":
                self.memory_guard()
                self.memory[self.mem_ptr] += 1
                self.pc += 1
            case "-":
                self.memory_guard()
                self.memory[self.mem_ptr] -= 1
                self.pc += 1
            case "[":
                self.memory_guard()
                # enter loop if current memory nonzero, otherwise skip
                if self.memory[self.mem_ptr] != 0:
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


            case "]":
                if len(self.pc_stack) == 0:
                    raise StackError("Empty stack for jump")
                self.memory_guard()
                # exit loop if current memory cell is zero
                if self.memory[self.mem_ptr] == 0:
                    self.pc_stack.pop()
                    self.pc += 1
                else:
                    self.pc = self.pc_stack[-1] + 1
            case ",":
                self.memory_guard()
                # assumes ascii encoding
                char = sys.stdin.read(1)
                if char == "\n":
                    char = "\0"
                val = ord(char)
                self.memory[self.mem_ptr] = val
                self.pc += 1
            case ".":
                self.memory_guard()
                val = self.memory[self.mem_ptr]
                char = chr(val)
                sys.stdout.write(char)
                self.pc += 1
            case _:
                self.pc += 1
