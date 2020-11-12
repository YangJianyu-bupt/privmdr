import numpy as np
import math
import grid_generate as GridGen
import estimate_method as EstMeth
import frequency_oracle as FreOra
import itertools
import choose_granularity


class AG_Uniform_Grid_1_2_way_optimal:
    def __init__(self, args = None):
        self.args = args
        self.group_attribute_num = 2 # to construct 2-D grids
        self.group_num = 0
        self.AG = []  # attribute_group
        self.Grid_set = []
        self.answer_list = []
        self.weighted_update_answer_list = []
        self.granularity = None # granularity g2
        self.granularity_1_way = None # granularity g1
        self.LDP_mechanism_list_divide_user = [] # LDP mechanism for each attribute group
        self.set_granularity_1_2_way()


    def set_granularity_1_2_way(self):
        chooseGran = choose_granularity.choose_granularity_beta(args= self.args)
        tmp_g1 = chooseGran.get_1_way_granularity_for_HDG(ep= self.args.epsilon)
        tmp_g2 = chooseGran.get_2_way_granularity_for_HDG(ep= self.args.epsilon)
        self.granularity_1_way = chooseGran.get_rounding_to_pow_2(gran= tmp_g1)
        self.granularity = chooseGran.get_rounding_to_pow_2(gran= tmp_g2)

        self.args.granularity_1_way = self.granularity_1_way
        self.args.granularity = self.granularity


    def judge_sub_attribute_in_attribute_group(self, sub_attribute = None, attribute_group:list = None):
        if sub_attribute in attribute_group:
            return True
        else:
            return False


    def get_C_W_list(self, sub_attribute_value = None, sub_attribute = None, relevant_attribute_group_list:list = None):
        C_list = np.zeros(self.args.group_num)
        C_reci_list = np.zeros(self.args.group_num)
        for i in relevant_attribute_group_list:
            tmp_grid = self.Grid_set[i]
            if len(tmp_grid.attribute_set) == 1:
                C_list[i] = self.args.granularity_1_way // self.args.granularity
            else:
                C_list[i] = self.args.granularity
            C_reci_list[i] = 1.0 / C_list[i]
        return C_list, C_reci_list


    def get_T_A_a(self, sub_attribute_value = None, sub_attribute = None, relevant_attribute_group_list:list = None, C_reci_list = None):
        sum_C_reci_list = sum(C_reci_list)
        sum_T_V_i_a = 0
        for i in relevant_attribute_group_list:
            T_V_i_a = 0
            tmp_grid = self.Grid_set[i]
            if len(tmp_grid.attribute_set) == 1:
                left_interval_1_way = sub_attribute_value * (self.args.granularity_1_way // self.args.granularity)
                right_interval_1_way = (sub_attribute_value + 1) * (self.args.granularity_1_way // self.args.granularity) - 1
                k = left_interval_1_way
                while k <= right_interval_1_way:
                    tmp_cell = tmp_grid.cell_list[k]
                    T_V_i_a += tmp_cell.consistent_count
                    k += 1
            else:
                sub_attribute_index_in_grid = tmp_grid.attribute_set.index(sub_attribute)
                for tmp_cell in tmp_grid.cell_list:
                    if tmp_cell.dimension_index_list[sub_attribute_index_in_grid] == sub_attribute_value:
                        T_V_i_a += tmp_cell.consistent_count

            sum_T_V_i_a += (C_reci_list[i] * T_V_i_a)
        T_A_a = sum_T_V_i_a / sum_C_reci_list
        return T_A_a




    def get_consistency_for_sub_attribute(self, sub_attribute = None):
        relevant_attribute_group_list = []
        for i in range(self.group_num):
            if self.judge_sub_attribute_in_attribute_group(sub_attribute, self.AG[i]):
                relevant_attribute_group_list.append(i)

        sub_attribute_domain = range(self.args.granularity) # need to be changed for 3-way attribute group
        for sub_attribute_value in sub_attribute_domain:
            C_list, C_reci_list = self.get_C_W_list(sub_attribute_value, sub_attribute, relevant_attribute_group_list)
            T_A_a = self.get_T_A_a(sub_attribute_value, sub_attribute, relevant_attribute_group_list, C_reci_list)

            for i in relevant_attribute_group_list: #update T_V_i_c
                T_V_i_a = 0
                T_V_i_c_cell_list = []
                tmp_grid = self.Grid_set[i]
                if len(tmp_grid.attribute_set) == 1:
                    left_interval_1_way = sub_attribute_value * (self.args.granularity_1_way // self.args.granularity)
                    right_interval_1_way = (sub_attribute_value + 1) * (self.args.granularity_1_way // self.args.granularity) - 1
                    k = left_interval_1_way
                    while k <= right_interval_1_way:
                        tmp_cell = tmp_grid.cell_list[k]
                        T_V_i_c_cell_list.append(k)
                        T_V_i_a += tmp_cell.consistent_count
                        k += 1
                else:
                    sub_attribute_index_in_grid = tmp_grid.attribute_set.index(sub_attribute)
                    for k in range(len(tmp_grid.cell_list)):
                        tmp_cell = tmp_grid.cell_list[k]
                        if tmp_cell.dimension_index_list[sub_attribute_index_in_grid] == sub_attribute_value:
                            T_V_i_c_cell_list.append(k)
                            T_V_i_a += tmp_cell.consistent_count

                for k in T_V_i_c_cell_list:
                    tmp_cell = tmp_grid.cell_list[k]
                    tmp_cell.consistent_count = tmp_cell.consistent_count + (T_A_a - T_V_i_a) * C_reci_list[i]
        return

    def overall_consistency(self):
        for i in range(self.args.attribute_num):
            self.get_consistency_for_sub_attribute(i)
        return

    def get_consistent_Grid_set(self):
        for tmp_grid in self.Grid_set:
            tmp_grid.get_consistent_grid()
        self.overall_consistency()
        for i in range(self.args.consistency_iteration_num_max):
            for tmp_grid in self.Grid_set:
                tmp_grid.get_consistent_grid_iteration()
            self.overall_consistency()

        # end with the Non-Negativity step
        for tmp_grid in self.Grid_set:
            tmp_grid.get_consistent_grid_iteration()
        return

    #*************consistency end*******************************

    def weighted_update_iteration(self, grid_1_way_list = None, grid_2_way = None):
        # update using 1_way
        for tmp_grid_1_way in grid_1_way_list:
            tmp_1_way_attribute = tmp_grid_1_way.attribute_set[0]
            tmp_1_way_attribute_index = grid_2_way.attribute_set.index(tmp_1_way_attribute)
            for i in range(len(tmp_grid_1_way.cell_list)):
                tmp_cell = tmp_grid_1_way.cell_list[i]
                lower_bound = tmp_cell.left_interval_list[0]
                upper_bound = tmp_cell.right_interval_list[0] + 1
                if tmp_1_way_attribute_index == 0:
                    tmp_sum = np.sum(grid_2_way.weighted_update_matrix[lower_bound:upper_bound, :])
                    if tmp_sum == 0:
                        continue
                    grid_2_way.weighted_update_matrix[lower_bound:upper_bound, :] = grid_2_way.weighted_update_matrix[lower_bound:upper_bound, :] / tmp_sum * tmp_cell.consistent_count
                else:
                    tmp_sum = np.sum(grid_2_way.weighted_update_matrix[:, lower_bound:upper_bound])
                    if tmp_sum == 0:
                        continue
                    grid_2_way.weighted_update_matrix[:, lower_bound:upper_bound] = grid_2_way.weighted_update_matrix[:, lower_bound:upper_bound] / tmp_sum * tmp_cell.consistent_count
                # normalization
                grid_2_way.weighted_update_matrix = grid_2_way.weighted_update_matrix / np.sum(grid_2_way.weighted_update_matrix) * self.args.user_num
        # update using 2_way
        for tmp_cell in grid_2_way.cell_list:
            x_lower_bound = tmp_cell.left_interval_list[0]
            x_upper_bound = tmp_cell.right_interval_list[0] + 1
            y_lower_bound = tmp_cell.left_interval_list[1]
            y_upper_bound = tmp_cell.right_interval_list[1] + 1
            tmp_sum = np.sum(grid_2_way.weighted_update_matrix[x_lower_bound:x_upper_bound, y_lower_bound:y_upper_bound])
            if tmp_sum == 0:
                continue
            grid_2_way.weighted_update_matrix[x_lower_bound:x_upper_bound, y_lower_bound:y_upper_bound] = grid_2_way.weighted_update_matrix[x_lower_bound:x_upper_bound, \
                                                                                                          y_lower_bound:y_upper_bound] / tmp_sum * tmp_cell.consistent_count
            # normalization
            grid_2_way.weighted_update_matrix = grid_2_way.weighted_update_matrix / np.sum(grid_2_way.weighted_update_matrix) * self.args.user_num

        return

    def get_weight_update_for_2_way_group(self):
        for tmp_grid in self.Grid_set:
            if len(tmp_grid.attribute_set) == 2:
                grid_1_way_list = []
                for tmp_grid_1_way in self.Grid_set:
                    if len(tmp_grid_1_way.attribute_set) == 1 and tmp_grid_1_way.attribute_set[0] in tmp_grid.attribute_set:
                        grid_1_way_list.append(tmp_grid_1_way)
                tmp_grid.weighted_update_matrix = np.zeros((self.args.domain_size, self.args.domain_size))
                # initialize
                tmp_grid.weighted_update_matrix[:,:] = self.args.user_num / (self.args.domain_size * self.args.domain_size)

                for i in range(self.args.weighted_update_iteration_num_max):
                    weighted_update_matrix_before = np.copy(tmp_grid.weighted_update_matrix)
                    self.weighted_update_iteration(grid_1_way_list, tmp_grid)
                    weighted_update_matrix_delta = np.sum(np.abs(tmp_grid.weighted_update_matrix - weighted_update_matrix_before))
                    if weighted_update_matrix_delta < 1:
                        break
        return


    def generate_attribute_group(self):
        attribute_group_list = []
        attribute_list = [i for i in range(self.args.attribute_num)]
        for tmp_attribute in attribute_list:
            attribute_group_list.append((tmp_attribute,))
        attribute_group_2_way_list = list(itertools.combinations(attribute_list, self.group_attribute_num))
        for tmp_attribute_group_2_way in attribute_group_2_way_list:
            attribute_group_list.append(tmp_attribute_group_2_way)
        self.group_num = len(attribute_group_list)
        self.args.group_num = self.group_num
        self.AG = attribute_group_list
        for i in range(len(self.AG)):
            self.AG[i] = list(self.AG[i])

    def group_attribute(self):
        self.generate_attribute_group()
        return


    def construct_Grid_set(self):
        for i in range(self.group_num):
            if len(self.AG[i]) == 1:
                tmp_Grid = GridGen.UniformGrid(self.AG[i], granularity= self.granularity_1_way, args= self.args)
            else:
                tmp_Grid =  GridGen.UniformGrid(self.AG[i], granularity= self.granularity, args= self.args)
            tmp_Grid.Grid_index = i
            tmp_Grid.Main()
            self.Grid_set.append(tmp_Grid)
        return

    def get_user_record_in_attribute_group(self, user_record_i, attribute_group: int = None):
        user_record_in_attribute_group = []
        for tmp in self.AG[attribute_group]:
            user_record_in_attribute_group.append(user_record_i[tmp])
        return user_record_in_attribute_group


    def get_LDP_Grid_set_divide_user(self, user_record):
        print("HDG is working...")

        self.LDP_mechanism_list_divide_user = [] # intialize for each time to randomize user data
        for j in range(self.group_num): # initialize LDP mechanism for each attribute group
            tmp_Grid = self.Grid_set[j]  # the i-th Grid
            tmp_domain_size = len(tmp_Grid.cell_list)

            tmp_LDR = FreOra.OUE(domain_size=tmp_domain_size, epsilon= self.args.epsilon, sampling_factor=self.group_num, args=self.args)
            # tmp_LDR = FreOra.OLH(domain_size=tmp_domain_size, epsilon= self.args.epsilon, sampling_factor=self.group_num, args=self.args)

            self.LDP_mechanism_list_divide_user.append(tmp_LDR)

        for i in range(self.args.user_num):
            tmp_user_granularity = math.ceil(self.args.user_num / self.group_num)
            group_index_of_user = i // tmp_user_granularity
            j = group_index_of_user

            # to count the user num of each group
            self.LDP_mechanism_list_divide_user[j].group_user_num += 1
            tmp_Grid = self.Grid_set[j]
            user_record_in_attribute_group_j = self.get_user_record_in_attribute_group(user_record[i], j)
            tmp_real_cell_index = tmp_Grid.get_cell_index_from_attribute_value_set(user_record_in_attribute_group_j)
            tmp_LDP_mechanism = self.LDP_mechanism_list_divide_user[j]
            tmp_LDP_mechanism.operation_perturb(tmp_real_cell_index)

        # update the perturbed_count of each cell
        for j in range(self.group_num):
            tmp_LDP_mechanism = self.LDP_mechanism_list_divide_user[j]
            tmp_LDP_mechanism.operation_aggregate()
            tmp_Grid = self.Grid_set[j]  # the j-th Grid
            for k in range(len(tmp_Grid.cell_list)):
                tmp_Grid.cell_list[k].perturbed_count = tmp_LDP_mechanism.aggregated_count[k]
        return

    def judge_sub_attribute_list_in_attribute_group(self, sub_attribute_list, attribute_group):
        if len(sub_attribute_list) == 1:
            return False
        flag = True
        for sub_attribute in sub_attribute_list:
            if sub_attribute not in attribute_group:
                flag = False
                break
        return flag

    def get_answer_range_query_attribute_group_list(self, selected_attribute_list):
        answer_range_query_attribute_group_index_list = []
        answer_range_query_attribute_group_list = []
        for tmp_Grid in self.Grid_set:
            #note that here we judge if tmp_Grid.attribute_set belongs to selected_attribute_list
            if self.judge_sub_attribute_list_in_attribute_group(tmp_Grid.attribute_set, selected_attribute_list):
                answer_range_query_attribute_group_index_list.append(tmp_Grid.Grid_index)
                answer_range_query_attribute_group_list.append(tmp_Grid.attribute_set)

        return answer_range_query_attribute_group_index_list, answer_range_query_attribute_group_list


    def answer_range_query(self, range_query):
        t_Grid_ans = []
        answer_range_query_attribute_group_index_list, answer_range_query_attribute_group_list = \
        self.get_answer_range_query_attribute_group_list(range_query.selected_attribute_list)

        for k in answer_range_query_attribute_group_index_list:
            tmp_Grid = self.Grid_set[k]
            Grid_range_query_attribute_node_list = []
            for tmp_attribute in tmp_Grid.attribute_set:
                Grid_range_query_attribute_node_list.append(range_query.query_attribute_node_list[tmp_attribute])
            t_Grid_ans.append(tmp_Grid.answer_range_query_with_weight_update_matrix(Grid_range_query_attribute_node_list))

        if range_query.query_dimension == self.group_attribute_num: # answer the 2-way marginal
            tans_weighted_update = t_Grid_ans[0]
        else:
            tt = EstMeth.EsimateMethod(args= self.args)
            tans_weighted_update = tt.weighted_update(range_query, answer_range_query_attribute_group_list, t_Grid_ans)

        return tans_weighted_update



    def answer_range_query_list(self, range_query_list):
        self.weighted_update_answer_list = []
        for tmp_range_query in range_query_list:
            tans_weighted_update = self.answer_range_query(tmp_range_query)
            self.weighted_update_answer_list.append(tans_weighted_update)
        return


