
class UtilityMetric:
    def __init__(self, args = None):
        self.args = args

    # Note that real_list and est_list reserves count, not probability
    def MAE(self, real_list, est_list):
        assert len(real_list) == len(est_list)
        tans = 0
        for i in range(len(real_list)):
            tans += (abs(est_list[i] - real_list[i]) * 1.0 / self.args.user_num)
        ans = tans / len(real_list)
        return ans


if __name__ == '__main__':
    pass


