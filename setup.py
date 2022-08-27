import glob

import setuptools

try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='fastapi_base',
    version='0.0.1',
    author='duydq',
    author_email='duydq@rabiloo.com',
    description='Base Package for FastApi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/rabiloo/fastapi_base',
    project_urls={
        "Bug Tracker": "https://github.com/rabiloo/fastapi_base/issues"
    },
    license='MIT',
    packages=[
        "rbl_fastapi_base",
        "rbl_fastapi_base.auth",
        "rbl_fastapi_base.base",
        "rbl_fastapi_base.config",
        "rbl_fastapi_base.middleware",
    ],

    install_requires=[str(ir.requirement) for ir in parse_requirements('requirements.txt', session=PipSession())],
)
