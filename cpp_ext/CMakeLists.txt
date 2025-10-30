cmake_minimum_required(VERSION 3.15)
project(compute_ext)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 Python 和 pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# 查找 OpenMP
find_package(OpenMP REQUIRED)

# 创建 pybind11 模块
pybind11_add_module(compute_ext compute_ext.cpp)

# 链接 OpenMP
target_link_libraries(compute_ext PRIVATE OpenMP::OpenMP_CXX)

# 优化选项
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(compute_ext PRIVATE -O3 -march=native -ffast-math)
elseif(MSVC)
    target_compile_options(compute_ext PRIVATE /O2 /GL /fp:fast /arch:AVX2)
endif()

# 安装到项目根目录（与 Python 包同级）
install(TARGETS compute_ext LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/..)
