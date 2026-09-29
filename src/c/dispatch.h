#ifndef DISPATCH_H
#define DISPATCH_H

#ifdef __cplusplus
extern "C" {
#endif

void init_dispatch(void);
void compute_dispatch(const float *in, float *out, int n);

#ifdef __cplusplus
}
#endif

#endif // DISPATCH_H
