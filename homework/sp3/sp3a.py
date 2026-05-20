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

name_to_op = {name: i for i, name in enumerate(op_names)}

def assemble(in_path, out_path):
    with open(in_path) as f:
        lines = f.readlines()

    instructions = []
    labels = {}
    pos = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith(':'):
            labels[line[:-1]] = pos
            continue
        parts = line.split(None, 1)
        op_name = parts[0]
        arg_str = parts[1].strip() if len(parts) > 1 else None
        if op_name not in name_to_op:
            raise Exception(f"Unknown opcode: {op_name}")
        op = name_to_op[op_name]
        arg = None
        if arg_str is not None:
            try:
                arg = int(arg_str)
            except ValueError:
                arg = arg_str
        instructions.append((op, arg, pos))
        pos += 1

    resolved = []
    for op, arg, p in instructions:
        if arg is not None and isinstance(arg, str) and arg in labels:
            resolved.append((op, labels[arg]))
        else:
            resolved.append((op, arg))

    with open(out_path, 'wb') as f:
        for op, arg in resolved:
            if arg is None:
                f.write(struct.pack('B', op))
            elif isinstance(arg, int):
                f.write(struct.pack('Bi', op, arg))
            elif isinstance(arg, str):
                encoded = arg.encode('utf-8')
                f.write(struct.pack('B', op))
                f.write(struct.pack('I', len(encoded)))
                f.write(encoded)
            else:
                f.write(struct.pack('B', op))

    print(f"Assembled {len(resolved)} instructions -> {out_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python sp3a.py <input.txt> <output.bc>")
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
