"""Setup script for C++ extension module"""

import platform

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# 编译选项
extra_compile_args = []
extra_link_args = []

if platform.system() == "Windows":
    extra_compile_args = [
        "/O2",
        "/GL",
        "/fp:fast",
        "/arch:AVX2",
        "/openmp:llvm",
        "/std:c++17",
        "/Ob3",
        "/Oi",
        "/Ot",
    ]
    extra_link_args = ["/LTCG"]
elif platform.system() == "Darwin":
    extra_compile_args = [
        "-O3",
        "-Xpreprocessor",
        "-fopenmp",
        "-ffast-math",
        "-march=native",
    ]
    extra_link_args = ["-lomp"]
else:
    extra_compile_args = ["-O3", "-fopenmp", "-ffast-math", "-march=native"]
    extra_link_args = ["-fopenmp", "-static-libstdc++", "-static-libgcc"]

ext_modules = [
    Pybind11Extension(
        "compute_ext",
        ["cpp_ext/compute_ext.cpp"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=20,
    ),
]

setup(
    name="compute_ext",
    version="0.1.0",
    description="C++ 计算扩展模块 (pybind11 + OpenMP)",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.10",
)
