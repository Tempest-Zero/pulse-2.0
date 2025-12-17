/**
 * @file main.cpp
 * @brief Main entry point for OpenMP image filtering application
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 *
 * Usage:
 *   ./image_filter [options]
 *
 * Options:
 *   -i, --input <file>     Input image file (PGM/PPM)
 *   -o, --output <file>    Output image file
 *   -f, --filter <name>    Filter to apply (blur, sharpen, sobel, etc.)
 *   -t, --threads <n>      Number of threads (default: auto)
 *   -s, --schedule <type>  OpenMP schedule (static, dynamic, guided)
 *   -c, --chunk <size>     Chunk size for scheduling
 *   --tiled                Use cache-aware tiled implementation
 *   --tile-size <n>        Tile size (default: 64)
 *   -b, --benchmark        Run full benchmark suite
 *   --generate <size>      Generate test image (e.g., 1024x1024)
 *   --pattern <n>          Test pattern type (0-4)
 *   -l, --list             List available filters
 *   -h, --help             Show this help message
 */

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstring>
#include <sstream>

#include "image.hpp"
#include "kernels.hpp"
#include "filter.hpp"
#include "benchmark.hpp"

// ============================================================================
// Command Line Parsing
// ============================================================================

struct Options {
    std::string input_file;
    std::string output_file;
    std::string filter_name = "gaussian";
    int num_threads = 0;
    filter::Schedule schedule = filter::Schedule::STATIC;
    int chunk_size = 0;
    bool use_tiled = false;
    int tile_size = 64;
    bool run_benchmark = false;
    bool generate_test = false;
    int gen_width = 1024;
    int gen_height = 1024;
    int pattern = 0;
    bool list_filters = false;
    bool show_help = false;
    bool serial_only = false;
    bool compare_mode = false;
};

void print_usage(const char* program) {
    std::cout << R"(
OpenMP-Accelerated Image Filtering and Edge Detection
======================================================
CS-361L Computer Architecture Lab Project
Author: Muhammad Bilal (2023394)

Usage: )" << program << R"( [options]

Options:
  -i, --input <file>     Input image file (PGM/PPM)
  -o, --output <file>    Output image file
  -f, --filter <name>    Filter to apply (default: gaussian)
  -t, --threads <n>      Number of threads (default: auto)
  -s, --schedule <type>  OpenMP schedule: static, dynamic, guided
  -c, --chunk <size>     Chunk size for scheduling
  --tiled                Use cache-aware tiled implementation
  --tile-size <n>        Tile size (default: 64)
  --serial               Run serial implementation only
  --compare              Compare serial vs parallel execution
  -b, --benchmark        Run full benchmark suite
  --generate <WxH>       Generate test image (e.g., 1024x1024)
  --pattern <n>          Test pattern: 0=gradient, 1=checker, 2=circles, 3=stripes, 4=edges
  -l, --list             List available filters
  -h, --help             Show this help message

Examples:
  # Apply Gaussian blur to an image
  )" << program << R"( -i input.pgm -o output.pgm -f gaussian -t 4

  # Run edge detection with dynamic scheduling
  )" << program << R"( -i photo.pgm -o edges.pgm -f sobel -s dynamic

  # Generate test image and apply filter
  )" << program << R"( --generate 2048x2048 --pattern 1 -f sharpen -o sharp.pgm

  # Run full benchmark suite
  )" << program << R"( -b

  # Compare serial vs parallel performance
  )" << program << R"( -i input.pgm -f blur --compare

)";
}

Options parse_args(int argc, char* argv[]) {
    Options opts;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            opts.show_help = true;
        } else if (arg == "-l" || arg == "--list") {
            opts.list_filters = true;
        } else if (arg == "-b" || arg == "--benchmark") {
            opts.run_benchmark = true;
        } else if (arg == "--serial") {
            opts.serial_only = true;
        } else if (arg == "--compare") {
            opts.compare_mode = true;
        } else if (arg == "--tiled") {
            opts.use_tiled = true;
        } else if ((arg == "-i" || arg == "--input") && i + 1 < argc) {
            opts.input_file = argv[++i];
        } else if ((arg == "-o" || arg == "--output") && i + 1 < argc) {
            opts.output_file = argv[++i];
        } else if ((arg == "-f" || arg == "--filter") && i + 1 < argc) {
            opts.filter_name = argv[++i];
        } else if ((arg == "-t" || arg == "--threads") && i + 1 < argc) {
            opts.num_threads = std::stoi(argv[++i]);
        } else if ((arg == "-s" || arg == "--schedule") && i + 1 < argc) {
            opts.schedule = filter::string_to_schedule(argv[++i]);
        } else if ((arg == "-c" || arg == "--chunk") && i + 1 < argc) {
            opts.chunk_size = std::stoi(argv[++i]);
        } else if (arg == "--tile-size" && i + 1 < argc) {
            opts.tile_size = std::stoi(argv[++i]);
        } else if (arg == "--generate" && i + 1 < argc) {
            opts.generate_test = true;
            std::string size_str = argv[++i];
            size_t x_pos = size_str.find('x');
            if (x_pos != std::string::npos) {
                opts.gen_width = std::stoi(size_str.substr(0, x_pos));
                opts.gen_height = std::stoi(size_str.substr(x_pos + 1));
            } else {
                opts.gen_width = opts.gen_height = std::stoi(size_str);
            }
        } else if (arg == "--pattern" && i + 1 < argc) {
            opts.pattern = std::stoi(argv[++i]);
        }
    }

    return opts;
}

// ============================================================================
// Filter Application
// ============================================================================

void apply_single_filter(const Options& opts) {
    img::GrayscaleImage input;

    // Load or generate input image
    if (opts.generate_test) {
        std::cout << "Generating test image " << opts.gen_width << "x" << opts.gen_height
                  << " (pattern " << opts.pattern << ")...\n";
        input = img::generate_test_image(opts.gen_width, opts.gen_height, opts.pattern);
    } else if (!opts.input_file.empty()) {
        std::cout << "Loading: " << opts.input_file << "...\n";
        input = img::read_pgm(opts.input_file);
    } else {
        std::cerr << "Error: No input file specified. Use --generate or -i option.\n";
        return;
    }

    std::cout << "Image size: " << input.width << "x" << input.height
              << " (" << (input.width * input.height / 1e6) << " MP)\n";

    // Get kernel
    kernels::Kernel kernel;
    bool is_sobel_edge = (opts.filter_name == "sobel" || opts.filter_name == "edges");

    if (!is_sobel_edge) {
        kernel = kernels::get_kernel_by_name(opts.filter_name);
        std::cout << "Filter: " << kernel.name << " (" << kernel.size << "x" << kernel.size << ")\n";
    } else {
        std::cout << "Filter: Sobel Edge Detection\n";
    }

    // Setup configuration
    filter::FilterConfig config;
    config.num_threads = opts.num_threads;
    config.schedule = opts.schedule;
    config.chunk_size = opts.chunk_size;
    config.use_tiling = opts.use_tiled;
    config.tile_size = opts.tile_size;

    img::GrayscaleImage output;
    benchmark::Timer timer;

    if (opts.compare_mode) {
        // Compare serial vs parallel
        std::cout << "\n--- Serial vs Parallel Comparison ---\n";

        // Serial
        timer.start();
        if (is_sobel_edge) {
            output = filter::sobel_edge_detection_serial(input);
        } else {
            output = filter::apply_filter_serial(input, kernel);
        }
        timer.stop();
        double serial_time = timer.elapsed_ms();
        std::cout << "Serial time: " << serial_time << " ms\n";

        // Parallel
        timer.reset();
        timer.start();
        if (is_sobel_edge) {
            output = filter::sobel_edge_detection_parallel(input, config);
        } else if (opts.use_tiled) {
            output = filter::apply_filter_tiled(input, kernel, config);
        } else {
            output = filter::apply_filter_parallel(input, kernel, config);
        }
        timer.stop();
        double parallel_time = timer.elapsed_ms();

        int threads = opts.num_threads > 0 ? opts.num_threads : omp_get_max_threads();
        double speedup = serial_time / parallel_time;
        double efficiency = speedup / threads;

        std::cout << "Parallel time (" << threads << " threads): " << parallel_time << " ms\n";
        std::cout << "Speedup: " << speedup << "x\n";
        std::cout << "Efficiency: " << (efficiency * 100) << "%\n";
        std::cout << "Throughput: " << benchmark::compute_throughput(input.width, input.height, parallel_time) << " MP/s\n";

    } else if (opts.serial_only) {
        // Serial only
        timer.start();
        if (is_sobel_edge) {
            output = filter::sobel_edge_detection_serial(input);
        } else {
            output = filter::apply_filter_serial(input, kernel);
        }
        timer.stop();
        std::cout << "Serial execution time: " << timer.elapsed_ms() << " ms\n";

    } else {
        // Parallel (default)
        std::cout << "Using " << (opts.num_threads > 0 ? opts.num_threads : omp_get_max_threads())
                  << " threads, schedule: " << filter::schedule_to_string(opts.schedule);
        if (opts.chunk_size > 0) {
            std::cout << " (chunk=" << opts.chunk_size << ")";
        }
        if (opts.use_tiled) {
            std::cout << " [tiled, tile_size=" << opts.tile_size << "]";
        }
        std::cout << "\n";

        timer.start();
        if (is_sobel_edge) {
            output = filter::sobel_edge_detection_parallel(input, config);
        } else if (opts.use_tiled) {
            output = filter::apply_filter_tiled(input, kernel, config);
        } else {
            output = filter::apply_filter_parallel(input, kernel, config);
        }
        timer.stop();
        std::cout << "Parallel execution time: " << timer.elapsed_ms() << " ms\n";
        std::cout << "Throughput: " << benchmark::compute_throughput(input.width, input.height, timer.elapsed_ms()) << " MP/s\n";
    }

    // Save output
    if (!opts.output_file.empty()) {
        img::write_pgm(opts.output_file, output);
        std::cout << "Output saved to: " << opts.output_file << "\n";
    }
}

// ============================================================================
// Benchmark Suite
// ============================================================================

void run_benchmark_suite() {
    benchmark::print_system_info();

    benchmark::BenchmarkSuite suite("OpenMP Image Filtering Benchmark");

    // Test configurations
    std::vector<std::pair<int, int>> sizes = {
        {512, 512},
        {1024, 1024},
        {2048, 2048},
        {1920, 1080},
        {4096, 4096}
    };

    std::vector<std::string> filters = {
        "gaussian",
        "sharpen",
        "sobel_x",
        "gaussian_5x5"
    };

    std::vector<int> thread_counts = benchmark::standard_thread_counts();

    std::vector<filter::Schedule> schedules = {
        filter::Schedule::STATIC,
        filter::Schedule::DYNAMIC,
        filter::Schedule::GUIDED
    };

    int iterations = 3;
    int warmup = 1;

    std::cout << "Running benchmark suite...\n";
    std::cout << "Image sizes: " << sizes.size() << "\n";
    std::cout << "Filters: " << filters.size() << "\n";
    std::cout << "Thread counts: " << thread_counts.size() << "\n";
    std::cout << "Schedules: " << schedules.size() << "\n";
    std::cout << "Iterations per test: " << iterations << "\n\n";

    for (const auto& [width, height] : sizes) {
        std::cout << "\n=== Image size: " << width << "x" << height << " ===\n";

        // Generate test image
        img::GrayscaleImage test_img = img::generate_test_image(width, height, 1);

        for (const auto& filter_name : filters) {
            kernels::Kernel kernel = kernels::get_kernel_by_name(filter_name);
            std::cout << "\nFilter: " << kernel.name << "\n";

            // Baseline serial measurement
            double serial_time = benchmark::measure_time([&]() {
                filter::apply_filter_serial(test_img, kernel);
            }, iterations, warmup);

            benchmark::BenchmarkResult serial_result;
            serial_result.name = "Serial";
            serial_result.filter_name = kernel.name;
            serial_result.image_width = width;
            serial_result.image_height = height;
            serial_result.num_threads = 1;
            serial_result.schedule = "N/A";
            serial_result.chunk_size = 0;
            serial_result.time_ms = serial_time;
            serial_result.speedup = 1.0;
            serial_result.efficiency = 1.0;
            serial_result.throughput_mpps = benchmark::compute_throughput(width, height, serial_time);
            suite.add_result(serial_result);

            std::cout << "  Serial: " << serial_time << " ms\n";

            // Parallel measurements
            for (int num_threads : thread_counts) {
                for (auto sched : schedules) {
                    filter::FilterConfig config;
                    config.num_threads = num_threads;
                    config.schedule = sched;

                    double parallel_time = benchmark::measure_time([&]() {
                        filter::apply_filter_parallel(test_img, kernel, config);
                    }, iterations, warmup);

                    double speedup = benchmark::compute_speedup(serial_time, parallel_time);
                    double efficiency = benchmark::compute_efficiency(speedup, num_threads);

                    benchmark::BenchmarkResult result;
                    result.name = "Parallel";
                    result.filter_name = kernel.name;
                    result.image_width = width;
                    result.image_height = height;
                    result.num_threads = num_threads;
                    result.schedule = filter::schedule_to_string(sched);
                    result.chunk_size = 0;
                    result.time_ms = parallel_time;
                    result.speedup = speedup;
                    result.efficiency = efficiency;
                    result.throughput_mpps = benchmark::compute_throughput(width, height, parallel_time);
                    suite.add_result(result);

                    std::cout << "  " << num_threads << " threads ("
                              << filter::schedule_to_string(sched) << "): "
                              << parallel_time << " ms, "
                              << speedup << "x speedup\n";
                }
            }

            // Tiled implementation
            filter::FilterConfig tiled_config;
            tiled_config.num_threads = omp_get_max_threads();
            tiled_config.tile_size = 64;

            double tiled_time = benchmark::measure_time([&]() {
                filter::apply_filter_tiled(test_img, kernel, tiled_config);
            }, iterations, warmup);

            double tiled_speedup = benchmark::compute_speedup(serial_time, tiled_time);

            benchmark::BenchmarkResult tiled_result;
            tiled_result.name = "Tiled";
            tiled_result.filter_name = kernel.name;
            tiled_result.image_width = width;
            tiled_result.image_height = height;
            tiled_result.num_threads = omp_get_max_threads();
            tiled_result.schedule = "dynamic";
            tiled_result.chunk_size = 64;
            tiled_result.time_ms = tiled_time;
            tiled_result.speedup = tiled_speedup;
            tiled_result.efficiency = benchmark::compute_efficiency(tiled_speedup, omp_get_max_threads());
            tiled_result.throughput_mpps = benchmark::compute_throughput(width, height, tiled_time);
            suite.add_result(tiled_result);

            std::cout << "  Tiled (64x64): " << tiled_time << " ms, "
                      << tiled_speedup << "x speedup\n";
        }
    }

    // Print and export results
    suite.print_results();
    suite.export_csv("benchmark_results.csv");

    std::cout << "\nBenchmark complete! Results saved to benchmark_results.csv\n";
}

// ============================================================================
// Main
// ============================================================================

int main(int argc, char* argv[]) {
    try {
        Options opts = parse_args(argc, argv);

        if (opts.show_help || argc == 1) {
            print_usage(argv[0]);
            return 0;
        }

        if (opts.list_filters) {
            std::cout << "Available filters:\n";
            for (const auto& name : kernels::list_kernels()) {
                auto k = kernels::get_kernel_by_name(name);
                std::cout << "  " << name << " (" << k.size << "x" << k.size << ") - " << k.name << "\n";
            }
            std::cout << "\nSpecial filters:\n";
            std::cout << "  sobel, edges - Sobel edge detection (combined gradient magnitude)\n";
            return 0;
        }

        if (opts.run_benchmark) {
            run_benchmark_suite();
            return 0;
        }

        // Single filter application
        apply_single_filter(opts);

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
