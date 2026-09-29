#include <stddef.h>
#include <string.h>

void compute_impl(const float *in, float *out, int n) {
    // simple scalar implementation: copy and set first element to sum
    float s = 0.0f;
    for (int i = 0; i < n; ++i) s += in[i];
    memset(out, 0, n * sizeof(float));
    if (n > 0) out[0] = s;
}
