/**
 * @file kernels.cpp
 * @brief Convolution kernel factory implementation
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#include "kernels.hpp"
#include <algorithm>
#include <stdexcept>

namespace kernels {

Kernel get_kernel_by_name(const std::string& name) {
    // Convert to lowercase for case-insensitive matching
    std::string lower_name = name;
    std::transform(lower_name.begin(), lower_name.end(), lower_name.begin(),
                   [](unsigned char c) { return std::tolower(c); });

    // 3x3 kernels
    if (lower_name == "box_blur" || lower_name == "box_blur_3x3" ||
        lower_name == "blur" || lower_name == "average") {
        return box_blur_3x3();
    }
    if (lower_name == "gaussian" || lower_name == "gaussian_blur" ||
        lower_name == "gaussian_blur_3x3" || lower_name == "gaussian_3x3") {
        return gaussian_blur_3x3();
    }
    if (lower_name == "sharpen" || lower_name == "sharpen_3x3") {
        return sharpen_3x3();
    }
    if (lower_name == "sharpen_strong" || lower_name == "strong_sharpen") {
        return sharpen_strong_3x3();
    }
    if (lower_name == "sobel_x" || lower_name == "sobel_x_3x3" ||
        lower_name == "sobelx") {
        return sobel_x_3x3();
    }
    if (lower_name == "sobel_y" || lower_name == "sobel_y_3x3" ||
        lower_name == "sobely") {
        return sobel_y_3x3();
    }
    if (lower_name == "prewitt_x" || lower_name == "prewittx") {
        return prewitt_x_3x3();
    }
    if (lower_name == "prewitt_y" || lower_name == "prewitty") {
        return prewitt_y_3x3();
    }
    if (lower_name == "laplacian" || lower_name == "laplacian_3x3") {
        return laplacian_3x3();
    }
    if (lower_name == "emboss" || lower_name == "emboss_3x3") {
        return emboss_3x3();
    }
    if (lower_name == "identity" || lower_name == "identity_3x3") {
        return identity_3x3();
    }

    // 5x5 kernels
    if (lower_name == "box_blur_5x5" || lower_name == "blur_5x5") {
        return box_blur_5x5();
    }
    if (lower_name == "gaussian_5x5" || lower_name == "gaussian_blur_5x5") {
        return gaussian_blur_5x5();
    }
    if (lower_name == "unsharp" || lower_name == "unsharp_mask" ||
        lower_name == "unsharp_mask_5x5") {
        return unsharp_mask_5x5();
    }
    if (lower_name == "sobel_x_5x5") {
        return sobel_x_5x5();
    }
    if (lower_name == "sobel_y_5x5") {
        return sobel_y_5x5();
    }
    if (lower_name == "log" || lower_name == "log_5x5" ||
        lower_name == "laplacian_of_gaussian") {
        return log_5x5();
    }

    throw std::invalid_argument("Unknown kernel: " + name);
}

std::vector<std::string> list_kernels() {
    return {
        // 3x3 kernels
        "box_blur",
        "gaussian",
        "sharpen",
        "sharpen_strong",
        "sobel_x",
        "sobel_y",
        "prewitt_x",
        "prewitt_y",
        "laplacian",
        "emboss",
        "identity",
        // 5x5 kernels
        "box_blur_5x5",
        "gaussian_5x5",
        "unsharp_mask",
        "sobel_x_5x5",
        "sobel_y_5x5",
        "log_5x5"
    };
}

} // namespace kernels
