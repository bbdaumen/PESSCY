from sage.all import *
from utils.timer import *

class Template:
    def __init__(self):
        pass

    def generate_systems(self):
        pass

### This is the only compulsory function, it must have the indicated signature

def generate_system_of_equations(q, field, order:str, branch:int, cico:int, round:int, seed:int, constant_vector_list:list) -> tuple[list | None, float | None]:

    ### Set the random seed
    set_random_seed(seed)

    ### Generate the polynomial ring, the variables must be on format X_i with i a non negative integer 
    R = PolynomialRing(field,["X_{}".format(i) for i in range()], order=order)

    ### Instantiate the permutation class
    permutation = Template()

    ### Instantiate the timer for the generation 
    timer_gen_sys_of_eq = Chronograph("Generation system of equations")

    try:
        system_of_equations = permutation.generate_system()
        time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure()

    except Exception as e:
        system_of_equations = None
        time_gen_sys_of_eq = None

    ### Add the system of equations and the time to generate it to the Queue
    q.put((system_of_equations, time_gen_sys_of_eq))