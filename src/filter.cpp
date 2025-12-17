/**
 * @file filter.cpp
 * @brief Serial and OpenMP parallel image filtering implementation
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#include "filter.hpp"
#include <cmath>
#include <algorithm>
#include <stdexcept>

namespace filter {

// ============================================================================
// Utility Functions
// ============================================================================

std::string schedule_to_string(Schedule s) {
    switch (s) {
        case Schedule::STATIC:  return "static";
        case Schedule::DYNAMIC: return "dynamic";
        case Schedule::GUIDED:  return "guided";
        default: return "unknown";
    }
}

Schedule string_to_schedule(const std::string& s) {
    std::string lower = s;
    std::transform(lower.begin(), lower.end(), lower.begin(),
                   [](unsigned char c) { return std::tolower(c); });

    if (lower == "static")  return Schedule::STATIC;
    if (lower == "dynamic") return Schedule::DYNAMIC;
    if (lower == "guided")  return Schedule::GUIDED;

    throw std::invalid_argument("Unknown schedule: " + s);
}

int get_max_threads() {
    return omp_get_max_threads();
}

void set_num_threads(int n) {
    if (n > 0) {
        omp_set_num_threads(n);
    }
}

// ============================================================================
// Serial Implementation
// ============================================================================

img::GrayscaleImage apply_filter_serial(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel)
{
    img::GrayscaleImage output(input.width, input.height);
    int radius = kernel.radius();

    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            float sum = 0.0f;

            // Apply convolution
            for (int ky = -radius; ky <= radius; ++ky) {
                for (int kx = -radius; kx <= radius; ++kx) {
                    int px = x + kx;
                    int py = y + ky;

                    // Boundary handling: clamp to edge
                    px = std::max(0, std::min(px, input.width - 1));
                    py = std::max(0, std::min(py, input.height - 1));

                    float pixel_val = static_cast<float>(input.pixel(px, py));
                    float kernel_val = kernel.at(kx + radius, ky + radius);
                    sum += pixel_val * kernel_val;
                }
            }

            // Normalize and clamp
            sum /= kernel.divisor;
            sum = std::max(0.0f, std::min(255.0f, sum));
            output.pixel(x, y) = static_cast<uint8_t>(sum);
        }
    }

    return output;
}

img::RGBImage apply_filter_serial(
    const img::RGBImage& input,
    const kernels::Kernel& kernel)
{
    img::RGBImage output(input.width, input.height);
    int radius = kernel.radius();

    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            float sum_r = 0.0f, sum_g = 0.0f, sum_b = 0.0f;

            for (int ky = -radius; ky <= radius; ++ky) {
                for (int kx = -radius; kx <= radius; ++kx) {
                    int px = std::max(0, std::min(x + kx, input.width - 1));
                    int py = std::max(0, std::min(y + ky, input.height - 1));

                    float kernel_val = kernel.at(kx + radius, ky + radius);
                    sum_r += static_cast<float>(input.r(px, py)) * kernel_val;
                    sum_g += static_cast<float>(input.g(px, py)) * kernel_val;
                    sum_b += static_cast<float>(input.b(px, py)) * kernel_val;
                }
            }

            output.r(x, y) = static_cast<uint8_t>(std::clamp(sum_r / kernel.divisor, 0.0f, 255.0f));
            output.g(x, y) = static_cast<uint8_t>(std::clamp(sum_g / kernel.divisor, 0.0f, 255.0f));
            output.b(x, y) = static_cast<uint8_t>(std::clamp(sum_b / kernel.divisor, 0.0f, 255.0f));
        }
    }

    return output;
}

img::GrayscaleImage sobel_edge_detection_serial(const img::GrayscaleImage& input) {
    img::GrayscaleImage output(input.width, input.height);

    // Sobel kernels
    const int sobel_x[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    const int sobel_y[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            float gx = 0.0f, gy = 0.0f;

            for (int ky = -1; ky <= 1; ++ky) {
                for (int kx = -1; kx <= 1; ++kx) {
                    int px = std::max(0, std::min(x + kx, input.width - 1));
                    int py = std::max(0, std::min(y + ky, input.height - 1));

                    float pixel = static_cast<float>(input.pixel(px, py));
                    gx += pixel * sobel_x[ky + 1][kx + 1];
                    gy += pixel * sobel_y[ky + 1][kx + 1];
                }
            }

            // Gradient magnitude
            float magnitude = std::sqrt(gx * gx + gy * gy);
            output.pixel(x, y) = static_cast<uint8_t>(std::min(255.0f, magnitude));
        }
    }

    return output;
}

// ============================================================================
// OpenMP Parallel Implementation
// ============================================================================

img::GrayscaleImage apply_filter_parallel(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config)
{
    img::GrayscaleImage output(input.width, input.height);
    int radius = kernel.radius();

    // Set thread count
    if (config.num_threads > 0) {
        omp_set_num_threads(config.num_threads);
    }

    // Choose scheduling based on config
    switch (config.schedule) {
        case Schedule::STATIC:
            if (config.chunk_size > 0) {
                #pragma omp parallel for schedule(static, config.chunk_size)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            } else {
                #pragma omp parallel for schedule(static)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            }
            break;

        case Schedule::DYNAMIC:
            if (config.chunk_size > 0) {
                #pragma omp parallel for schedule(dynamic, config.chunk_size)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            } else {
                #pragma omp parallel for schedule(dynamic)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            }
            break;

        case Schedule::GUIDED:
            if (config.chunk_size > 0) {
                #pragma omp parallel for schedule(guided, config.chunk_size)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            } else {
                #pragma omp parallel for schedule(guided)
                for (int y = 0; y < input.height; ++y) {
                    for (int x = 0; x < input.width; ++x) {
                        float sum = 0.0f;
                        for (int ky = -radius; ky <= radius; ++ky) {
                            for (int kx = -radius; kx <= radius; ++kx) {
                                int px = std::max(0, std::min(x + kx, input.width - 1));
                                int py = std::max(0, std::min(y + ky, input.height - 1));
                                sum += static_cast<float>(input.pixel(px, py)) *
                                       kernel.at(kx + radius, ky + radius);
                            }
                        }
                        output.pixel(x, y) = static_cast<uint8_t>(
                            std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
                    }
                }
            }
            break;
    }

    return output;
}

img::RGBImage apply_filter_parallel(
    const img::RGBImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config)
{
    img::RGBImage output(input.width, input.height);
    int radius = kernel.radius();

    if (config.num_threads > 0) {
        omp_set_num_threads(config.num_threads);
    }

    #pragma omp parallel for schedule(static)
    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            float sum_r = 0.0f, sum_g = 0.0f, sum_b = 0.0f;

            for (int ky = -radius; ky <= radius; ++ky) {
                for (int kx = -radius; kx <= radius; ++kx) {
                    int px = std::max(0, std::min(x + kx, input.width - 1));
                    int py = std::max(0, std::min(y + ky, input.height - 1));

                    float kernel_val = kernel.at(kx + radius, ky + radius);
                    sum_r += static_cast<float>(input.r(px, py)) * kernel_val;
                    sum_g += static_cast<float>(input.g(px, py)) * kernel_val;
                    sum_b += static_cast<float>(input.b(px, py)) * kernel_val;
                }
            }

            output.r(x, y) = static_cast<uint8_t>(std::clamp(sum_r / kernel.divisor, 0.0f, 255.0f));
            output.g(x, y) = static_cast<uint8_t>(std::clamp(sum_g / kernel.divisor, 0.0f, 255.0f));
            output.b(x, y) = static_cast<uint8_t>(std::clamp(sum_b / kernel.divisor, 0.0f, 255.0f));
        }
    }

    return output;
}

img::GrayscaleImage sobel_edge_detection_parallel(
    const img::GrayscaleImage& input,
    const FilterConfig& config)
{
    img::GrayscaleImage output(input.width, input.height);

    if (config.num_threads > 0) {
        omp_set_num_threads(config.num_threads);
    }

    // Sobel kernels (inline for performance)
    const int sobel_x[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    const int sobel_y[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    #pragma omp parallel for schedule(static)
    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            float gx = 0.0f, gy = 0.0f;

            for (int ky = -1; ky <= 1; ++ky) {
                for (int kx = -1; kx <= 1; ++kx) {
                    int px = std::max(0, std::min(x + kx, input.width - 1));
                    int py = std::max(0, std::min(y + ky, input.height - 1));

                    float pixel = static_cast<float>(input.pixel(px, py));
                    gx += pixel * sobel_x[ky + 1][kx + 1];
                    gy += pixel * sobel_y[ky + 1][kx + 1];
                }
            }

            float magnitude = std::sqrt(gx * gx + gy * gy);
            output.pixel(x, y) = static_cast<uint8_t>(std::min(255.0f, magnitude));
        }
    }

    return output;
}

// ============================================================================
// Cache-Aware Tiled Implementation
// ============================================================================

img::GrayscaleImage apply_filter_tiled(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config)
{
    img::GrayscaleImage output(input.width, input.height);
    int radius = kernel.radius();
    int tile_size = config.tile_size;

    if (config.num_threads > 0) {
        omp_set_num_threads(config.num_threads);
    }

    // Calculate number of tiles
    int num_tiles_y = (input.height + tile_size - 1) / tile_size;
    int num_tiles_x = (input.width + tile_size - 1) / tile_size;
    int total_tiles = num_tiles_x * num_tiles_y;

    #pragma omp parallel for schedule(dynamic)
    for (int tile_idx = 0; tile_idx < total_tiles; ++tile_idx) {
        int tile_y = tile_idx / num_tiles_x;
        int tile_x = tile_idx % num_tiles_x;

        int y_start = tile_y * tile_size;
        int y_end = std::min(y_start + tile_size, input.height);
        int x_start = tile_x * tile_size;
        int x_end = std::min(x_start + tile_size, input.width);

        // Process tile
        for (int y = y_start; y < y_end; ++y) {
            for (int x = x_start; x < x_end; ++x) {
                float sum = 0.0f;

                for (int ky = -radius; ky <= radius; ++ky) {
                    for (int kx = -radius; kx <= radius; ++kx) {
                        int px = std::max(0, std::min(x + kx, input.width - 1));
                        int py = std::max(0, std::min(y + ky, input.height - 1));
                        sum += static_cast<float>(input.pixel(px, py)) *
                               kernel.at(kx + radius, ky + radius);
                    }
                }

                output.pixel(x, y) = static_cast<uint8_t>(
                    std::clamp(sum / kernel.divisor, 0.0f, 255.0f));
            }
        }
    }

    return output;
}

// ============================================================================
// Multi-pass Filtering
// ============================================================================

img::GrayscaleImage apply_filter_chain_serial(
    const img::GrayscaleImage& input,
    const std::vector<std::string>& kernel_names)
{
    if (kernel_names.empty()) {
        return input;
    }

    img::GrayscaleImage current = input;
    for (const auto& name : kernel_names) {
        kernels::Kernel k = kernels::get_kernel_by_name(name);
        current = apply_filter_serial(current, k);
    }

    return current;
}

img::GrayscaleImage apply_filter_chain_parallel(
    const img::GrayscaleImage& input,
    const std::vector<std::string>& kernel_names,
    const FilterConfig& config)
{
    if (kernel_names.empty()) {
        return input;
    }

    img::GrayscaleImage current = input;
    for (const auto& name : kernel_names) {
        kernels::Kernel k = kernels::get_kernel_by_name(name);
        current = apply_filter_parallel(current, k, config);
    }

    return current;
}

// ============================================================================
// Statistics with OpenMP Reductions
// ============================================================================

void compute_statistics_parallel(
    const img::GrayscaleImage& img,
    double& min_val,
    double& max_val,
    double& mean,
    double& variance)
{
    size_t n = img.data.size();
    if (n == 0) {
        min_val = max_val = mean = variance = 0;
        return;
    }

    double sum = 0.0;
    double sum_sq = 0.0;
    double local_min = 255.0;
    double local_max = 0.0;

    #pragma omp parallel for reduction(+:sum, sum_sq) reduction(min:local_min) reduction(max:local_max)
    for (size_t i = 0; i < n; ++i) {
        double val = static_cast<double>(img.data[i]);
        sum += val;
        sum_sq += val * val;
        if (val < local_min) local_min = val;
        if (val > local_max) local_max = val;
    }

    min_val = local_min;
    max_val = local_max;
    mean = sum / n;
    variance = (sum_sq / n) - (mean * mean);
}

std::vector<int> compute_histogram_parallel(const img::GrayscaleImage& img) {
    std::vector<int> histogram(256, 0);
    size_t n = img.data.size();

    #pragma omp parallel
    {
        // Thread-local histogram
        std::vector<int> local_hist(256, 0);

        #pragma omp for nowait
        for (size_t i = 0; i < n; ++i) {
            local_hist[img.data[i]]++;
        }

        // Combine local histograms
        #pragma omp critical
        {
            for (int i = 0; i < 256; ++i) {
                histogram[i] += local_hist[i];
            }
        }
    }

    return histogram;
}

} // namespace filter
