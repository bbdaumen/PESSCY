from sys import argv
from pickle import load
from benchmark.algebraic_attack_benchmark import ExperimentRecord
from utils.utils_all import redirect_all_output

def perform_experiments(folder_results:str, parameters:list[dict], system_generation_timeout:float, full_computation_timeout:float):

    """ Perform the list of experiments in parameters.

    This list contains experiments with the same parameter for the permutation except the number of branches or rounds. The time to perform an algebraic attack increases with these variables. Then, we use a forbidden zone that contains timed out experiments. If an experiment is treated with a higher number of rounds or branches than one from the forbidden zone then it is immediatly skipped as we know it will we be timed out.

    :param folder_results: folder with the results of the benchmark
    :type folder_results: str
    :param parameters: list of dictionnaries of parameters to treat
    :type parameters: list[dict]
    :param system_generation_timeout: Timeout for the generation of the system
    :type system_generation_timeout: float
    :param full_computation_timeout: Timeout for the algebraic attack
    :type full_computation_timeout: float
    """

    forbidden_zone = []
 
    for parameter in parameters:

        log_path = f"./{folder_results}/logs/{parameter['id']}.log"
        redirect_all_output(log_path)
        print("Parameters are", parameter, flush=True)

        experimentation_to_do = True

        """ Check whether the current experiment is in the forbidden zone
        """

        for element in forbidden_zone:
            if (parameter["branch"] >= element[0]) and (parameter["round"] >= element[1]):
                experimentation_to_do = False
                break

        experiment = ExperimentRecord(folder_results, id = parameter["id"], algo_gb = parameter["algo_gb"], options = parameter["options"], algo_order_change = parameter["algo_order_change"], field_size = parameter["field_char"], monomial_order = parameter["monomial_order"], permutation = parameter["permutation"], cico = parameter["cico"], round = parameter["round"], number_test = parameter["number_test"], branch = parameter["branch"], seed=parameter["seed"], constant_sparsity = parameter["constant_sparsity"])   

        if experimentation_to_do:

            add_to_forbidden_zone = experiment.solve_systems(system_generation_timeout, full_computation_timeout)

            if add_to_forbidden_zone:
                forbidden_zone.append((parameter["branch"], parameter["round"]))

        else:
            
            """
                The experiment is not performed but we compute the structure of the system to output it.
            """
            _ = experiment.generate_systems(system_generation_timeout, "skipped")


if __name__ == "__main__":

    folder_results = argv[1]
    parameter_first_id = int(argv[2]) ## First ID parameter to treat
    system_generation_timeout = float(argv[3])
    full_computation_timeout = float(argv[4])

    with open("./"+folder_results+"/parameters.pkl", 'rb') as f_pkl:

        """
            Get the number of parameters to treat starting to the first ID: parameter_first_id
        """

        parameters_by_thread_list = load(f_pkl)

        for j in range(len(parameters_by_thread_list)):
            if sum(parameters_by_thread_list[:j]) + 1 == parameter_first_id:
                index = j
                break

        parameters = []
        i = 0
        while i != parameter_first_id:
            i += 1
            first_set_parameters_to_treat = load(f_pkl)
        
        """
            Check we get the good first set of parameters
        """

        parameters.append(first_set_parameters_to_treat)
        assert parameters[0]["id"] == parameter_first_id

        """
            Read and store the next set of parameters
        """

        for _ in range(parameters_by_thread_list[index]-1):
            parameters.append(load(f_pkl))

    """
        Perform the experiments of the parameters list
    """

    perform_experiments(folder_results, parameters, system_generation_timeout, full_computation_timeout)