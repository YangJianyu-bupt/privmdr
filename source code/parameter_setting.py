import argparse

def generate_args(): # intialize paprameters
    parser = argparse.ArgumentParser()

    # int type
    parser.add_argument("--user_num", type=int, default= 50000, help="the number of users")
    parser.add_argument("--attribute_num", type=int, default= 8, help="the number of attributes")
    parser.add_argument("--domain_size", type=int, default=16, help="the domain size of each attribute")
    parser.add_argument("--query_num", type=int, default=10, help= "the number of queries")
    parser.add_argument("--query_dimension", type=int, default=3, help= "the query dimension")
    parser.add_argument("--consistency_iteration_num_max", type=int, default=100, help="the maximum number of iterations in consitency operation")
    parser.add_argument("--weighted_update_iteration_num_max", type=int, default=100, help="the maximum number of iterations in weighted update process")

    # float type
    parser.add_argument("--epsilon", type=float, default=1.0, help= "the privacy budget")
    parser.add_argument("--dimension_query_volume", type=float, default=0.5, help="the dimensional query volume")

    # str type
    parser.add_argument("--algorithm_name", type=str, default="", help="choose the algorithm: TDG or HDG")

    args = parser.parse_args()
    return args

