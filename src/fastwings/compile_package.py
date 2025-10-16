"""Compile and build package utilities for fastwings.

Provides functions to combine, compile, and clean Python packages using Cython.

Functions:
    read_file: Reads the contents of a file.
    write_file: Writes text to a file.
    scan_dir: Returns all files inside a directory with a given suffix.
    combine_files: Combines Python files in a package into a single file.
    compile_code: Compiles the combined file using Cython.
    clean_build: Cleans up build artifacts after compilation.
    get_args: Parses command-line arguments for package compilation.
"""

import glob
import os
import shutil
import sys

import isort
from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

"""
Find script to compile package and Run
    eval `python -c 'import fastwings as _;print(f"compile_path={_.__path__[0]}/compile_package.py")'`
    python $compile_path build_ext --inplace --package app/src/core
"""

def read_file(filename: str, mode: str = "r", encoding: str = "utf-8") -> str:
    """Reads the contents of a file.

    Args:
        filename: Path to the file.
        mode: File open mode.
        encoding: File encoding.

    Returns:
        str: Contents of the file.
    """
    with open(filename, mode, encoding=encoding) as file:
        text: str = file.read()
    return text


def write_file(filename: str, text: str, mode: str = "w", encoding: str = "utf-8") -> None:
    """Writes text to a file.

    Args:
        filename: Path to the file.
        text: Text to write.
        mode: File open mode.
        encoding: File encoding.
    """
    with open(filename, mode, encoding=encoding) as file:
        file.write(text)


def scan_dir(dirname: str, suffix: str = ".py") -> list[str]:
    """Returns all the files inside a directory with a given suffix.

    Args:
        dirname: Directory path.
        suffix: File suffix to filter.

    Returns:
        list[str]: List of file paths.
    """
    files_list = glob.glob(f"{dirname}/**/*{suffix}", recursive=True)
    files_list = sorted(files_list, key=lambda p: os.path.basename(p), reverse=True)
    return files_list


def combine_files(package: str) -> None:
    """Combines Python files in a package into a single file for compilation.

    Args:
        package: Package directory path.
    """
    files_list = scan_dir(package)
    package_content = []
    package_import = set()
    for file_path in files_list:
        if file_path == f"{package}/__init__.py":
            continue
        lines_content = read_file(file_path).strip().split("\n")
        for line_content in lines_content:
            if line_content.startswith("from") or line_content.startswith("import"):
                if line_content.find(f".{os.path.basename(package)}.") < 0:
                    package_import.add(line_content)
                continue

            if not line_content:
                continue

            if line_content.strip() == 'if __name__ == "__main__":':
                break

            package_content.append(line_content)

    content = "\n".join(package_import) + "\n\n" + "\n".join(package_content)
    content = isort.code(content)
    write_file(f"{package}.py", content)


def compile_code(package: str) -> None:
    """Compiles the combined Python file using Cython.

    Args:
        package: Package directory path.
    """
    setup(
        ext_modules=cythonize(
            [
                Extension(package.replace("/", "."), [f"{package}.py"]),
            ],
            build_dir="build_cythonize",
            compiler_directives={
                "language_level": "3",
                "always_allow_keywords": True,
            },
        ),
    )


def clean_build(package: str) -> None:
    """Cleans up build artifacts after compilation.

    Args:
        package: Package directory path.
    """
    os.remove(f"{package}.py")
    shutil.rmtree("build")
    shutil.rmtree("build_cythonize")


def get_args() -> str:
    """Parses command-line arguments for package compilation.

    Returns:
        str: Package directory path.
    """
    # Compile project using Cython
    if "--package" not in sys.argv:  # package path
        sys.exit("Compile Error: Required --package argument")

    index = sys.argv.index("--package")
    sys.argv.pop(index)  # Removes the '--package'
    package = sys.argv.pop(index)  # Returns the element after the '--package'

    return package


if __name__ == "__main__":
    package_ = get_args()
    combine_files(package_)
    compile_code(package_)
    clean_build(package_)
