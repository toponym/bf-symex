"""Engine for running symbolic execution interpreters"""
from .sym_interpreter import SymbolicInterpreter

class SymEngine:
    def __init__(self, code):
        self.running = []
        self.done = []
        self.code = list(code)
    
    def run(self):
        """Run symex insances round-robin"""
        symex = SymbolicInterpreter(self.code)
        self.running.append(symex)
        print("[LOG] Starting up SymEngine")
        while self.running:
            symex = self.running.pop()
            states = symex.run()
            for state in states:
                if state.done:
                    print("[LOG] Adding state to done")
                    self.done.append(state)
                else:
                    print("[LOG] Adding state to running")
                    self.running.append(state)
