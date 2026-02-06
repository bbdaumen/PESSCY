from pickle import load, dump
from os import makedirs
from os.path import exists
from sys import argv

def get_parameters(folder_results:str):

    """
    Return the list of dictionnaries corresponding to parameters of the experiments
    
    :param folder_results: Folder with the results
    :type folder_results: str
    """
    parameters = []
    with open(folder_results + "/parameters.pkl", "rb") as f_pkl:
        while True :
            try:
                data = load(f_pkl)
                parameters.append(data)
            except EOFError:
                break
    return parameters

def get_experiment_result(filename:str):

    """
    Reults of an experiment
    
    :param filename: Name of the file
    :type filename: str
    """

    with open(filename, "rb") as f_pkl:
        try:
            data = load(f_pkl)
        except EOFError:
            print("Cannot read data")
            data = None
    return data

def generate_random_comparison_parameters(results_primitives_to_compare:str, parameters:list, number_test:int):

    """
    Generate the list of the paramaters fro the random comparisons
    
    :param results_primitives_to_compare: Folder with the results to compare
    :type results_primitives_to_compare: str
    :param parameters: List of parameters of the experiments to compare
    :type parameters: list
    :param number_test: Number of comparisons to do per experiment
    :type number_test: int
    """

    random_parameters = []

    for parameter in parameters[1:]:

        id = parameter["id"]
        filename = results_primitives_to_compare + str(id) + ".pkl"

        """
            If there is no result for this ID of experiment then the comparison has to be skipped. It is specified by giving to the algo_gb key, the value skipped.
        """

        if not exists(filename):
            random_parameters.append({"version": parameter["version"], "id" : id, "permutation" : "random", "algo_gb" : "skipped"})
    
        else:

            try :

                data = get_experiment_result(filename)

                shape_system = data["system_of_equation_shape"]

                """
                    The goal is to compare the equations with random ideals of the same structure. The same maximal degree, variables and number of monomials.
                """

                if data["groebner_time"] != "failed" and data["groebner_time"] != "skipped" and data["groebner_time"] != "timeout":
                    random_parameters.append({"version": parameter["version"], "id" : id, "permutation" : "random", "algo_gb" : parameter["algo_gb"], "options" : parameter["options"], "algo_order_change" : parameter["algo_order_change"], "field_char": parameter["field_char"], "monomial_order" : parameter["monomial_order"], "number_test" : number_test, "seed" : parameter["seed"], "monomials_degree_variables_vector" : shape_system})

                    """
                        If the Gröbner basis computation has failed, timed out or been skipped for this ID of experiment then the comparison has to be skipped. It is specified by giving to the algo_gb key, the value skipped.
                    """

                else:
                    random_parameters.append({"version": parameter["version"], "id" : id, "permutation" : "random", "algo_gb" : "skipped", "number_test" : number_test})

            except Exception as e :
                print("Cannot read file {}".format(id))
                print(e)
                random_parameters.append({"version": parameter["version"], "id" : id, "permutation" : "random", "algo_gb" : "skipped", "number_test" : number_test})

    last_id = id

    return random_parameters, last_id

if __name__ == "__main__":

    folder_to_compare = argv[1] 
    folder_results = argv[2]
    number_test = int(argv[3])

    if not exists(folder_results):
        makedirs(folder_results)

    results_primitives_to_compare = f"./{folder_to_compare}/res/"

    """
        Return the full list of parameters of the experiments we want to compare
    """
    parameters = get_parameters(folder_to_compare)
    parameters_by_thread_list = parameters[0]

    """
        Generate the parameters for random ideals. 
    """

    random_parameters, last_id = generate_random_comparison_parameters(results_primitives_to_compare, parameters, number_test)

    """
        Write the list of parameters in the parameters.pkl file. Reuse the list of number of experiments to do per thread used in the primitives experiments.
    """

    with open("./"+folder_results+"/parameters.pkl", 'wb') as f_param_pkl:

        dump(parameters_by_thread_list, f_param_pkl)

        for parameter in random_parameters:
            dump(parameter, f_param_pkl)
            f_param_pkl.flush()

    """
        Write the first ID of experiments in the ids.txt file.
    """

    first_id = last_id + 1

    with open("./"+folder_results+"/ids.txt", 'w') as f_id:
        for nb_param in reversed(parameters_by_thread_list):
            first_id -= nb_param
            f_id.write(str(first_id)+"\n")
            f_id.flush()