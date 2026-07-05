from setuptools import setup, find_packages

setup(
    name='memory-hygiene',
    version='0.1.0',
    description='AI Memory Hygiene — 上下文预算分析CLI工具',
    author='wanghui316',
    packages=find_packages(),
    py_modules=['mh_core'],
    scripts=['bin/mh.py'],
    python_requires='>=3.6',
)
