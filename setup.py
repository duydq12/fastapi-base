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
    ext_modules=cythonize(ext_modules),
    packages=[
        "fastapi_base",
        "fastapi_base.authen",
        "fastapi_base.connection",
        "fastapi_base.crud",
        "fastapi_base.logger",
        "fastapi_base.middleware",
        "fastapi_base.pattern",
    ],
)
