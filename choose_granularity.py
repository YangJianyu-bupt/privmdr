import math

class choose_granularity_beta:
    def __init__(self, args = None):
        self.args = args
        self.flag_granularity_list = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
        self.alpha_1 = 0.7
        self.alpha_2 = 0.03

    def get_1_way_granularity_for_HDG(self, ep = None):
        n = self.args.user_num
        k = self.args.attribute_num + self.args.attribute_num * (self.args.attribute_num - 1) // 2

        x1 = n * (math.exp(ep) - 1) * (math.exp(ep) - 1) * self.alpha_1 * self.alpha_1
        x2 = 2 * k * math.exp(ep)
        g1 = math.pow(x1 / x2, 1 / 3)

        if g1 > self.args.domain_size:
            g1 = self.args.domain_size
        return g1



    def get_2_way_granularity_for_HDG(self, ep = None):
        n = self.args.user_num
        k = self.args.attribute_num + self.args.attribute_num * (self.args.attribute_num - 1) // 2

        x1 = 2 * self.alpha_2 * (math.exp(ep) - 1)
        x2 = n / (k * math.exp(ep))
        x3 = math.sqrt(x2)
        g2 = math.sqrt(x1 * x3)

        if g2 > self.args.domain_size:
            g2 = self.args.domain_size
        return g2


    def get_2_way_granularity_for_TDG(self, ep=None):
        n = self.args.user_num
        k = self.args.attribute_num * (self.args.attribute_num - 1) // 2

        x1 = 2 * self.alpha_2 * (math.exp(ep) - 1)
        x2 = n / (k * math.exp(ep))
        x3 = math.sqrt(x2)
        g2 = math.sqrt(x1 * x3)

        if g2 > self.args.domain_size:
            g2 = self.args.domain_size
        return g2


    def get_rounding_to_pow_2(self, gran = None):
        tmp_len = len(self.flag_granularity_list)

        for i in range(tmp_len - 1):
            if self.flag_granularity_list[i] <= gran and gran <= self.flag_granularity_list[i + 1]:
                dis_left = gran - self.flag_granularity_list[i]
                dis_right = self.flag_granularity_list[i + 1] - gran
                if dis_left <= dis_right:
                    if self.flag_granularity_list[i] == 1:
                        return 2
                    return self.flag_granularity_list[i]
                else:
                    return self.flag_granularity_list[i + 1]
            elif gran <= 1:
                return 2


