# perfdemo - 高性能并发与并行计算演示

一个展示 Python 高性能并发和并行计算的完整项目，包含 5 个不同的性能优化方案。

## ✨ 特性

- **Demo 1**: 高并发 I/O 任务（asyncio + 信号量）
- **Demo 2**: 速率限制器（Token Bucket 算法）
- **Demo 3**: 多进程并行计算（ProcessPoolExecutor）
- **Demo 4**: Numba JIT 并行加速
- **Demo 5**: C++ OpenMP 并行（可选）

## 🚀 快速开始

### 方式 1: 使用 uvx（推荐，一键运行）

```bash
# 安装 uv（如果还没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 一键运行项目（自动处理依赖）
uvx --from . perfdemo

# 或者从当前目录运行
uv run perfdemo
```

### 方式 2: 使用 pip

```bash
# 安装依赖
pip install numba

# 运行
python main.py
```

### 方式 3: 传统方式

```bash
# 作为模块运行
python -m perfdemo

# 或者先安装
pip install -e .
perfdemo
```

## 📦 项目结构

```
perfdemo/
├── perfdemo/                    # Python 包
│   ├── __init__.py           # 包初始化
│   ├── __main__.py           # 命令行入口
│   ├── demos.py              # 所有演示函数
│   ├── async_utils.py        # 异步工具（retry、bounded_map）
│   ├── rate_limiter.py       # Token Bucket 速率限制器
│   └── tasks.py              # 模拟任务函数
├── cpp_ext/                   # C++ 扩展（可选）
│   ├── compute_ext.cpp       # C++ 源代码
│   └── CMakeLists.txt        # CMake 配置
├── pyproject.toml             # 项目配置（PEP 621）
├── setup.py                   # C++ 扩展编译配置
├── README.md                  # 本文件
└── BUILD.md                   # 构建和编译说明
```

## 🔧 安装 C++ 扩展（可选，获得最佳性能）

如果想运行 Demo 5（C++ OpenMP），需要先编译 C++ 扩展：

```bash
# 1. 安装编译依赖
pip install pybind11

# 2. 编译扩展
python setup.py build_ext --inplace

# 3. 运行（包含 demo5）
python main.py
```

详细编译说明请查看 [BUILD.md](BUILD.md)。

## 📊 性能对比

在 8 核 CPU 上，4 亿次迭代的性能对比：

| Demo | 方案 | 预期耗时 | 吞吐量 |
|------|------|---------|--------|
| Demo 3 | Python 进程池 | ~2-3s | ~150 M it/s |
| Demo 4 | Numba JIT 并行 | ~0.5-1s | ~500 M it/s |
| Demo 5 | C++ OpenMP | ~0.3-0.6s | ~700 M it/s ⚡ |

## 🎯 使用场景

### 异步 I/O 密集型（Demo 1）
- Web API 批量请求
- 数据库批量查询
- 文件批量处理

### 速率限制（Demo 2）
- API 调用限流
- 订单提交控制
- 爬虫速率控制

### CPU 密集型计算（Demo 3-5）
- 数据分析和科学计算
- 机器学习模型训练
- 图像/视频处理
- 加密解密操作

## 📝 依赖项

### 核心依赖（必需）
- Python >= 3.10
- numba >= 0.59.0

### 可选依赖
- pybind11 >= 2.10.0（C++ 扩展）
- 编译器（GCC/Clang/MSVC，用于 C++ 扩展）

## 🛠️ 开发

```bash
# 克隆项目
git clone <your-repo-url>
cd perfdemo

# 使用 uv 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 运行（多种方式）
python -m perfdemo      # 作为模块运行
perfdemo                # 命令行运行
uv run perfdemo         # 使用 uv 运行
```

## 📖 技术栈

- **异步编程**: asyncio, TaskGroup, Semaphore
- **并发控制**: Token Bucket 限流算法
- **并行计算**: ProcessPoolExecutor, Numba, OpenMP
- **性能优化**: JIT 编译, SIMD, 多线程/多进程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关资源

- [Numba 文档](https://numba.pydata.org/)
- [pybind11 文档](https://pybind11.readthedocs.io/)
- [OpenMP 文档](https://www.openmp.org/)
- [uv 文档](https://docs.astral.sh/uv/)
