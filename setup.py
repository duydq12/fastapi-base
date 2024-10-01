import os

from Cython.Build import cythonize
from setuptools import Extension, setup

ext_modules = []

for root, dirs, files in os.walk("src/fastapi_base"):
    for file in files:
        if file.endswith(".py"):
            module_path = os.path.join(root, file)
            module_name = module_path.replace("/", ".")[:-3]
            ext_modules.append(Extension(module_name, [module_path]))

setup(
    name="fastapi_base",
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={
            "language_level": "3",
            "embedsignature": True,
            "binding": True,
        },
    ),
    packages=[
        "fastapi_base",
    ],
    package_data={"fastapi_base": ["*.pxd", "*.pyi", "*.so"]},
    zip_safe=False,
)
