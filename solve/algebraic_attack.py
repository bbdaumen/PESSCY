from sys import executable, stdout, stderr, argv
from os import remove, makedirs
from os.path import exists
from pickle import dump
from subprocess import TimeoutExpired, CalledProcessError, Popen
from ast import literal_eval
from signal import SIGINT
from tempfile import NamedTemporaryFile

from utils.pickle_utils import change_dict_failed_to_timeout, read_pkl_file
from utils.utils_all import redirect_all_output

def system_of_equation_shape(system_of_equation:list):

    """Return the system of equations shape that is a list of tuple. Each tuple has 3 coordinates: the number of monomials in the polynomial, the indices of the variables involved in the polynomial and the total degree of the polynomial.
    Each tuple corresponds to the shape of a polynomial in the system. It allows to draw random ideal generated from system of equations sharing the same shape.
    
    :param list system_of_equation: System of equations
    """

    system_of_equation_shape = []
    for equation in system_of_equation:
        vars = equation.variables()
        indices = [int(str(var).split('_')[1]) for var in vars]
        system_of_equation_shape.append((len(equation.monomials()), indices, equation.total_degree()))
    return system_of_equation_shape

class Solve:

    """Solve is the class to solve a multivariate system of equations.

        :param str file_log_result_path: Path to the log file
        :param str file_output_result_path: Path to the file containing result
        :param str file_input_path: Path to the file with systems
        :param str algo_gb: Algorithm to compute the Gröbner basis
        :param dict[str, list[dict[str, any]]] options: Options for the Gröbner basis algorithm
        :param str algo_order_change: Algorithm to use for the temr order change step
        :param float full_computation_timeout: timeout to solve the systems
        
        """

    def __init__(self, file_log_result_path:str, file_output_result_path:str, file_input_path:str, algo_gb:str, options:dict[str, list[dict[str, any]]], algo_order_change:str, full_computation_timetout:float):

        self.file_log_result_path = file_log_result_path
        self.file_output_result_path = file_output_result_path

        self.input_file_path = file_input_path

        self.full_computation_timetout = full_computation_timetout

        self.algo_gb = algo_gb
        self.options = options
        self.algo_order_change = algo_order_change
        
    def solve(self):

        """Solve the systems of equations
        """

        open(self.file_output_result_path, "wb").close()

        system_of_equations_list = read_pkl_file(self.input_file_path)
        number_test = len(system_of_equations_list)

        for (i, (system_of_equations, generation_time)) in enumerate(system_of_equations_list):

            ### Define the dictionnary of the algebraic attack with the data of the generation of the system

            results_dict = {"system_of_equation_shape" : system_of_equation_shape(system_of_equations), "generation_time" : generation_time, "groebner_time" : "failed", "solving_degree" : "failed", "ideal_dimension" : "failed", "transformation_basis_time" : "failed", "radical_ideal" : "failed", "shape_position" : "failed", "ideal_degree" : "failed"}

            with open(self.file_output_result_path, "ab") as f:
                dump(results_dict, f)
                f.flush()
            f.close()

        for (i, (system_of_equations, generation_time)) in enumerate(system_of_equations_list):

            if system_of_equations is not None and system_of_equations != "timeout_generation" and system_of_equations != "failed_generation":

                ### If the system of equations have been generated then try to solve it
                try:
                    
                    monomial_order = system_of_equations[0].parent().term_order()

                    ### Store the inputs of the solve script in a file as system of equations may not be used as input due to its potential length

                    with NamedTemporaryFile(delete=False) as f:
                        dump((self.file_log_result_path, self.file_output_result_path, i, number_test, system_of_equations, self.algo_gb, monomial_order, self.algo_order_change, self.options), f) ### Order to change
                        f.flush()
                        input_file = f.name

                    proc = Popen(
                        [executable, "utils/systems_solver.py", input_file],
                        stdout=stdout,
                        stderr=stderr,
                        text=True,
                        start_new_session=True
                    )

                    ### Tiemout the full resolution of the system
                    
                    proc.wait(timeout=full_computation_timetout)
                    
                except TimeoutExpired:
                    print("Timeout in the solving of the system of equations")
                    proc.send_signal(SIGINT)
                    _ = change_dict_failed_to_timeout(self.file_output_result_path, i, number_test)
                    
                except CalledProcessError as e:
                    print(f"Error in algebraic attack: {e}")
                
                except KeyboardInterrupt:
                    proc.send_signal(SIGINT)

                finally:
                    if exists(input_file):
                        remove(input_file)
                

if __name__ == "__main__":

    folder_result_name = argv[1]
    folder_input_name = argv[2]

    folder_result_path = f"results/solve/{folder_result_name}"
    file_log_result_path = f"results/solve/{folder_result_name}/{folder_result_name}.log"
    file_output_result_path = f"results/solve/{folder_result_name}/{folder_result_name}.pkl"

    file_input_path = f"results/generate/{folder_input_name}/{folder_input_name}.pkl"

    if not exists(folder_result_path):
        makedirs(folder_result_path)

    redirect_all_output(file_log_result_path)

    algo_gb = argv[3]

    if argv[4] == "None":
        options = None
    else:
        options = literal_eval(argv[4])

    algo_order_change = argv[5]
    full_computation_timetout = float(argv[6])
    
    solve = Solve(file_log_result_path, file_output_result_path, file_input_path, algo_gb, options, algo_order_change, full_computation_timetout)

    solve.solve()

    print("Attack succeeded!")