import glob
import io
import os
import shutil
import sys

import isort

from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

"""
Find script to compile package and Run
eval `python -c 'import fastapi_base as _;print(f"compile_path={_.__path__[0]}/compile_package.py")'`
python $compile_path build_ext --inplace --package app/src/core
"""


def read_file(filename: str, mode: str = "r", encoding: str = "utf-8"):
    with io.open(filename, mode, encoding=encoding) as file:
        text: str = file.read()
    return text


def write_file(filename: str, text: str, mode: str = "w", encoding: str = "utf-8") -> None:
    with io.open(filename, mode, encoding=encoding) as file:
        file.write(text)


def scan_dir(dirname, suffix=".py"):
    """
    Returns all the files inside a directory
    """
    files_list = glob.glob(f"{dirname}/**/*{suffix}", recursive=True)
    files_list = sorted(files_list, key=lambda p: os.path.basename(p), reverse=True)
    return files_list


def combine_files(package):
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


def compile_code(package):
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


def clean_build(package):
    os.remove(f"{package}.py")
    shutil.rmtree("build")
    shutil.rmtree("build_cythonize")


def get_args():
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
