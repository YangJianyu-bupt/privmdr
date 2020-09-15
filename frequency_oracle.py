import numpy as np
import math


class OUE: # OUE has the same variance as OLH
    def __init__(self, domain_size = None, epsilon = None, sampling_factor = 1, args = None):
        self.args = args
        if domain_size is None:
            self.domain_size = self.args.domain_size
        else:
            self.domain_size = domain_size
        if epsilon is None:
            self.epsilon = self.args.epsilon
        else:
            self.epsilon = epsilon


        self.group_user_num = 0
        self.perturbed_count = np.zeros(self.domain_size, dtype= int)
        self.aggregated_count = np.zeros(self.domain_size, dtype= int) # after correction
        self.p = 0.5
        self.q = 1.0 / (math.exp(self.epsilon) + 1)
        self.sampling_factor = sampling_factor

    def operation_perturb(self, real_value = None):
        self.perturbed_count[real_value] += 1
        return

    def operation_aggregate(self):
        tmp_perturbed_count_1 = np.copy(self.perturbed_count)
        est_count = np.random.binomial(tmp_perturbed_count_1, self.p)
        tmp_perturbed_count_0 = self.group_user_num - np.copy(self.perturbed_count)
        est_count += np.random.binomial(tmp_perturbed_count_0, self.q)
        a = 1.0 / (self.p - self.q)
        b = self.group_user_num * self.q / (self.p - self.q)
        est_count = a * est_count - b

        # convert count to probability
        self.aggregated_count = est_count / self.group_user_num * self.args.user_num
        return



