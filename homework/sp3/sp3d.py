import sys, struct

(PUSH, POP, ADD, SUB, MUL, DIV, EQ, NE,
 LT, GT, LE, GE, JMP, JZ, CALL, RET,
 SET, GET, PRINT, HALT, NOT,
 ARRAY, IDX_GET, IDX_SET, READ, BREAK, CONTINUE) = range(27)

op_names = [
    "PUSH", "POP", "ADD", "SUB", "MUL", "DIV", "EQ", "NE",
    "LT", "GT", "LE", "GE", "JMP", "JZ", "CALL", "RET",
    "SET", "GET", "PRINT", "HALT", "NOT",
    "ARRAY", "IDX_GET", "IDX_SET", "READ", "BREAK", "CONTINUE",
]

def has_arg(op):
    return op in (PUSH, JMP, JZ, CALL, SET, GET, ARRAY, IDX_GET, IDX_SET, READ, BREAK, CONTINUE)

def disassemble(in_path, out_path):
    with open(in_path, 'rb') as f:
        data = f.read()

    pos = 0
    instructions = []
    idx = 0
    while pos < len(data):
        op = data[pos]
        pos += 1
        if op >= len(op_names):
            print(f"Warning: unknown opcode {op} at byte {pos-1}")
            break
        if has_arg(op):
            if pos + 4 > len(data):
                break
            arg = struct.unpack('i', data[pos:pos+4])[0]
            pos += 4
        else:
            arg = None
        instructions.append((op, arg))
        idx += 1

    with open(out_path, 'w') as f:
        for i, (op, arg) in enumerate(instructions):
            op_name = op_names[op]
            line = f"{op_name}"
            if arg is not None:
                line += f" {arg}"
            f.write(line + '\n')

    print(f"Disassembled {len(instructions)} instructions -> {out_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python sp3d.py <input.bc> <output.txt>")
        sys.exit(1)
    disassemble(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
