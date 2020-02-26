import numpy as np
from numba import jit


@jit
def corrdist_exp(a, b):
    a = np.exp(a)
    b = np.exp(b)
    n = a.shape[0]
    mu_a = 0.0
    mu_b = 0.0
    norm_a = 0.0
    norm_b = 0.0
    dot_prod = 0.0

    for i in range(n):
        mu_a += a[i]
        mu_b += b[i]

    mu_a /= a.shape[0]
    mu_b /= b.shape[0]

    for i in range(n):
        mu_a += a[i]
        mu_b += b[i]

    mu_a /= n
    mu_b /= n

    for i in range(n):
        shifted_a = a[i] - mu_a
        shifted_b = b[i] - mu_b
        norm_a += shifted_a ** 2
        norm_b += shifted_b ** 2
        dot_prod += shifted_a * shifted_b

    if norm_a == 0.0 and norm_a == 0.0:
        return 0.0
    elif dot_prod == 0.0:
        return 1.0
    else:
        return 1.0 - (dot_prod / np.sqrt(norm_a * norm_b))


@jit
def euclidean_exp(a, b):
    a = np.exp(a)
    b = np.exp(b)
    ret = 0.0

    for i in range(a.shape[0]):
        ret += (a[i] - b[i]) ** 2

    return np.sqrt(ret)


@jit
def symmetric_kl_exp(a, b, c=1e-11):
    a = np.exp(a)
    b = np.exp(b)
    n = a.shape[0]
    a_sum = 0.0
    b_sum = 0.0
    kl1 = 0.0
    kl2 = 0.0

    for i in range(n):
        a[i] += c
        a_sum += a[i]
        b[i] += c
        b_sum += b[i]

    for i in range(n):
        a[i] /= a_sum
        b[i] /= b_sum

    for i in range(n):
        kl1 += a[i] * np.log(a[i] / b[i])
        kl2 += b[i] * np.log(b[i] / a[i])

    return (kl1 + kl2) / 2


distance_funcs = {
    'euclidean': euclidean_exp,
    'correlation': corrdist_exp,
    'kl': symmetric_kl_exp
}