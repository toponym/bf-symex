import sys

class Interpreter:
    def __init__(self, instrs: list):
        self.instrs = instrs
        self.memory = []
        self.mem_ptr = 0
        self.pc = 0
        self.pc_stack = []

    def memory_guard(self):
        """Ensure memory pointer is nonnegative and accessing a memory cell that exists"""
        if self.mem_ptr < 0:
            raise Exception(f"Negative memory pointer: {self.mem_ptr}")
        if self.mem_ptr >= len(self.memory):
            cells_to_add = self.mem_ptr-len(self.memory)+1
            self.memory.extend([0]*cells_to_add)

    def __repr__(self):
        return f"PC: {self.pc}\nPC Stack:{self.pc_stack}\nMemory Ptr: {self.mem_ptr}\nMemory: {self.memory}\n"

    def eval(self) -> None:
        """Evaluate instructions"""
        while self.pc < len(self.instrs):
            curr_instr = self.instrs[self.pc]
            match curr_instr:
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
                    self.memory[self.mem_ptr] -= -1
                    self.pc += 1
                case "[":
                    self.pc_stack.append(self.pc)
                    self.pc += 1
                case "]":
                    if len(self.pc_stack) == 0:
                        raise Exception(f"Empty stack for jump")
                    self.pc = self.pc_stack.pop()
                case ",":
                    self.memory_guard()
                    char = sys.stdin.read(1)
                    val = ord(char) - 48
                    self.memory[self.mem_ptr] = val
                    self.pc += 1
                case ".":
                    self.memory_guard()
                    val = self.memory[self.mem_ptr]
                    char = chr(val)
                    sys.stdout.write(char)
                    self.pc += 1
                case _:
                    print(f"[DEBUG] Ignoring character: {curr_instr}")