from z3 import BitVec, BitVecVal, BitVecRef, simplify

class MemoryAccessError(Exception):
    """Interpreter Memory Access Errors"""

class SymbolicMemory():
    BYTE_SIZE = 8

    def __init__(self, size, ctx='memory'):
        self.ctx = ctx
        # note: BitVecVal() constructs a BitVecNumRef object
        self.memory = [BitVecVal(0, SymbolicMemory.BYTE_SIZE) for i in range(size)]

    def memory_guard(self, index):
        """Ensure memory pointer is nonnegative and accessing a memory cell that exists"""
        if index < 0 or index >= len(self.memory):
            raise MemoryAccessError(f"Out-of-bounds memory access: {index}")

    def get(self, index) -> BitVecRef:
        self.memory_guard(index)
        return self.memory[index]
    
    def set(self, index, byte) -> None:
        self.memory_guard(index)
        self.memory[index]= simplify(byte)
    