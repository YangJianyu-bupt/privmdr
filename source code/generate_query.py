import random
import sys
import numpy as np


class QueryAttributeNode:
    def __init__(self, attribute= -1, interval_length = -1, args = None):
        self.args = args
        self.attribute= attribute
        self.interval_length_ratio = 1
        self.interval_length = interval_length
        if self.interval_length == -1: # use this to make the default value equal to self.args.domain_size
            self.interval_length = self.args.domain_size

        self.left_interval = 0
        self.right_interval = self.left_interval + self.interval_length - 1

        self.selected_left_interval_ratio = 0


    def set_interval_length_ratio(self, interval_length_ratio = 1.0):
        self.interval_length_ratio = interval_length_ratio
        self.left_interval = 0 # need to be revised for random interval selected

        flag_domain_size = 16
        if self.args.domain_size < flag_domain_size:
            flag_domain_size = self.args.domain_size

        self.interval_length = int(flag_domain_size * self.interval_length_ratio)
        tmp_max_left_interval = flag_domain_size - self.interval_length
        self.left_interval = random.randint(0, tmp_max_left_interval)
        self.right_interval = self.left_interval + self.interval_length - 1
        self.left_interval = self.left_interval * (self.args.domain_size // flag_domain_size)
        self.right_interval = self.right_interval * (self.args.domain_size // flag_domain_size) + (self.args.domain_size // flag_domain_size) - 1

        assert self.right_interval < self.args.domain_size
        return


class RangeQuery:
    def __init__(self, query_dimension = -1, attribute_num = -1, args = None):
        self.args = args
        self.query_dimension = query_dimension
        self.attribute_num = attribute_num
        self.selected_attribute_list =[]
        self.attribute_list = [i for i in range(self.attribute_num)]
        self.query_attribute_node_list = []
        assert self.query_dimension <= self.attribute_num
        self.real_answer = None


    def initialize_range_query(self):
        for i in range(self.attribute_num):
            self.query_attribute_node_list.append(QueryAttributeNode(i, args= self.args))

    def set_selected_attribute_list(self):
        arr = self.attribute_list.copy()
        np.random.shuffle(arr)
        self.selected_attribute_list = arr[:self.query_dimension]
        self.selected_attribute_list.sort()


    def set_query_attribute_node_list_interval_length_ratio(self, interval_length_ratio=1.0):
        for i in self.selected_attribute_list:
            self.query_attribute_node_list[i].set_interval_length_ratio(interval_length_ratio)


    def print_range_query(self, file_out = None):
        if file_out is None:
            file_out = sys.stdout
        print("selected attributes:", self.selected_attribute_list, end="\t\t: ", file= file_out)
        for tmp_query_node in self.query_attribute_node_list:
            print("[", tmp_query_node.attribute, "|", \
                  tmp_query_node.left_interval, tmp_query_node.right_interval, "]", end=" ", file=file_out)

        print('real_answer:', self.real_answer, end=" ", file=file_out)
        print(file= file_out)


    def Main(self):
        self.initialize_range_query()
        self.set_selected_attribute_list()



class RangeQueryList:
    def __init__(self, query_dimension = -1, attribute_num = -1, query_num = -1, dimension_query_volume = 0.1, args = None):
        self.args = args
        self.query_dimension = query_dimension
        self.query_num = query_num
        self.attribute_num = attribute_num
        if self.attribute_num == -1:
            self.attribute_num = self.args.attribute_num
        self.range_query_list = []
        self.real_answer_list = []
        self.dimension_query_volume = dimension_query_volume
        self.direct_multiply_MNAE = None
        self.max_entropy_MNAE = None
        self.weight_update_MNAE = None
        assert self.query_dimension <= self.attribute_num and self.query_num > 0

    def generate_range_query_list(self):
        print("generating range queries...")
        for i in range(self.query_num):
            tmp_range_query = RangeQuery(self.query_dimension, self.attribute_num, args= self.args)
            tmp_range_query.Main()
            tmp_range_query.set_query_attribute_node_list_interval_length_ratio(self.dimension_query_volume)
            self.range_query_list.append(tmp_range_query)

        return

    def generate_real_answer_list(self, user_record):
        print("get real counts of queries...")
        for tmp_range_query in self.range_query_list:
            tans = 0
            for user_i in range(self.args.user_num):
                flag = True
                # for tmp_attribute_node in tmp_range_query.query_attribute_node_list:
                for tmp_attribute in tmp_range_query.selected_attribute_list:
                    tmp_attribute_node = tmp_range_query.query_attribute_node_list[tmp_attribute]
                    tmp_val = user_record[user_i][tmp_attribute]
                    if tmp_val >= tmp_attribute_node.left_interval and tmp_val <= tmp_attribute_node.right_interval:
                        pass
                    else:
                        flag = False
                        break
                if flag:
                    tans += 1

            tmp_range_query.real_answer = tans
            self.real_answer_list.append(tans)
        return


    def Main(self):
        self.generate_range_query_list()

    def print_range_query_list(self, file_out = None):
        for i in range(len(self.range_query_list)):
            tmp_range_query = self.range_query_list[i]
            tmp_range_query.print_range_query(file_out)

