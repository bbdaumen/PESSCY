from sys import executable, stdout, stderr
from os import remove
from os.path import exists
from sage.all import GF
from multiprocessing import Queue, Process
from pickle import dump
from subprocess import TimeoutExpired, CalledProcessError, Popen
from tempfile import NamedTemporaryFile

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
        system_of_equation_shape.append((len(equation.monomials()), indices, equation.total_degree()))
    return system_of_equation_shape

class ExperimentRecord:

    """
    Class for the generation of system(s) of equations corresponding to an algebraic attack over a primitive and its solving.

    :param str folder_results: Path of the folder containing the results of the generation
    :param int id: ID of the files containing log and results of the experiment

    :param int field_size: size of the prime finite field
    :param str monomial_order: monomial order to use to define the multivariate polynomial ring
    :param list[tuple[int, list[int], int]] monomials_degree_variables_vector: List of shape of the equations to generate

    :param number_test: Number of systems to generate
    :param int seed: seed for randomness

    :param str algo_gb: Algorithm to compute the Gröbner basis
    :param dict[str, list[dict[str, any]]] options: Options for the Gröbner basis algorithm
    :param str algo_order_change: Algorithm to use for the term order change
    """

    def __init__(self, folder_results:str, id:int, algo_gb:str, options:dict[str, list[dict[str, any]]], algo_order_change:str, field_size:int, monomial_order:str, permutation:str,number_test:int, seed:int, monomials_degree_variables_vector:list[tuple[int, list[int], int]]):

        self.file_log_result_path = f"./{folder_results}/logs/{id}.log"
        self.file_output_result_path = f"./{folder_results}/res/{id}.pkl"

        self.id = id
        self.seed = seed

        self.permutation = permutation
        self.field_size = field_size
        self.field = GF(field_size)
        self.monomial_order = monomial_order
        self.number_test = number_test

        self.monomials_degree_variables_vector = monomials_degree_variables_vector

        self.algo_gb = algo_gb
        self.options = options
        self.algo_order_change = algo_order_change

    """
        Generate the system of equations depending on whether the systems are from an algebraic attack on a permutation or a random ideal.
    """

    def generation_equation(self, system_generation_timeout:float, state:str):
        
        """
            Return the system of equations shape.
        """

        system_of_equations_list = []
        
        for i in range(self.number_test):

            results_dict = {"system_of_equation_shape" : state, "generation_time" : state, "groebner_time" : state, "solving_degree" : state, "ideal_dimension" : state, "transformation_basis_time" : state, "radical_ideal" : state, "shape_position" : state, "ideal_degree" : state}
            
            generate_system_of_equations_cico_fun = import_perm(self.permutation)

            try:

                q = Queue()
                p = Process(target=generate_system_of_equations_cico_fun, args=(q, self.field, self.monomial_order, self.monomials_degree_variables_vector, self.seed + i, ))
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
                        raise Exception("Error has occurred")

            except TimeoutException:
                system_of_equations, system_of_equations_generation_time = "timetimeout_generationout", "timeout_generation"
                print("ID", self.id, "Timeout")

            except Exception as e:
                system_of_equations, system_of_equations_generation_time = "failed_generation", "failed_generation"
                print("ID", self.id, "Random ideal generation failed")
                print(f"Error : {e}")
            
            finally:

                system_of_equations_list.append(system_of_equations)

                if system_of_equations is None:
                    results_dict = {"system_of_equation_shape" : "failed_generation", "generation_time" : "failed_generation", "groebner_time" : "failed_generation", "solving_degree" : "failed_generation", "ideal_dimension" : "failed_generation", "transformation_basis_time" : "failed_generation", "radical_ideal" : "failed_generation", "shape_position" : "failed_generation", "ideal_degree" : "failed_generation"} ### Added solving_degree ###
                    
                elif system_of_equations == "timeout_generation":
                    results_dict = {"system_of_equation_shape" : "timeout_generation", "generation_time" : "timeout_generation", "groebner_time" : "timeout_generation", "solving_degree" : "timeout_generation", "ideal_dimension" : "timeout_generation", "transformation_basis_time" : "timeout_generation", "radical_ideal" : "timeout_generation", "shape_position" : "timeout_generation", "ideal_degree" : "timeout_generation"} ### Added solving_degree ###

                elif system_of_equations == "failed_generation":
                    results_dict = {"system_of_equation_shape" : "failed_generation", "generation_time" : "failed_generation", "groebner_time" : "failed_generation", "solving_degree" : "failed_generation", "ideal_dimension" : "failed_generation", "transformation_basis_time" : "failed_generation", "radical_ideal" : "failed_generation", "shape_position" : "failed_generation", "ideal_degree" : "failed_generation"} ### Added solving_degree ###

                else:
                    results_dict["system_of_equation_shape"] = system_of_equation_shape(system_of_equations)
                    results_dict["generation_time"] = system_of_equations_generation_time
                
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

        system_of_equations_list = self.generation_equation(system_generation_timeout, "failed")

        add_to_forbidden_zone = False

        for (i, system_of_equations) in enumerate(system_of_equations_list):

            print("\nExperiment number:", i, flush=True)

            if system_of_equations is not None and system_of_equations != "timeout_generation" and system_of_equations != "failed_generation":

                try:

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
                    kill_process_tree(proc)
                    timeout_algo = change_dict_failed_to_timeout(self.file_output_result_path, i, self.number_test)
                    if timeout_algo == 0 and i == 0: ### Si le calcul de la première base de Gröbner n'est pas possible alors j'arrête cette attaque algébrique
                        for j in range(1, self.number_test):
                            change_dict_failed_to_skipped(self.file_output_result_path, j, self.number_test)
                        print("End of timeout management", flush=True)
                        return add_to_forbidden_zone
                    print("End of timeout management", flush=True)
                    
                except CalledProcessError as e:
                    print(f"Error in algebraic attack: {e}")
                
                except KeyboardInterrupt:
                    print("Processes killed by Ctrl+C")
                    kill_process_tree(proc)
                    return

                finally:
                    if exists(input_file):
                        remove(input_file)
            
            else:

                print("No system of equations")
                
        return add_to_forbidden_zone