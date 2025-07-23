import dis
import types
import sys
from pathlib import Path
import dis
import marshal
import numpy as np
import types


INPUT_PATH = Path("py_file.pyc")

# Patch the bytecode of a single code object
def patch_bytecode(co):
    patched = bytearray()
    i = 0
    code = co.co_code
    while i < len(code):
        op = code[i]
        patched.append(op)
        i += 1

        if op >= dis.HAVE_ARGUMENT:
            arg = code[i] + (code[i+1] << 8)
            # Patch BINARY_ADD to BINARY_SUBTRACT
            if op == dis.opmap["BINARY_ADD"]:
                patched[-1] = dis.opmap["BINARY_SUBTRACT"]
            patched.append(arg & 0xFF)
            patched.append((arg >> 8) & 0xFF)
            i += 2
    return bytes(patched)

# Recursively patch code objects
def patch_code_obj(co):
    # Recursively patch any inner code objects in co_consts
    new_consts = []
    for const in co.co_consts:
        if isinstance(const, types.CodeType):
            new_consts.append(patch_code_obj(const))
        else:
            new_consts.append(const)

    # Patch this object's bytecode
    new_bytecode = patch_bytecode(co)

    new_code = types.CodeType(
        co.co_argcount,
        co.co_posonlyargcount,
        co.co_kwonlyargcount,
        co.co_nlocals,
        co.co_stacksize,
        co.co_flags,
        new_bytecode,
        tuple(new_consts),
        co.co_names,
        co.co_varnames,
        co.co_filename,
        co.co_name,
        co.co_firstlineno,
        co.co_lnotab,
        co.co_freevars,
        co.co_cellvars
    )
    return new_code


if __name__ == "__main__":
    with INPUT_PATH.open("rb") as f:

        content = f.read(16)
        code_obj = marshal.load(f)
    file_inside = dis.dis(code_obj)
    patched_code = patch_code_obj(code_obj)

    with open("py_file.pyc", "wb") as f:
        f.write(content)                 
        marshal.dump(patched_code, f)
