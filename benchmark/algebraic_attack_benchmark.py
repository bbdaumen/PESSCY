from sys import executable, stdout, stderr
from os import remove
from os.path import exists
from sage.all import GF
from multiprocessing import Queue, Process
from pickle import dump
from subprocess import TimeoutExpired, CalledProcessError, Popen
from tempfile import NamedTemporaryFile

from utils.constants_generation import constants_random_sparsity
from utils.exception import TimeoutException
from utils.pickle_utils import change_dict_failed_to_timeout, change_dict_failed_to_skipped
from utils.utils_all import import_perm, kill_process_tree


def system_of_equation_shape(system_of_equation:list):

    """Return the system of equations shape, that is a tuple of a number of monomials, a list of indices of the variables to use and a total degree.
    
    :param system_of_equation: The system of equations
    :type system_of_equation: list
    """

    system_of_equation_shape = []
    for equation in system_of_equation:
        vars = equation.variables()
        indices = [int(str(var).split('_')[1]) for var in vars]
        ### The shape of a system of equations is a tuple of a number of monomials, list of indices of variables (number of variables must be non negative integer) and a total degree        
        system_of_equation_shape.append((len(equation.monomials()), indices, equation.total_degree()))
    return system_of_equation_shape

class ExperimentRecord:

    """Class for the generation of system(s) of equations corresponding to an algebraic attack over a primitive and its solving.

    :param str folder_results: Path of the folder containing the results of the generation
    :param int id: ID of the files containing log and results of the experiment

    :param int field_size: size of the prime finite field
    :param str monomial_order: monomial order to use to define the multivariate polynomial ring
    :param str permutation: permutation (modelling)
    :param int cico: number of the CICO problem to solve
    :param int round: Number of rounds
    :param int branch: Number of branches
    :param int constant_sparsity: Sparsity of the constant

    :param number_test: Number of systems to generate
    :param int seed: seed for randomness

    :param str algo_gb: Algorithm to compute the Gröbner basis
    :param dict[str, list[dict[str, any]]] options: Options for the Gröbner basis algorithm
    :param str algo_order_change: Algorithm to use for the term order change
    """

    def __init__(self, folder_results:str, id:int, algo_gb:str, options:dict[str, list[dict[str, any]]], algo_order_change:str, field_size:int, monomial_order:str, permutation:str, cico:int, round:int, number_test:int, branch:int, seed:int, constant_sparsity:int):

        self.file_log_result_path = f"./{folder_results}/logs/{id}.log"
        self.file_output_result_path = f"./{folder_results}/res/{id}.pkl"

        self.id = id
        self.seed = seed

        self.permutation = permutation
        self.field_size = field_size
        self.field = GF(field_size)
        self.monomial_order = monomial_order
        self.number_test = number_test

        self.cico = cico
        self.round = round
        self.branch = branch
        self.constant_sparsity = constant_sparsity

        self.algo_gb = algo_gb
        self.options = options
        self.algo_order_change = algo_order_change

    def generate_systems(self, system_generation_timeout:float, state:str):

        """Generate the system of equations from the permutation.
        
        :param system_generation_timeout: Timeout for the generation of the system
        :type system_generation_timeout: float
        :param state: State of the experiment. At the initialisation it is either "skipped" if it is in the forbidden zone or "failed"
        :type state: str
        """

        system_of_equations_list = []
        
        for i in range(self.number_test):

            results_dict = {"system_of_equation_shape" : state, "generation_time" : state, "groebner_time" : state, "solving_degree" : state, "ideal_dimension" : state, "transformation_basis_time" : state, "radical_ideal" : state, "shape_position" : state, "ideal_degree" : state}
            
            ### Import the function that generates the system of equations
            generate_system_of_equations_cico_fun = import_perm(self.permutation)
                
            constant_vector_list = []

            for j in range(self.round):

                ### The seed is modified for every round and systems
                constant_vector_list.append(constants_random_sparsity(self.field, self.branch, self.constant_sparsity, self.seed + j + i * self.round))

            try:

                ### We create a new process to generate the equations and use a Queue to get the system of equations

                q = Queue()
                p = Process(target=generate_system_of_equations_cico_fun, args=(q, self.field, self.monomial_order, self.branch, self.cico, self.round, self.seed , constant_vector_list))
                p.start()
                p.join(system_generation_timeout)

                if p.is_alive():
                    p.terminate()
                    p.join()
                    raise TimeoutException()
                
                else:
                    if not q.empty():
                        system_of_equations, system_of_equations_generation_time = q.get()
                    else:
                        raise Exception("Error has occurred in the Queue to get the system of equations")
                    
            except TimeoutException:
                system_of_equations, system_of_equations_generation_time = "timeout_generation", "timeout_generation"
                print("Timeout system of equations generation")

            except Exception as e:
                system_of_equations, system_of_equations_generation_time = "failed_generation", "failed_generation"
                print("System of equations generation has failed\n")
                print(f"The error is: {e}")
            
            finally:

                system_of_equations_list.append(system_of_equations)

                if system_of_equations is None:
                    results_dict = {"system_of_equation_shape" : "failed_generation", "generation_time" : "failed_generation", "groebner_time" : "failed_generation", "solving_degree" : "failed_generation", "ideal_dimension" : "failed_generation", "transformation_basis_time" : "failed_generation", "radical_ideal" : "failed_generation", "shape_position" : "failed_generation", "ideal_degree" : "failed_generation"}
                    
                elif system_of_equations == "timeout_generation":
                    results_dict = {"system_of_equation_shape" : "timeout_generation", "generation_time" : "timeout_generation", "groebner_time" : "timeout_generation", "solving_degree" : "timeout_generation", "ideal_dimension" : "timeout_generation", "transformation_basis_time" : "timeout_generation", "radical_ideal" : "timeout_generation", "shape_position" : "timeout_generation", "ideal_degree" : "timeout_generation"}

                elif system_of_equations == "failed_generation":
                    results_dict = {"system_of_equation_shape" : "failed_generation", "generation_time" : "failed_generation", "groebner_time" : "failed_generation", "solving_degree" : "failed_generation", "ideal_dimension" : "failed_generation", "transformation_basis_time" : "failed_generation", "radical_ideal" : "failed_generation", "shape_position" : "failed_generation", "ideal_degree" : "failed_generation"}

                else:
                    results_dict["system_of_equation_shape"] = system_of_equation_shape(system_of_equations)
                    results_dict["generation_time"] = system_of_equations_generation_time
                
                ### Write the list of result dictionnaries in a pickle file. This file will be updated all along the solving of the systems of equations.
                with open(self.file_output_result_path, 'ab') as f_pkl:
                    dump(results_dict, f_pkl)
                    f_pkl.flush()
                f_pkl.close()

        return system_of_equations_list
    
    def solve_systems(self, system_generation_timeout:float, full_computation_timetout:float):

        """Solve systems of equations generated
        
        :param system_generation_timeout: Timeout for the generation of the system
        :type system_generation_timeout: float
        :param full_computation_timeout: Timeout for the algebraic attack
        :type full_computation_timeout: float
        """

        system_of_equations_list = self.generate_systems(system_generation_timeout, "failed")

        add_to_forbidden_zone = False

        for (i, system_of_equations) in enumerate(system_of_equations_list):

            print("\nExperiment number:", i, flush=True)

            if system_of_equations is not None and system_of_equations != "timeout_generation" and system_of_equations != "failed_generation":

                try:

                    ### Store the inputs of the solve.py script in the tmp file as system of equations is too large to be given as input of the function. Moreover we use subprocess to be able to timeout the execution of the script and to isolate the C processes such as Singular. If one them crashes then it doesn't impact other experiments running on other cores.

                    with NamedTemporaryFile(delete=False) as f:
                        dump((self.file_log_result_path, self.file_output_result_path, i, self.number_test, system_of_equations, self.algo_gb, self.monomial_order, self.algo_order_change, self.options), f)
                        f.flush()
                        input_file = f.name

                    proc = Popen(
                        [executable, "utils/systems_solver.py", input_file],
                        stdout=stdout,
                        stderr=stderr,
                        text=True,
                        start_new_session=True
                    )

                    proc.wait(timeout=full_computation_timetout)
                    
                except TimeoutExpired:
                    print("Timeout, next errors are due to the timeout", flush=True)
                    add_to_forbidden_zone = True
                    ### Kill all the processes coming from proc
                    kill_process_tree(proc)
                    timeout_algo = change_dict_failed_to_timeout(self.file_output_result_path, i, self.number_test)
                    if timeout_algo == 0 and i == 0: ### If the computation of the Gröbner basis of the first experiment is tto long then I stop also the next algebraic attacks
                        for j in range(1, self.number_test):
                            change_dict_failed_to_skipped(self.file_output_result_path, j, self.number_test)
                        print("End of timeout management", flush=True)
                        return add_to_forbidden_zone
                    print("End of timeout management", flush=True)
                    
                except CalledProcessError as e:
                    print(f"Error in algebraic attack: {e}")
                    kill_process_tree(proc)
                
                except KeyboardInterrupt:
                    print("Processes killed by Ctrl+C")
                    kill_process_tree(proc)
                    return

                finally:
                    if exists(input_file):
                        remove(input_file)
                    print("Systems treated")
            
            else:

                print("No system of equations")
                
        return add_to_forbidden_zone