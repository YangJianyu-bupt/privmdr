import numpy as np

class EsimateMethod:
    def __init__(self, args = None):
        self.args = args

    def weighted_update(self, range_query = None, attribute_group = None, attribute_group_ans = None):
        # get dict of range_query.selected_attribute_list
        query_selected_attribute_dict = dict()
        for i in range(len(range_query.selected_attribute_list)):
            tmp_attribute = range_query.selected_attribute_list[i]
            query_selected_attribute_dict[tmp_attribute] = i
        dim_list = []
        for i in range(range_query.query_dimension):
            dim_list.append(2) # always 2, since using 2-D query answer to estimate higher dimensional query
        dim_tuple = tuple(dim_list)
        tmp_weighted_update_matrix = np.zeros(dim_tuple)
        tmp_slice_whole = ''
        for i in range(range_query.query_dimension):
            tmp_slice_whole += ':'
            if i < range_query.query_dimension - 1:
                tmp_slice_whole += ','
        sentence_init_whole = 'tmp_weighted_update_matrix[' + tmp_slice_whole + '] = self.args.user_num / tmp_weighted_update_matrix.size'
        exec(sentence_init_whole)

        def local_update_weighted_update_matrix(tmp_weighted_update_matrix, tmp_attribute_group, \
                                                tmp_attribute_group_ans, tmp_query_dimension, tmp_selected_attribute_list:list):
            tmp_slice_update_symbol = []
            for i in range(tmp_query_dimension):
                tmp_slice_update_symbol.append(':')
            for tmp_attribute in tmp_attribute_group:
                # for answering query attribute from all attributes, not only the first query_select_num attribute
                tmp_slice_update_symbol[tmp_selected_attribute_list.index(tmp_attribute)] = '0'

            tmp_slice_update = ''
            for i in range(tmp_query_dimension):
                tmp_slice_update += tmp_slice_update_symbol[i]
                if i < tmp_query_dimension - 1:
                    tmp_slice_update += ','

            sentence_t_martrix_in_locals = 't_matrix_in_locals = tmp_weighted_update_matrix[' + tmp_slice_update + ']'
            exec(sentence_t_martrix_in_locals)
            t_matrix = locals()['t_matrix_in_locals']
            tmp_sum = np.sum(t_matrix)

            if tmp_sum == 0:
                pass
            else:
                t_matrix = t_matrix / tmp_sum * tmp_attribute_group_ans
                sentence_tmp_weighted_update_matrix = 'tmp_weighted_update_matrix[' + tmp_slice_update + '] = t_matrix'
                exec(sentence_tmp_weighted_update_matrix)
            return

        max_iteration_num = self.args.weighted_update_iteration_num_max
        for i in range(max_iteration_num):
            weighted_update_matrix_before = np.copy(tmp_weighted_update_matrix)
            for j in range(len(attribute_group)):
                tmp_attribute_group = attribute_group[j]
                tmp_attribute_group_ans = attribute_group_ans[j]
                local_update_weighted_update_matrix(tmp_weighted_update_matrix, tmp_attribute_group, \
                                                    tmp_attribute_group_ans, range_query.query_dimension, range_query.selected_attribute_list)
                tmp_weighted_update_matrix = tmp_weighted_update_matrix / np.sum(tmp_weighted_update_matrix) * self.args.user_num
            weighted_update_matrix_delta = np.sum(np.abs(tmp_weighted_update_matrix - weighted_update_matrix_before))
            if weighted_update_matrix_delta < 1:
                break

        tmp_slice_ans_list = []
        for i in range(range_query.query_dimension):
            tmp_slice_ans_list.append(0)
        tmp_slice_ans_tuple = tuple(tmp_slice_ans_list)
        ans = tmp_weighted_update_matrix[tmp_slice_ans_tuple]

        return ans


