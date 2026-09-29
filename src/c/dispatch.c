#include "dispatch.h"
#include <stdio.h>

// compute_impl is provided by variant-specific compilation unit
extern void compute_impl(const float *in, float *out, int n);

void init_dispatch(void) {
    // Runtime CPU detection and selection would go here.
    // For xmake-built variant artifacts, the appropriate implementation
    // is compiled into the binary.
}

void compute_dispatch(const float *in, float *out, int n) {
    compute_impl(in, out, n);
}
