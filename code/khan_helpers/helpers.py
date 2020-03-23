import numpy as np
from scipy.stats import entropy


# symmetrized KL divergence
# passed to scipy.spatial.distance.cdist in Participant.reconstruct_trace
def symmetric_kl(a, b, c=1e-11):
    return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)