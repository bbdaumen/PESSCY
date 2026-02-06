from os import makedirs
from os.path import exists
from sage.all import GF, sage_eval
from pickle import dump
from sys import argv
from multiprocessing import Queue, Process

from utils.constants_generation import constants_random_sparsity
from utils.utils_all import import_perm, redirect_all_output
from utils.exception import TimeoutException

class Generate:

    """Class for the generation of system(s) of equations corresponding to an algebraic attack over a primitive

    :param str file_systems_generated: File containg the systems generated
    :param float system_generation_timeout: Timeout to the generation of the system of equations

    :param int field_size: size of the prime finite field
    :param str monomial_order: monomial order to use to define the multivariate polynomial ring
    :param str permutation: permutation (modelling)
    :param int cico: number of the CICO problem to solve
    :param int round: Number of rounds
    :param int branch: Number of branches
    :param int constant_sparsity: Sparsity of the constant vectors
    :param number_test: Number of generation of the system to perform
    :param int seed: seed for randomness
    

    """

    def __init__(self, file_systems_generated:str, system_generation_timeout:float, field_size:int, monomial_order:str, permutation:str, cico:int, round:int, number_test:int, branch:int, seed:int, constant_sparsity:int):

        self.file_systems_generated = file_systems_generated

        self.number_test = number_test
        self.seed = seed
        self.system_generation_timeout = system_generation_timeout

        self.permutation = permutation
        self.field = GF(field_size)
        self.monomial_order = monomial_order
        
        self.cico = cico
        self.round = round
        self.branch = branch
        self.constant_sparsity = constant_sparsity

    def generate_systems(self):

        """Generate the system of equations depending on whether the systems are from an algebraic attack on a permutation or a random ideal.
        """

        system_of_equations_list = []

        ### Generate number_test systems of equations, for every loop the seed becomes self.seed + j + i * self.round, where j is the index for the round, i the index for the number of the system of equations and self.round the total number of round
        
        for i in range(self.number_test):

            ### Import the function from the permutation python script to generate the equations
            
            generate_system_of_equations_cico_fun = import_perm(self.permutation)

            constant_vector_list = []

            for j in range(self.round):

                ### Generate the constant vectors to add at each round

                constant_vector_list.append(constants_random_sparsity(self.field, self.branch, self.constant_sparsity, self.seed + j + i * self.round))

            try:

                ### Use multithreading and Queue to timeout the function and returns the value in a Queue

                q = Queue()
                p = Process(target=generate_system_of_equations_cico_fun, args=(q, self.field, self.monomial_order, self.branch, self.cico, self.round, self.seed, constant_vector_list))
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
                system_of_equations, system_of_equations_generation_time = "timeout", "timeout"
                print("Timeout system of equations generation")

            except Exception as e:
                system_of_equations, system_of_equations_generation_time = "failed", "failed"
                print("System of equations generation has failed\n")
                print(f"The error is: {e}")

            finally:

                ### Add to the list of systems of equations and the time to generate them

                system_of_equations_list.append((system_of_equations, system_of_equations_generation_time))

        ### Store the results in the result file

        with open(self.file_systems_generated, 'wb') as f_pkl:
            dump(system_of_equations_list, f_pkl)
            f_pkl.flush()
        f_pkl.close()
    
if __name__ == "__main__":

    folder_name = argv[1]
    folder_results = f"results/generate/{folder_name}"
    file_log = f"{folder_results}/{folder_name}.log"
    file_systems_generated = f"{folder_results}/{folder_name}.pkl"

    if not exists(folder_results):
        makedirs(folder_results)

    redirect_all_output(file_log)

    field_size = int(argv[2])

    if argv[3] in ["lex", "degrevlex", "deglex", "invlex", "neglex", "negdegrevlex", "negdeglex"]:
        monomial_order = argv[3]
    else:
        monomial_order = sage_eval(argv[3])

    permutation = argv[4]
    cico = int(argv[5])
    round = int(argv[6])
    number_test = int(argv[7])
    branch = int(argv[8])
    seed = int(argv[9])
    constant_sparsity = int(argv[10])
    system_generation_timeout = float(argv[11])

    generate = Generate(file_systems_generated, system_generation_timeout, field_size, monomial_order, permutation, cico, round, number_test, branch, seed, constant_sparsity)

    generate.generate_systems()

    print("Generation succeeded!")