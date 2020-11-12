import math
import grid_generate as GridGen
import estimate_method as EstMeth
import frequency_oracle as FreOra
import itertools
import choose_granularity

class AG_Uniform_Grid_optimal:
    def __init__(self, args = None):
        self.args = args
        self.group_attribute_num = 2 # to construct 2-D grids
        self.group_num = 0
        self.AG = []  # attribute_group
        self.Grid_set = [] # note that this is different from the HDRtree
        self.output_file_name = None
        self.answer_list = []
        self.weighted_update_answer_list = []
        self.LDP_mechanism_list_divide_user = [] # LDP mechanism for each attribute group

        self.set_granularity()

    def set_granularity(self):
        chooseGran = choose_granularity.choose_granularity_beta(args= self.args)
        tmp_g2 = chooseGran.get_2_way_granularity_for_TDG(ep=self.args.epsilon)
        self.granularity = chooseGran.get_rounding_to_pow_2(gran= tmp_g2)
        self.args.granularity = self.granularity


    def judge_sub_attribute_in_attribute_group(self, sub_attribute = None, attribute_group:list = None):
        if sub_attribute in attribute_group:
            return True
        else:
            return False

    def get_T_A_a(self, sub_attribute_value = None, sub_attribute = None, relevent_attribute_group_list:list = None):
        sum_T_V_i_a = 0
        j = len(relevent_attribute_group_list)
        for i in relevent_attribute_group_list:
            T_V_i_a = 0
            tmp_grid = self.Grid_set[i]
            sub_attribute_index_in_grid = tmp_grid.attribute_set.index(sub_attribute)
            for tmp_cell in tmp_grid.cell_list:
                if tmp_cell.dimension_index_list[sub_attribute_index_in_grid] == sub_attribute_value:
                    T_V_i_a += tmp_cell.consistent_count
            sum_T_V_i_a += T_V_i_a

        T_A_a = sum_T_V_i_a / j
        return T_A_a



    def get_consistency_for_sub_attribute(self, sub_attribute = None):

        relevent_attribute_group_list = []
        for i in range(self.group_num):
            if self.judge_sub_attribute_in_attribute_group(sub_attribute, self.AG[i]):
                relevent_attribute_group_list.append(i)

        sub_attribute_domain = range(self.args.granularity) # need to be changed for 3-way attribute group
        for sub_attribute_value in sub_attribute_domain:
            T_A_a = self.get_T_A_a(sub_attribute_value, sub_attribute, relevent_attribute_group_list)

            #update T_V_i_c
            for i in relevent_attribute_group_list:
                tmp_grid = self.Grid_set[i]
                sub_attribute_index_in_grid = tmp_grid.attribute_set.index(sub_attribute)
                T_V_i_a = 0
                T_V_i_c_cell_list = []
                for k in range(len(tmp_grid.cell_list)):
                    tmp_cell = tmp_grid.cell_list[k]
                    if tmp_cell.dimension_index_list[sub_attribute_index_in_grid] == sub_attribute_value:
                        T_V_i_c_cell_list.append(k)
                        T_V_i_a += tmp_cell.consistent_count

                for k in T_V_i_c_cell_list:
                    tmp_cell = tmp_grid.cell_list[k]
                    tmp_cell.consistent_count = tmp_cell.consistent_count + (T_A_a - T_V_i_a) / len(T_V_i_c_cell_list)
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

        # end with Non-Negativity Step
        for tmp_grid in self.Grid_set:
            tmp_grid.get_consistent_grid_iteration()
        return


    def generate_attribute_group(self):
        attribute_list = [i for i in range(self.args.attribute_num)]
        attribute_group_list = list(itertools.combinations(attribute_list, self.group_attribute_num))
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

        print("TDG is working...")

        self.LDP_mechanism_list_divide_user = [] # intialize for each time to randomize user data

        for j in range(self.group_num): # initialize LDP mechanism for each attribute group
            tmp_Grid = self.Grid_set[j]
            tmp_domain_size = len(tmp_Grid.cell_list)

            tmp_LDR = FreOra.OUE(domain_size=tmp_domain_size, epsilon= self.args.epsilon, sampling_factor=self.group_num, args=self.args)
            # tmp_LDR = FreOra.OLH(domain_size=tmp_domain_size, epsilon= self.args.epsilon, sampling_factor=self.group_num, args=self.args)

            self.LDP_mechanism_list_divide_user.append(tmp_LDR)

        for i in range(self.args.user_num):

            tmp_user_granularity = math.ceil(self.args.user_num / self.group_num)
            group_index_of_user = i // tmp_user_granularity
            j = group_index_of_user

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
            tmp_Grid = self.Grid_set[j]
            for k in range(len(tmp_Grid.cell_list)):
                tmp_Grid.cell_list[k].perturbed_count = tmp_LDP_mechanism.aggregated_count[k]
        return

    def judge_sub_attribute_list_in_attribute_group(self, sub_attribute_list, attribute_group):
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


    def answer_range_query(self, range_query, private_flag = 0):
        t_Grid_ans = []
        answer_range_query_attribute_group_index_list, answer_range_query_attribute_group_list = \
        self.get_answer_range_query_attribute_group_list(range_query.selected_attribute_list)
        for k in answer_range_query_attribute_group_index_list:
            tmp_Grid = self.Grid_set[k]
            Grid_range_query_attribute_node_list = []
            for tmp_attribute in tmp_Grid.attribute_set:
                Grid_range_query_attribute_node_list.append(range_query.query_attribute_node_list[tmp_attribute])
            t_Grid_ans.append(tmp_Grid.answer_range_query(Grid_range_query_attribute_node_list))

        if range_query.query_dimension == self.group_attribute_num: # answer the 1-way2-way marginal
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

