with open("/tmp/debug_script.js") as f:
    text = f.read()

in_str = None
in_comment = False
in_block_comment = False
escape = False
brace_stack = []

lines = text.splitlines()
for line_no, line in enumerate(lines, 1):
    i = 0
    while i < len(line):
        ch = line[i]
        if in_comment:
            break
        if in_block_comment:
            if ch == "*" and i + 1 < len(line) and line[i+1] == "/":
                in_block_comment = False
                i += 1
            i += 1
            continue
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue
        # Not in string or comment
        if ch == "/" and i + 1 < len(line) and line[i+1] == "/":
            in_comment = True
            break
        elif ch == "/" and i + 1 < len(line) and line[i+1] == "*":
            in_block_comment = True
            i += 1
        elif ch in ('"', "'", '`'):
            in_str = ch
        elif ch == "{":
            brace_stack.append((line_no, line.strip()))
        elif ch == "}":
            if brace_stack:
                brace_stack.pop()
            else:
                print(f"Extra closing brace at line {line_no}: {line.strip()}")
        i += 1
    in_comment = False

print(f"Total unclosed braces: {len(brace_stack)}")
for lno, ltext in brace_stack[-10:]:
    print(f"  Unclosed brace from line {lno}: {ltext}")
