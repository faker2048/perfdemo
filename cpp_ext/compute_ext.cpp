#include <pybind11/pybind11.h>
#include <omp.h>
#include <cstdint>

namespace py = pybind11;

// 单线程版本
double heavy_compute_cpp(int64_t n) {
    constexpr double s2 = 1e-6; // (0.001)^2
    double sum = 0.0;
    for (int64_t i = 0; i < n; ++i) {
        double di = static_cast<double>(i);
        sum += di * di;
    }
    return s2 * sum;
}

// OpenMP 并行（只用 parallel for + reduction）
double heavy_compute_cpp_parallel(int64_t n, int num_threads = 0) {
    if (num_threads > 0) omp_set_num_threads(num_threads);

    constexpr double s2 = 1e-6;
    double sum = 0.0;

    #pragma omp parallel for reduction(+:sum) schedule(static)
    for (int64_t i = 0; i < n; ++i) {
        double di = static_cast<double>(i);
        sum += di * di;
    }
    return s2 * sum;
}

PYBIND11_MODULE(compute_ext, m) {
    m.doc() = "C++ 计算密集型任务模块（pybind11 + OpenMP）";
    m.def("heavy_compute_cpp", &heavy_compute_cpp, "单线程重计算任务", py::arg("n"));
    m.def("heavy_compute_cpp_parallel", &heavy_compute_cpp_parallel,
          "OpenMP 并行重计算任务", py::arg("n"), py::arg("num_threads") = 0);
}
