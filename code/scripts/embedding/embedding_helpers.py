import numba
import numpy as np
from math import e


@numba.njit
def correlation_exp(x, y):
    x = e ** x
    y = e ** y
    mu_x = 0.0
    mu_y = 0.0
    norm_x = 0.0
    norm_y = 0.0
    dot_product = 0.0

    for i in range(x.shape[0]):
        mu_x += x[i]
        mu_y += y[i]

    mu_x /= x.shape[0]
    mu_y /= x.shape[0]

    for i in range(x.shape[0]):
        shifted_x = x[i] - mu_x
        shifted_y = y[i] - mu_y
        norm_x += shifted_x ** 2
        norm_y += shifted_y ** 2
        dot_product += shifted_x * shifted_y

    if norm_x == 0.0 and norm_y == 0.0:
        dist = 0.0
        grad = np.zeros(x.shape)
    elif dot_product == 0.0:
        dist = 1.0
        grad = np.zeros(x.shape)
    else:
        dist = 1.0 - (dot_product / np.sqrt(norm_x * norm_y))
        grad = ((x - mu_x) / norm_x - (y - mu_y) / dot_product) * dist

    return dist, grad


# @numba.njit(fastmath=True)
# def euclidean_exp(x, y):
#     x = e ** x
#     y = e ** y
#     result = 0.0
#     for i in range(x.shape[0]):
#         result += (x[i] - y[i]) ** 2
#     d = np.sqrt(result)
#     grad = (x - y) / (1e-6 + d)
#     return d, grad


# @numba.njit(fastmath=True)
# def symmetric_kl_exp(x, y, z=1e-11):
#     x = e ** x
#     y = e ** y
#     n = x.shape[0]
#     x_sum = 0.0
#     y_sum = 0.0
#     kl1 = 0.0
#     kl2 = 0.0
#
#     for i in range(n):
#         x[i] += z
#         x_sum += x[i]
#         y[i] += z
#         y_sum += y[i]
#
#     for i in range(n):
#         x[i] /= x_sum
#         y[i] /= y_sum
#
#     for i in range(n):
#         kl1 += x[i] * np.log(x[i] / y[i])
#         kl2 += y[i] * np.log(y[i] / x[i])
#
#     dist = (kl1 + kl2) / 2
#     grad = (np.log(y / x) - (x / y) + 1) / 2
#     return dist, grad


# distance_funcs = {
#     'euclidean': euclidean_exp,
#     'correlation': correlation_exp
#     # 'kl': symmetric_kl_exp
# }
