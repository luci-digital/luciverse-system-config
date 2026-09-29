#include "dispatch.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    init_dispatch();
    int n = 8;
    float in[8];
    float out[8];
    for (int i = 0; i < n; ++i) in[i] = (float)i + 1.0f;
    compute_dispatch(in, out, n);
    printf("result[0]=%f\n", out[0]);
    return 0;
}
