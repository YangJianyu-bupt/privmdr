import numpy as np
import utility_metric as UM
import generate_query as GenQuery
import random
import TDG
import HDG
import parameter_setting as para


def setup_args(args = None):
    args.algorithm_name = 'TDG'
    # args.algorithm_name = 'HDG'

    args.user_num = 1000000
    args.attribute_num = 6
    args.domain_size = 64

    args.epsilon = 0.2

    args.dimension_query_volume = 0.5
    args.query_num = 20
    args.query_dimension = 3


def load_dataset(txt_dataset_path = None):
    user_record = []
    with open(txt_dataset_path, "r") as fr:
        i = 0
        for line in fr:
            line = line.strip()
            line = line.split()
            user_record.append(list(map(int, line)))
            i += 1
    return user_record



def sys_test():

    txt_dataset_path = "test_dataset/laplace2_dataset_users_1000000_attributes_6_domain_64.txt"

    args = para.generate_args() # define the parameters
    setup_args(args= args) # setup the parameters

    user_record = load_dataset(txt_dataset_path= txt_dataset_path) # read user data

    # generate range query****************************************************************

    random_seed = 1
    random.seed(random_seed)
    np.random.seed(seed=random_seed)

    range_query = GenQuery.RangeQueryList(query_dimension=args.query_dimension,
                                          attribute_num=args.attribute_num,
                                          query_num=args.query_num,
                                          dimension_query_volume=args.dimension_query_volume, args=args)

    range_query.generate_range_query_list()
    range_query.generate_real_answer_list(user_record)

    txt_file_path = "test_output/range_query.txt" # print the generated range queries
    with open(txt_file_path, "w") as txt_fr_out:
        range_query.print_range_query_list(txt_fr_out)


    #invoke TDG or HDG ****************************************************************
    np.random.shuffle(user_record)

    if args.algorithm_name == 'TDG':
        aa = TDG.AG_Uniform_Grid_optimal(args=args)
    elif args.algorithm_name == "HDG":
        aa = HDG.AG_Uniform_Grid_1_2_way_optimal(args=args)

    aa.group_attribute()
    aa.construct_Grid_set()
    aa.get_LDP_Grid_set_divide_user(user_record)
    aa.get_consistent_Grid_set()

    if args.algorithm_name == 'HDG':
        aa.get_weight_update_for_2_way_group()

    aa.answer_range_query_list(range_query.range_query_list)

    #calculate MAE ****************************************************************
    bb = UM.UtilityMetric(args=args)
    MAE = bb.MAE(range_query.real_answer_list, aa.weighted_update_answer_list)

    print("MAE:", MAE)



if __name__ == '__main__':
    sys_test()
