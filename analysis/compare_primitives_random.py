from sys import exit
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Button

from utils.analysis import read_pickle_parameters, dict_keys_equal_except_keys_specified, read_pickle_experiment, to_list_info, all_inf_lowerbound, all_none, statistics_analysis, statistics_analysis_no_log, first_monomial_order_plus_transformation_statistics_analysis, ALGOS_COLOR, ALGOS_MARKER, NAMES_NICE_PRINTING

STOP_REQUESTED = False
LOWERBOUND = -2

def stop(event):
    global STOP_REQUESTED
    STOP_REQUESTED = True
    plt.close('all')

def compare_solving_methods(folder_results_primitive:str, folder_results_random:str, variable_parameter:str):

    """
    Display the evolution of the time to compute a Gröbner basis for the elimination order, the first order and the term order change + the first order depending on a parameter. It is done for the primitive and the random ideal (dotted line)

    :param folder_results_primitive: Folder containing the results file of the primitive benchmark
    :type folder_results_primitive: str
    :param folder_results_random: Folder containing the results of the comparison with random ideals
    :type folder_results_random: str
    :param variable_parameter: The parameter we want to see the influence
    :type variable_parameter: str
        
    """

    parameters = read_pickle_parameters(folder_results_primitive)[1:]

    parameters_treated = []

    keys_to_ignore=["id", variable_parameter, "seed"]  ## Keys we ignore as we don"t compare them (they may be different)
    keys_to_ignore_elimination=["id", variable_parameter, "seed", "algo_order_change", "monomial_order"]

    for parameter in parameters:

        if not parameter in parameters_treated: ## Check if the parameter has not been treated before

            parameters_treated.append(parameter)

            parameters_used = [parameter]

            for parameter_compared in parameters: ## The list of parameters that are going to displayed

                if dict_keys_equal_except_keys_specified(parameter, parameter_compared, keys_to_ignore) and parameter_compared != parameter:

                    parameters_treated.append(parameter_compared)
                    parameters_used.append(parameter_compared)

                if dict_keys_equal_except_keys_specified(parameter, parameter_compared, keys_to_ignore_elimination) and parameter_compared != parameter and parameter_compared["algo_order_change"] is None and not parameter_compared in parameters_used:

                    parameters_treated.append(parameter_compared)
                    parameters_used.append(parameter_compared)

            ### x-axis

            x = []
            x_elimination = []

            ### Primitives

            first_monomial_order_primitive = []
            first_monomial_order_primitive_ecart_type = []
            first_monomial_order_primitive_info = []

            transformation_primitive = []
            transformation_primitive_ecart_type = []
            transformation_primitive_info = []

            first_monomial_order_plus_transformation_primitive = []
            first_monomial_order_plus_transformation_primitive_ecart_type = []

            elimination_primitive = []
            elimination_primitive_ecart_type = []
            elimination_primitive_info = []

            ideal_degree_list_primitive = []
            ideal_degree_list_primitive_ecart_type = []

            ideal_degree_theory = []
            

            solving_degree_list_primitive = []
            solving_degree_list_primitive_ecart_type = []

            solving_degree_theory = []
            
            ### Random

            first_monomial_order_random = []
            first_monomial_order_random_ecart_type = []
            first_monomial_order_random_info = []
            
            transformation_random = []
            transformation_random_ecart_type = []
            transformation_random_info = []

            first_monomial_order_plus_transformation_random = []
            first_monomial_order_plus_transformation_random_ecart_type = []

            elimination_random = []
            elimination_random_ecart_type = []
            elimination_random_info = []

            ideal_degree_list_random = []
            ideal_degree_list_random_ecart_type = []

            solving_degree_list_random = []
            solving_degree_list_random_ecart_type = []

            for parameter_used in parameters_used:

                if STOP_REQUESTED:
                    exit(0)

                data_primitive = read_pickle_experiment(folder_results_primitive, parameter_used["id"]) ### Liste de données
                data_random = read_pickle_experiment(folder_results_random, parameter_used["id"]) ### Liste de données

                monomial_order = parameter_used["monomial_order"]


                if monomial_order == "degrevlex" or monomial_order == "deglex":

                    x.append(parameter_used[variable_parameter])

                    """
                        First deal with the result of the primitive
                    """

                    if data_primitive is None:
                        first_monomial_order_primitive.append(None)
                        first_monomial_order_primitive_info.append("none"[0])
                        first_monomial_order_plus_transformation_primitive.append(None)
                        transformation_primitive_info.append("none"[0])
                        transformation_primitive.append(None)
                        ideal_degree_list_primitive.append(None)
                        ideal_degree_theory.append(None)
                        solving_degree_list_primitive.append(None)
                        solving_degree_theory.append(None)

                    else:

                        system_of_equation_shape = data_primitive[0]["system_of_equation_shape"]
                        mean_time_gb_primitive, ecart_type_time_gb_primitive = statistics_analysis(data_primitive, "groebner_time")
                        mean_time_tf_primitive, ecart_type_time_tf_primitive = statistics_analysis(data_primitive, "transformation_basis_time")
                        mean_ideal_degree_primitive, ecart_type_ideal_degree_primitive = statistics_analysis_no_log(data_primitive, "ideal_degree")
                        mean_solving_degree_primitive, ecart_type_solving_degree_primitive = statistics_analysis_no_log(data_primitive, "solving_degree")
                        
                        product_input_degree = 1
                        macaulay_bound = 1
                        for equation_shape in system_of_equation_shape:
                            product_input_degree *= equation_shape[2]
                            macaulay_bound += equation_shape[2] - 1

                        if mean_time_gb_primitive is np.nan and mean_time_tf_primitive is np.nan:

                            first_monomial_order_primitive.append(np.nan)
                            first_monomial_order_primitive_info.append('n')
                            first_monomial_order_primitive_ecart_type.append(np.nan)
                            first_monomial_order_plus_transformation_primitive.append(np.nan)
                            first_monomial_order_plus_transformation_primitive_ecart_type.append(np.nan)
                            transformation_primitive.append(np.nan)
                            transformation_primitive_ecart_type.append(np.nan)
                            transformation_primitive_info.append('n')
                            ideal_degree_list_primitive.append(np.nan)
                            ideal_degree_theory.append(product_input_degree)
                            ideal_degree_list_primitive_ecart_type.append(np.nan)
                            solving_degree_list_primitive.append(np.nan)
                            solving_degree_theory.append(macaulay_bound)
                            solving_degree_list_primitive_ecart_type.append(np.nan)
                        
                        elif mean_time_gb_primitive is not np.nan and mean_time_tf_primitive is np.nan:

                            first_monomial_order_primitive.append(mean_time_gb_primitive)
                            first_monomial_order_primitive_info.append('w')
                            first_monomial_order_primitive_ecart_type.append(ecart_type_time_gb_primitive)
                            first_monomial_order_plus_transformation_primitive.append(np.nan)
                            first_monomial_order_plus_transformation_primitive_ecart_type.append(np.nan)
                            transformation_primitive.append(np.nan)
                            transformation_primitive_ecart_type.append(np.nan)
                            transformation_primitive_info.append('n')
                            ideal_degree_list_primitive.append(np.nan)
                            ideal_degree_theory.append(product_input_degree)
                            ideal_degree_list_primitive_ecart_type.append(np.nan)
                            solving_degree_list_primitive.append(mean_solving_degree_primitive)
                            solving_degree_theory.append(macaulay_bound)
                            solving_degree_list_primitive_ecart_type.append(ecart_type_solving_degree_primitive)

                        else:

                            mean_first_monomial_order_plus_transformation_time_primitive, ecart_type_first_monomial_order_plus_transformation_time_primitive = first_monomial_order_plus_transformation_statistics_analysis(data_primitive)

                            first_monomial_order_primitive.append(mean_time_gb_primitive)
                            first_monomial_order_primitive_info.append('w')
                            first_monomial_order_primitive_ecart_type.append(ecart_type_time_gb_primitive)
                            first_monomial_order_plus_transformation_primitive.append(mean_first_monomial_order_plus_transformation_time_primitive)
                            first_monomial_order_plus_transformation_primitive_ecart_type.append(ecart_type_first_monomial_order_plus_transformation_time_primitive)
                            transformation_primitive_info.append("w")
                            transformation_primitive.append(mean_time_tf_primitive)
                            transformation_primitive_ecart_type.append(ecart_type_time_tf_primitive)
                            ideal_degree_list_primitive.append(mean_ideal_degree_primitive)
                            ideal_degree_theory.append(product_input_degree)
                            ideal_degree_list_primitive_ecart_type.append(ecart_type_ideal_degree_primitive)
                            solving_degree_list_primitive.append(mean_solving_degree_primitive)
                            solving_degree_theory.append(macaulay_bound)
                            solving_degree_list_primitive_ecart_type.append(ecart_type_solving_degree_primitive)
                    
                    """
                        Second deal with the result of the random
                    """

                    if data_random is None:
                        first_monomial_order_random.append(np.nan)
                        first_monomial_order_random_ecart_type.append(np.nan)
                        first_monomial_order_random_info.append('n')
                        first_monomial_order_plus_transformation_random.append(np.nan)
                        first_monomial_order_plus_transformation_random_ecart_type.append(np.nan)
                        transformation_random_info.append('n')
                        transformation_random.append(np.nan)
                        transformation_random_ecart_type.append(np.nan)
                        ideal_degree_list_random.append(np.nan)
                        ideal_degree_list_random_ecart_type.append(np.nan)
                        solving_degree_list_random.append(np.nan)
                        solving_degree_list_random_ecart_type.append(np.nan)

                    else:

                        mean_time_gb_random, ecart_type_time_gb_random = statistics_analysis(data_random, "groebner_time")
                        mean_time_tf_random, ecart_type_time_tf_random = statistics_analysis(data_random, "transformation_basis_time")
                        mean_ideal_degree_random, ecart_type_ideal_degree_random = statistics_analysis_no_log(data_random, "ideal_degree")
                        mean_solving_degree_random, ecart_type_solving_degree_random = statistics_analysis_no_log(data_random, "solving_degree")

                        if mean_time_gb_random is np.nan and mean_time_tf_random is np.nan:

                            first_monomial_order_random.append(np.nan)
                            first_monomial_order_random_info.append('n')
                            first_monomial_order_random_ecart_type.append(np.nan)
                            first_monomial_order_plus_transformation_random.append(np.nan)
                            first_monomial_order_plus_transformation_random_ecart_type.append(np.nan)
                            transformation_random.append(np.nan)
                            transformation_random_ecart_type.append(np.nan)
                            transformation_random_info.append('n')
                            ideal_degree_list_random.append(np.nan)
                            ideal_degree_list_random_ecart_type.append(np.nan)
                            solving_degree_list_random.append(np.nan)
                            solving_degree_list_random_ecart_type.append(np.nan)
                        
                        elif mean_time_gb_random is not np.nan and mean_time_tf_random is np.nan:

                            first_monomial_order_random.append(mean_time_gb_random)
                            first_monomial_order_random_info.append('w')
                            first_monomial_order_random_ecart_type.append(ecart_type_time_gb_random)
                            first_monomial_order_plus_transformation_random.append(np.nan)
                            first_monomial_order_plus_transformation_random_ecart_type.append(np.nan)
                            transformation_random.append(np.nan)
                            transformation_random_ecart_type.append(np.nan)
                            transformation_random_info.append('n')
                            ideal_degree_list_random.append(np.nan)
                            ideal_degree_list_random_ecart_type.append(np.nan)
                            solving_degree_list_random.append(mean_solving_degree_random)
                            solving_degree_list_random_ecart_type.append(ecart_type_solving_degree_random)

                        else:

                            mean_first_monomial_order_plus_transformation_time, ecart_type_first_monomial_order_plus_transformation_time = first_monomial_order_plus_transformation_statistics_analysis(data_random)

                            first_monomial_order_random.append(mean_time_gb_random)
                            first_monomial_order_random_info.append('w')
                            first_monomial_order_random_ecart_type.append(ecart_type_time_gb_random)
                            first_monomial_order_plus_transformation_random.append(mean_first_monomial_order_plus_transformation_time)
                            first_monomial_order_plus_transformation_random_ecart_type.append(ecart_type_first_monomial_order_plus_transformation_time)
                            transformation_random_info.append("w")
                            transformation_random.append(mean_time_tf_random)
                            transformation_random_ecart_type.append(ecart_type_time_tf_random)
                            ideal_degree_list_random.append(mean_ideal_degree_random)
                            ideal_degree_list_random_ecart_type.append(ecart_type_ideal_degree_random)
                            solving_degree_list_random.append(mean_solving_degree_random)
                            solving_degree_list_random_ecart_type.append(ecart_type_solving_degree_random)
                    

                elif monomial_order == "lex" or monomial_order == "invlex":

                    x_elimination.append(parameter_used[variable_parameter])

                    """
                        First deal with the result of the primitive
                    """

                    if data_primitive is None:
                        elimination_primitive.append(np.nan)
                        elimination_primitive_info.append('n')
                        elimination_primitive_ecart_type.append(np.nan)

                    else:

                        mean_time_gb_compared, ecart_type_time_gb_compared = statistics_analysis(data_primitive, "groebner_time")

                        if mean_time_gb_compared is np.nan:
                            elimination_primitive.append(np.nan)
                            elimination_primitive_ecart_type.append(np.nan)
                            elimination_primitive_info.append('n')

                        else:
                            elimination_primitive_info.append("w")
                            elimination_primitive.append(mean_time_gb_compared)
                            elimination_primitive_ecart_type.append(ecart_type_time_gb_compared)

                    """
                        Second deal with the result of the random
                    """
                    
                    if data_random is None:
                        elimination_random.append(np.nan)
                        elimination_random_info.append('n')
                        elimination_random_ecart_type.append(np.nan)

                    else:

                        mean_time_gb_compared, ecart_type_time_gb_compared = statistics_analysis(data_random, "groebner_time")

                        if mean_time_gb_compared is np.nan:
                            elimination_random.append(np.nan)
                            elimination_random_ecart_type.append(np.nan)
                            elimination_random_info.append('n')

                        else:
                            elimination_random_info.append("w")
                            elimination_random.append(mean_time_gb_compared)
                            elimination_random_ecart_type.append(ecart_type_time_gb_compared)

            if all_none(elimination_primitive) and all_none(first_monomial_order_primitive) and all_none(first_monomial_order_plus_transformation_primitive):
                continue

            if all_inf_lowerbound(elimination_primitive, LOWERBOUND) and all_inf_lowerbound(first_monomial_order_primitive, LOWERBOUND) and all_inf_lowerbound(first_monomial_order_plus_transformation_primitive, LOWERBOUND):
                continue

            fig, axes = plt.subplots(1, 3)

            handles_0 = []
            labels_0 = []
                
            if first_monomial_order_primitive != []:

                first_monomial_order_primitive_plot = axes[0].errorbar(x, first_monomial_order_primitive, yerr=first_monomial_order_primitive_ecart_type, marker='o', color="#1f77b4")
                handles_0.append(first_monomial_order_primitive_plot)
                labels_0.append('First monomial order ' + str(to_list_info(first_monomial_order_primitive_info)))

            if first_monomial_order_random != []:
                first_monomial_order_random_plot = axes[0].errorbar(x, first_monomial_order_random, yerr=first_monomial_order_random_ecart_type, linestyle='--', marker='o', color="#1f77b4")
                handles_0.append(first_monomial_order_random_plot)
                labels_0.append('First monomial order Random ' + str(to_list_info(first_monomial_order_random_info)))

            if transformation_primitive != []:
                transformation_primitive_plot = axes[0].errorbar(x, transformation_primitive, yerr=transformation_primitive_ecart_type, marker='s', color="#2ca02c")
                handles_0.append(transformation_primitive_plot)
                labels_0.append('Transformation ' + str(to_list_info(transformation_primitive_info)))

            if transformation_random != []:
                transformation_random_plot = axes[0].errorbar(x, transformation_random, yerr=transformation_random_ecart_type, linestyle='--', marker='s', color="#2ca02c")
                handles_0.append(transformation_random_plot)
                labels_0.append('Transformation Random ' + str(to_list_info(transformation_random_info)))

            if first_monomial_order_plus_transformation_primitive != []:
                first_monomial_order_plus_transformation_primitive_plot = axes[0].errorbar(x, first_monomial_order_plus_transformation_primitive, yerr=first_monomial_order_plus_transformation_primitive_ecart_type, marker='*', label = "First monomial order + Transformation", color="#ff7f0e")
                handles_0.append(first_monomial_order_plus_transformation_primitive_plot)
                labels_0.append('First monomial order + Transformation')

            if first_monomial_order_plus_transformation_random != []:
                first_monomial_order_plus_transformation_random_plot = axes[0].errorbar(x, first_monomial_order_plus_transformation_random, yerr=first_monomial_order_plus_transformation_random_ecart_type, linestyle='--', marker='*', color="#ff7f0e")
                handles_0.append(first_monomial_order_plus_transformation_random_plot)
                labels_0.append('First monomial order + Transformation Random')

            if elimination_primitive != []:
                elimination_primitive_plot = axes[0].errorbar(x_elimination, elimination_primitive, yerr=elimination_primitive_ecart_type, marker='v', color="#d62728")
                handles_0.append(elimination_primitive_plot)
                labels_0.append('Elimination order ' + str(to_list_info(elimination_primitive_info)))

            if elimination_random != []:
                elimination_random_plot = axes[0].errorbar(x_elimination, elimination_random, yerr=elimination_random_ecart_type, linestyle='--', marker='v', color="#d62728")
                handles_0.append(elimination_random_plot)
                labels_0.append('Elimination order Random' + str(to_list_info(elimination_random_info)))

            handles_1 = []
            labels_1 = []

            if solving_degree_list_primitive != []:
                solving_degree_list_primitive_plot = axes[1].errorbar(x, solving_degree_list_primitive, yerr=solving_degree_list_primitive_ecart_type, color="#2ca02c")
                handles_1.append(solving_degree_list_primitive_plot)
                labels_1.append("Regularity degree " + str(to_list_info(solving_degree_list_primitive)))

            if solving_degree_list_random != []:
                solving_degree_list_random_plot = axes[1].errorbar(x, solving_degree_list_random, yerr=solving_degree_list_random_ecart_type, linestyle='--', color="#2ca02c")
                handles_1.append(solving_degree_list_random_plot)
                labels_1.append("Regularity degree random " + str(to_list_info(solving_degree_list_random)))

            if solving_degree_theory != []:
                solving_degree_theory_plot, = axes[1].plot(x, solving_degree_theory, color="#ff7f0e")
                handles_1.append(solving_degree_theory_plot)
                labels_1.append("Macaulay bound " + str(to_list_info(solving_degree_theory)))

            handles_2 = []
            labels_2 = []

            if ideal_degree_list_primitive != []:
                ideal_degree_list_primitive_plot = axes[2].errorbar(x, ideal_degree_list_primitive, yerr=ideal_degree_list_primitive_ecart_type, color="#2ca02c")
                handles_2.append(ideal_degree_list_primitive_plot)
                labels_2.append("Ideal degree " + str(to_list_info(ideal_degree_list_primitive)))
            
            if ideal_degree_list_random != []:
                ideal_degree_list_random_plot = axes[2].errorbar(x, ideal_degree_list_random, yerr=ideal_degree_list_random_ecart_type, linestyle='--', color="#2ca02c")
                handles_2.append(ideal_degree_list_random_plot)
                labels_2.append("Ideal degree random " + str(to_list_info(ideal_degree_list_random)))

            if ideal_degree_theory != []:
                ideal_degree_theory_plot, = axes[2].plot(x, ideal_degree_theory, color="#ff7f0e")
                handles_2.append(ideal_degree_theory_plot)
                labels_2.append("Ideal degree theory " + str(to_list_info(ideal_degree_theory)))

            exclude = ["id", variable_parameter, "monomials_degree_variables_vector", "seed", "version", "options", "monomial_order", "number_test"]    
            title = ", ".join(k + ": " + str(v) for k, v in parameter.items() if k not in exclude)
            fig.suptitle(title)

            axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[0].set_xlabel(NAMES_NICE_PRINTING[variable_parameter])
            axes[0].set_ylabel("Computation time (s) - logarithmic scale")
            axes[0].legend(handles=handles_0, labels=labels_0)
            axes[0].grid(True)

            axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[1].set_xlabel(NAMES_NICE_PRINTING[variable_parameter])
            axes[1].set_ylabel("Degree")
            axes[1].legend(handles=handles_1, labels=labels_1)
            axes[1].grid(True)

            axes[2].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[2].set_xlabel(NAMES_NICE_PRINTING[variable_parameter])
            axes[2].set_ylabel("Degree")
            axes[2].legend(handles=handles_2, labels=labels_2)
            axes[2].grid(True)

            ax_stop = plt.axes([0.8, 0.02, 0.15, 0.06])
            btn_stop = Button(ax_stop, 'STOP', color='red', hovercolor='red')
            btn_stop.on_clicked(stop)
            plt.show()


def algorithms_comparison(folder_results_primitive:str, folder_results_random:str, variable_parameter:str, timing_analysed:str):

    """
    Compare the computation of the algorithms to compute either the Gröbner basis or the term order change algorithm for random ideals and primitives

    :param folder_results_primitive: Folder containing the results file of the primitive benchmark
    :type folder_results_primitive: str
    :param folder_results_random: Folder containing the results of the comparison with random ideals
    :type folder_results_random: str
    :param variable_parameter: The parameter we want to see the influence
    :type variable_parameter: str
    :param timing_analysed: The part of the computation analysed ("groebner_time" or "transformation_basis_time")
    :type timing_analysed: str
        
    """

    if timing_analysed == "groebner_time":
        key = "algo_gb"

    elif timing_analysed == "transformation_basis_time":
        key = "algo_order_change"

    parameters_primitive = read_pickle_parameters(folder_results_primitive)[1:]

    parameters_treated = []

    if key == "algo_gb":

        keys_to_ignore=["id", variable_parameter, key, "seed", "options"]  ## Keys we ignore as we don"t compare them (they may be different)
        keys_to_ignore_elimination=["id", variable_parameter, key, "seed", "options", "algo_order_change"]

    elif key == "algo_order_change":

        keys_to_ignore=["id", variable_parameter, key, "seed", "options"]  ## Keys we ignore as we don"t compare them (they may be different)
        keys_to_ignore_elimination=[]


    for parameter in parameters_primitive:

        if key == "algo_order_change" and parameter["algo_order_change"] is None: ### SKip elimination ideal and elimination order for the transformation basis
            
            parameters_treated.append(parameter)
            continue

        if not parameter in parameters_treated: ## Check if the parameter has not been treated before

            parameters_treated.append(parameter)

            parameters_used = [parameter]

            for parameter_compared in parameters_primitive: ## The list of parameters that are going to displayed

                if dict_keys_equal_except_keys_specified(parameter, parameter_compared, keys_to_ignore) and parameter_compared != parameter:

                    parameters_treated.append(parameter_compared)
                    parameters_used.append(parameter_compared)

                if dict_keys_equal_except_keys_specified(parameter, parameter_compared, keys_to_ignore_elimination) and parameter_compared != parameter and (parameter_compared["algo_gb"].startswith("eliminate:giac") or parameter_compared["algo_gb"].startswith("eliminate:libsingular")) and not parameter_compared in parameters_used:

                    parameters_treated.append(parameter_compared)
                    parameters_used.append(parameter_compared)

            grouped = defaultdict(list)
            for d in parameters_used:

                grouped[d[key]].append(d) ## Parameters grouped depending on the algorithm

            evolution_by_algos = list(grouped.values())

            handles_list = []
            labels_list = []

            all_none_plot = True

            for evolution_algo in evolution_by_algos:

                if STOP_REQUESTED:
                    exit(0)

                timings_log_primitive = []
                timings_log_primitive_ecart_type = []
                timings_info_primitive = []

                timings_log_random = []
                timings_log_random_ecart_type = []
                timings_info_random = []

                x_axis = []

                algo = evolution_algo[0][key]

                for param in evolution_algo:

                    x_axis.append(param[variable_parameter])

                    data_primitive = read_pickle_experiment(folder_results_primitive, param["id"])
                    data_random = read_pickle_experiment(folder_results_random, param["id"])

                    """
                        First deal with the result of the primitive
                    """

                    if data_primitive is None:
                        timings_log_primitive.append(np.nan)
                        timings_log_primitive_ecart_type.append(np.nan)
                        timings_info_primitive.append('n')
                    else:
                        mean_time_primitve, ecart_type_time_primitive = statistics_analysis(data_primitive, timing_analysed)
                        if mean_time_primitve is np.nan:
                            timings_log_primitive.append(np.nan)
                            timings_log_primitive_ecart_type.append(np.nan)
                            timings_info_primitive.append('n')
                        else:
                            timings_log_primitive.append(mean_time_primitve)
                            timings_log_primitive_ecart_type.append(ecart_type_time_primitive)
                            timings_info_primitive.append('w')

                    """
                        Second deal with the result of the random
                    """

                    if data_random is None:
                        timings_log_random.append(np.nan)
                        timings_log_random_ecart_type.append(np.nan)
                        timings_info_random.append('n')
                    else:
                        mean_time, ecart_type_time = statistics_analysis(data_random, timing_analysed)
                        if mean_time is np.nan:
                            timings_log_random.append(np.nan)
                            timings_log_random_ecart_type.append(np.nan)
                            timings_info_random.append('n')
                        else:
                            timings_log_random.append(mean_time)
                            timings_log_random_ecart_type.append(ecart_type_time)
                            timings_info_random.append('w')

                if not all_none(timings_log_primitive) or not all_none(timings_log_random):
                    all_none_plot = False

                if algo.startswith("eliminate:giac"):
                    algo_marker = "eliminate:giac"

                elif algo.startswith("eliminate:libsingular"):
                    algo_marker = "eliminate:libsingular"

                else:
                    algo_marker = algo

                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

                if timings_log_primitive != []:

                    timings_log_primitive_plot = plt.errorbar(x_axis, timings_log_primitive, yerr=timings_log_primitive_ecart_type, marker=ALGOS_MARKER[algo_marker], color=ALGOS_COLOR[algo_marker])
                    handles_list.append(timings_log_primitive_plot)
                    labels_list.append(algo + " Primitive " + str(to_list_info(timings_info_primitive)))

                if timings_log_random != []:
                    timings_log_random_plot = plt.errorbar(x_axis, timings_log_random, yerr=timings_log_random_ecart_type, linestyle='--', marker=ALGOS_MARKER[algo_marker], color=ALGOS_COLOR[algo_marker])
                    handles_list.append(timings_log_random_plot)
                    labels_list.append(algo + " Random " + str(to_list_info(timings_info_random)))

            if not all_none_plot:

                exclude = ["id", key, variable_parameter, "monomials_degree_variables_vector", "seed", "version", "options"]   

                title = ", ".join(NAMES_NICE_PRINTING[k] + ": " + str(v) for k, v in parameter.items() if k not in exclude)
                plt.title(title)
                plt.xlabel(NAMES_NICE_PRINTING[variable_parameter])
                plt.ylabel(NAMES_NICE_PRINTING[timing_analysed] + " (s) logarithmic scale")
                plt.legend(handles=handles_list, labels=labels_list)
                plt.grid(True)
                plt.tight_layout()
                ax_stop = plt.axes([0.8, 0.02, 0.15, 0.06])
                btn_stop = Button(ax_stop, 'STOP', color='red', hovercolor='red')
                btn_stop.on_clicked(stop)
                plt.show()

            else:
                plt.clf()