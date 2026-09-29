// C++ wrapper that can call Google/highway optimized kernels when available.
// Compile with -DUSE_HIGHWAY and add include path for highway to enable.

#include <cstddef>
#include <cstring>

extern "C" {
void compute_impl(const float *in, float *out, int n);
}

#if defined(USE_HIGHWAY)
// If you enable USE_HIGHWAY, make sure highway is available on your include path.
// Example integration point:
// #include <hwy/highway.h>
// using namespace hwy;
// Then implement a ReduceSum over the input array using Highway vectors.

#include <hwy/highway.h>

// Note: The exact Highway API usage depends on the version; the code below is a
// placeholder that demonstrates intent. Replace with proper HWY dispatch and
// reduction patterns from highway examples when integrating.

void compute_impl(const float *in, float *out, int n) {
    // Placeholder using Highway pseudo-API. Replace with real Highway calls.
    // For now, fall back to a scalar loop to ensure correctness.
    float s = 0.0f;
    for (int i = 0; i < n; ++i) s += in[i];
    std::memset(out, 0, n * sizeof(float));
    if (n > 0) out[0] = s;
}

#else

// Fallback scalar implementation when Highway unavailable
void compute_impl(const float *in, float *out, int n) {
    float s = 0.0f;
    for (int i = 0; i < n; ++i) s += in[i];
    std::memset(out, 0, n * sizeof(float));
    if (n > 0) out[0] = s;
}

#endif
