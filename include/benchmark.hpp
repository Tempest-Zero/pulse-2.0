/**
 * @file benchmark.hpp
 * @brief Benchmarking and timing utilities
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#ifndef BENCHMARK_HPP
#define BENCHMARK_HPP

#include <chrono>
#include <string>
#include <vector>
#include <functional>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <omp.h>

namespace benchmark {

/**
 * @brief High-resolution timer for benchmarking
 */
class Timer {
public:
    using Clock = std::chrono::high_resolution_clock;
    using TimePoint = Clock::time_point;
    using Duration = std::chrono::duration<double, std::milli>;

    Timer() : running_(false), elapsed_(0) {}

    void start() {
        start_time_ = Clock::now();
        running_ = true;
    }

    void stop() {
        if (running_) {
            end_time_ = Clock::now();
            elapsed_ += std::chrono::duration_cast<Duration>(end_time_ - start_time_).count();
            running_ = false;
        }
    }

    void reset() {
        running_ = false;
        elapsed_ = 0;
    }

    // Returns elapsed time in milliseconds
    double elapsed_ms() const {
        if (running_) {
            auto now = Clock::now();
            return elapsed_ + std::chrono::duration_cast<Duration>(now - start_time_).count();
        }
        return elapsed_;
    }

    // Returns elapsed time in seconds
    double elapsed_sec() const {
        return elapsed_ms() / 1000.0;
    }

private:
    TimePoint start_time_;
    TimePoint end_time_;
    bool running_;
    double elapsed_;  // Accumulated time in ms
};

/**
 * @brief Result of a single benchmark run
 */
struct BenchmarkResult {
    std::string name;
    std::string filter_name;
    int image_width;
    int image_height;
    int num_threads;
    std::string schedule;
    int chunk_size;
    double time_ms;           // Execution time in milliseconds
    double speedup;           // Relative to serial baseline
    double efficiency;        // Speedup / num_threads
    double throughput_mpps;   // Megapixels per second

    void print(std::ostream& os = std::cout) const {
        os << std::fixed << std::setprecision(3);
        os << "| " << std::setw(20) << name
           << " | " << std::setw(15) << filter_name
           << " | " << std::setw(5) << image_width << "x" << std::setw(5) << image_height
           << " | " << std::setw(3) << num_threads
           << " | " << std::setw(8) << schedule
           << " | " << std::setw(10) << time_ms << " ms"
           << " | " << std::setw(6) << speedup << "x"
           << " | " << std::setw(6) << (efficiency * 100) << "%"
           << " | " << std::setw(8) << throughput_mpps << " MP/s"
           << " |" << std::endl;
    }
};

/**
 * @brief Benchmark suite for collecting and analyzing results
 */
class BenchmarkSuite {
public:
    BenchmarkSuite(const std::string& name = "Image Filter Benchmark")
        : suite_name_(name) {}

    void add_result(const BenchmarkResult& result) {
        results_.push_back(result);
    }

    void print_header(std::ostream& os = std::cout) const {
        os << "\n" << std::string(120, '=') << "\n";
        os << suite_name_ << "\n";
        os << std::string(120, '=') << "\n";
        os << "| " << std::setw(20) << "Test Name"
           << " | " << std::setw(15) << "Filter"
           << " | " << std::setw(12) << "Resolution"
           << " | " << std::setw(3) << "Thr"
           << " | " << std::setw(8) << "Schedule"
           << " | " << std::setw(14) << "Time"
           << " | " << std::setw(8) << "Speedup"
           << " | " << std::setw(8) << "Eff"
           << " | " << std::setw(12) << "Throughput"
           << " |" << std::endl;
        os << std::string(120, '-') << "\n";
    }

    void print_results(std::ostream& os = std::cout) const {
        print_header(os);
        for (const auto& r : results_) {
            r.print(os);
        }
        os << std::string(120, '=') << "\n";
    }

    void export_csv(const std::string& filename) const {
        std::ofstream file(filename);
        if (!file) {
            std::cerr << "Error: Cannot open file " << filename << std::endl;
            return;
        }

        // CSV header
        file << "name,filter,width,height,threads,schedule,chunk_size,"
             << "time_ms,speedup,efficiency,throughput_mpps\n";

        // Data rows
        for (const auto& r : results_) {
            file << r.name << ","
                 << r.filter_name << ","
                 << r.image_width << ","
                 << r.image_height << ","
                 << r.num_threads << ","
                 << r.schedule << ","
                 << r.chunk_size << ","
                 << r.time_ms << ","
                 << r.speedup << ","
                 << r.efficiency << ","
                 << r.throughput_mpps << "\n";
        }

        std::cout << "Results exported to: " << filename << std::endl;
    }

    const std::vector<BenchmarkResult>& results() const { return results_; }

    void clear() { results_.clear(); }

private:
    std::string suite_name_;
    std::vector<BenchmarkResult> results_;
};

/**
 * @brief Run a function multiple times and return average time
 * @param func Function to benchmark (should return void)
 * @param iterations Number of iterations
 * @param warmup_iterations Warmup runs (not counted)
 * @return Average execution time in milliseconds
 */
template<typename Func>
double measure_time(Func&& func, int iterations = 5, int warmup_iterations = 1) {
    Timer timer;

    // Warmup runs
    for (int i = 0; i < warmup_iterations; ++i) {
        func();
    }

    // Measured runs
    timer.start();
    for (int i = 0; i < iterations; ++i) {
        func();
    }
    timer.stop();

    return timer.elapsed_ms() / iterations;
}

/**
 * @brief Compute speedup from serial and parallel times
 */
inline double compute_speedup(double serial_time, double parallel_time) {
    if (parallel_time <= 0) return 0;
    return serial_time / parallel_time;
}

/**
 * @brief Compute parallel efficiency
 */
inline double compute_efficiency(double speedup, int num_threads) {
    if (num_threads <= 0) return 0;
    return speedup / num_threads;
}

/**
 * @brief Compute throughput in megapixels per second
 */
inline double compute_throughput(int width, int height, double time_ms) {
    if (time_ms <= 0) return 0;
    double pixels = static_cast<double>(width) * height;
    return (pixels / 1e6) / (time_ms / 1000.0);
}

/**
 * @brief Print system information
 */
void print_system_info(std::ostream& os = std::cout);

/**
 * @brief Standard image sizes for benchmarking
 */
inline std::vector<std::pair<int, int>> standard_sizes() {
    return {
        {256, 256},
        {512, 512},
        {1024, 1024},
        {1920, 1080},   // Full HD
        {2048, 2048},
        {3840, 2160},   // 4K
        {4096, 4096}
    };
}

/**
 * @brief Standard thread counts for benchmarking
 */
inline std::vector<int> standard_thread_counts() {
    int max_threads = omp_get_max_threads();
    std::vector<int> counts = {1};

    for (int t = 2; t <= max_threads; t *= 2) {
        counts.push_back(t);
    }

    if (counts.back() != max_threads) {
        counts.push_back(max_threads);
    }

    return counts;
}

} // namespace benchmark

#endif // BENCHMARK_HPP
