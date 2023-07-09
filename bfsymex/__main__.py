"""CLI for bfsymex"""
import argparse
from bfsymex import Interpreter, SymEngine

def get_code(file_path: str):
    """Read code from file or stdin"""
    if file_path:
        with open(file_path, 'r', encoding='ascii') as file:
            return file.read()
    else:
        return input("Enter program\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'bfsymex',
        description = "Brainfuck Symbolic Execution",
    )
    parser.add_argument("task",
                        choices = ['interpret', 'symex'],
                        help = 'task for bfsymex')
    parser.add_argument("-f", "--file",
                        help = 'file with program',
                        required = False)
    args = parser.parse_args()
    code = get_code(args.file)
    match args.task:
        case "interpret":
            interp = Interpreter(list(code))
            interp.interpret()
        case "symex":
            symex = SymEngine(list(code))
            symex.run()
        case _:
            print("Case not supported yet: {args.task}")
