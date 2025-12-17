/**
 * @file benchmark.cpp
 * @brief Benchmarking utility implementation
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#include "benchmark.hpp"
#include <fstream>
#include <sstream>
#include <cstring>
#include <omp.h>

#ifdef __linux__
#include <unistd.h>
#endif

namespace benchmark {

void print_system_info(std::ostream& os) {
    os << "\n";
    os << "================================================================================\n";
    os << "                           SYSTEM INFORMATION\n";
    os << "================================================================================\n";

    // OpenMP info
    os << "OpenMP:\n";
    os << "  - Version: " << _OPENMP << "\n";
    os << "  - Max threads: " << omp_get_max_threads() << "\n";
    os << "  - Num processors: " << omp_get_num_procs() << "\n";
    os << "  - Dynamic threads: " << (omp_get_dynamic() ? "enabled" : "disabled") << "\n";
    os << "  - Nested parallelism: " << (omp_get_nested() ? "enabled" : "disabled") << "\n";

#ifdef __linux__
    // Try to get CPU info from /proc/cpuinfo
    std::ifstream cpuinfo("/proc/cpuinfo");
    if (cpuinfo) {
        std::string line;
        std::string model_name;
        std::string cpu_mhz;
        std::string cache_size;
        int cpu_count = 0;

        while (std::getline(cpuinfo, line)) {
            if (line.find("model name") != std::string::npos && model_name.empty()) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    model_name = line.substr(pos + 2);
                }
            }
            if (line.find("cpu MHz") != std::string::npos && cpu_mhz.empty()) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    cpu_mhz = line.substr(pos + 2);
                }
            }
            if (line.find("cache size") != std::string::npos && cache_size.empty()) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    cache_size = line.substr(pos + 2);
                }
            }
            if (line.find("processor") != std::string::npos) {
                cpu_count++;
            }
        }

        os << "\nCPU:\n";
        if (!model_name.empty()) os << "  - Model: " << model_name << "\n";
        os << "  - Logical cores: " << cpu_count << "\n";
        if (!cpu_mhz.empty()) os << "  - Frequency: " << cpu_mhz << " MHz\n";
        if (!cache_size.empty()) os << "  - L3 Cache: " << cache_size << "\n";
    }

    // Memory info
    std::ifstream meminfo("/proc/meminfo");
    if (meminfo) {
        std::string line;
        os << "\nMemory:\n";
        int lines_read = 0;
        while (std::getline(meminfo, line) && lines_read < 3) {
            os << "  - " << line << "\n";
            lines_read++;
        }
    }
#endif

    // Compiler info
    os << "\nCompiler:\n";
#ifdef __GNUC__
    os << "  - GCC " << __GNUC__ << "." << __GNUC_MINOR__ << "." << __GNUC_PATCHLEVEL__ << "\n";
#endif
#ifdef __clang__
    os << "  - Clang " << __clang_major__ << "." << __clang_minor__ << "." << __clang_patchlevel__ << "\n";
#endif

    // Build configuration
    os << "\nBuild:\n";
#ifdef NDEBUG
    os << "  - Mode: Release\n";
#else
    os << "  - Mode: Debug\n";
#endif
#ifdef __OPTIMIZE__
    os << "  - Optimization: Enabled\n";
#endif

    os << "================================================================================\n\n";
}

} // namespace benchmark
