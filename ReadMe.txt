This script reads a `.pyc` file and replaces all `BINARY_ADD` (`+`) bytecode operations with `BINARY_SUBTRACT` (`-`), including inside nested functions.

How to Use

1. Make sure you have a `.pyc` file (e.g. from `python -m py_compile script.py`).
2. Set the input path in the script (`INPUT_PATH = Path("py_file.pyc")`).
3. Run the script:

   bash
   python patch_pyc.py