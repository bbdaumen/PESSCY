from sys import argv
from pickle import dump
from random import randint
from itertools import product
from collections import defaultdict
from json import load
"""

The matrices for the experiments have been fixed to the related permutation. It may be found in the documentation.

"""

def generate_set_of_parameters(json_file:str, permutation:str, version:str):

    """Generate all the parameters dictionnaries
    
    :param json_file: JSON file with the description of the parameters for the benchmark
    :type json_file: str
    :param permutation: Permutation/modelling name
    :type permutation: str
    :param version: Version of the tool
    :type version: str
    """

    try:
        with open(json_file) as inputs_file:
            inputs = load(inputs_file)
            inputs_file.close()
    except FileNotFoundError as e:
        print(e)

    """

        The order of the for loops are important. Indeed, the set of experiments must be sorted such that smaller number of rounds and branches are treated first for a fix range of parameters.
        
        Experiments that follow experiments that timed out may be skipped.

    """

    id = 1
    
    parameters = []

    number_of_parameters_by_thread_list = []

    seed = randint(1, 10**15)
 
    for field_char in inputs["field_chars"]:

        for monomial_order in inputs["monomial_orders"]:

            sparsities = defaultdict(list)
            for k, v in inputs["branches"].items():
                for sparsity in v:
                    sparsities[sparsity].append(k)

            for sparsity in sparsities.keys():
                branches = sparsities[sparsity]
                
                for cico, rounds in inputs["cicos"].items():

                    pairs = list(product(branches, rounds))
                    pairs_sorted = sorted(pairs, key=lambda x: int(x[0]) + int(x[1]))

                    elimination_order = 0
                    eliminate_giac = 0
                    eliminate_libsingular = 0

                    for algo_order_change in inputs["algos_order_change"]:

                        if (monomial_order == "invlex" or monomial_order == "lex") and elimination_order == 1: ### If the order is an elimination order then, we don't use the term order change algorithm so we only have to pass once
                            break

                        elimination_order +=1

                        for algo_gb in inputs["algos_gb"]:

                            if algo_gb.startswith("eliminate:giac") and eliminate_giac > 1:
                                continue
                                
                            eliminate_giac += 1

                            if algo_gb.startswith("eliminate:libsingular") and eliminate_libsingular > 1:

                                continue
                                
                            eliminate_libsingular += 1

                            options = []

                            if algo_gb == 'msolve' and monomial_order != 'degrevlex':
                                continue

                            if algo_gb in inputs["options"].keys():
                                options = inputs["options"][algo_gb]                              

                            if options == []:

                                actual_pair = 0
                                    
                                for branch, round in pairs_sorted:

                                    if int(cico) <= int(branch)-1:

                                        if (monomial_order == "invlex" or monomial_order == "lex" or algo_gb.startswith("eliminate:giac") or algo_gb.startswith("eliminate:libsingular")): ### We don't need the algo_order_change

                                            parameters.append({"version" : version, "id" : id, "permutation" : permutation, "algo_gb" : algo_gb, "options" : None, "algo_order_change" : None, "field_char": field_char, "monomial_order" : monomial_order, "round" : round, "cico" : int(cico), "branch" : int(branch), "number_test" : inputs["number_test"], "constant_sparsity" : sparsity, "seed" : seed})

                                        else:

                                            parameters.append({"version" : version, "id" : id, "permutation" : permutation, "algo_gb" : algo_gb, "options" : None, "algo_order_change" : algo_order_change, "field_char": field_char, "monomial_order" : monomial_order, "round" : round, "cico" : int(cico), "branch" : int(branch), "number_test" : inputs["number_test"], "constant_sparsity" : sparsity, "seed" : seed})
                                        
                                        print(parameters[-1], "\n", flush=True)
                                        id +=1

                                        actual_pair +=1

                                number_of_parameters_by_thread_list.append(actual_pair)

                            else:
                                
                                for option in options:
                                     
                                    actual_pair = 0
                                            
                                    for branch, round in pairs_sorted:

                                        if int(cico) <= int(branch)-1:   

                                            if (monomial_order == "invlex" or monomial_order == "lex" or algo_gb.startswith("eliminate:giac") or algo_gb.startswith("eliminate:libsingular")): ### We don't need the algo_order_change

                                                parameters.append({"version" : version, "id" : id, "permutation" : permutation, "algo_gb" : algo_gb, "options" : option, "algo_order_change" : None, "field_char": field_char, "monomial_order" : monomial_order, "round" : round, "cico" : int(cico), "branch" : int(branch), "number_test" : inputs["number_test"], "constant_sparsity" : sparsity, "seed" : seed})

                                            else:

                                                parameters.append({"version" : version, "id" : id, "permutation" : permutation, "algo_gb" : algo_gb, "options" : option, "algo_order_change" : algo_order_change, "field_char": field_char, "monomial_order" : monomial_order, "round" : round, "cico" : int(cico), "branch" : int(branch), "number_test" : inputs["number_test"], "constant_sparsity" : sparsity, "seed" : seed})
                                            print(parameters[-1], "\n", flush=True)
                                            id +=1

                                            actual_pair +=1

                                    number_of_parameters_by_thread_list.append(actual_pair)

    return parameters, number_of_parameters_by_thread_list
    

if __name__ == "__main__":

    folder_results = argv[1]
    json_file = argv[2]
    permutation = argv[3]
    version = argv[4]

    """
        Generate all the sets of parameters for the experiments. Moreover, return the list of number of experiments to treat after the first ID. The following IDs (up to the next one in the list) have the same parameters except the number of branches and rounds.
    """

    parameters, number_of_parameters_by_thread_list = generate_set_of_parameters(json_file, permutation, version)

    """
        Write the list of number of parameters by thread to treat and all the parameters set in the parameters.pkl file.
    """

    with open(folder_results+"/parameters.pkl", 'wb') as f_param_pkl:

        dump(number_of_parameters_by_thread_list, f_param_pkl)

        id = 1
        for parameter in parameters:
            dump(parameter, f_param_pkl)
            f_param_pkl.flush()
            id += 1

    """
        The first ID of each list of parameter to treat are written in decreasing order in the ids.txt file.
    """

    first_id = id

    with open(folder_results+"/ids.txt", 'w') as f_id:

        for nb_param in reversed(number_of_parameters_by_thread_list):
            first_id -= nb_param
            f_id.write(str(first_id)+"\n")
            f_id.flush()