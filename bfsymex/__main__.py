import argparse
from bfsymex import Interpreter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'bfsymex',
        description = "Brainfuck Symbolic Execution",
    )
    parser.add_argument("task",
                        choices = ['interpret'],
                        help = 'task for bfsymex')
    parser.add_argument("-f", "--file",
                        help = 'file with program',
                        required = False)
    args = parser.parse_args()
    match args.task:
        case "interpret":
            code = ""
            if args.file:
                with open(args.file, 'r') as f:
                    code = f.read()
            else:
                code = input("Enter program\n")
            interp = Interpreter(list(code))
            interp.eval()
            print("***Final State***")
            print(repr(interp))
        case _:
            print("Case not supported yet: {args.task}")
            
            