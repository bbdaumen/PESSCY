from sage.all import *
from utils.constants_generation import *
from utils.matrices_generation import *
from utils.timer import *

class Zerolith:

    def __init__(self, field, branch, round, constant_vector_list):
        self.field = field
        self.branch = branch
        self.round = round
        self.matrix = matrix_mds("zerolith", self.field, self.branch)
        self.constant_vector_list = constant_vector_list
        
    def round_function(self, input, i):
        tmp_next = input[0]
        for j in range(1, self.branch):
            tmp_prev = tmp_next
            tmp_next = input[j]
            input[j] += tmp_prev**2
        input = self.matrix * input + self.constant_vector_list[i]
        return input
    
    def permutation(self, input):
        for i in range(self.round):
            input = self.round_function(input, i)
        return input
    

def generate_system_of_equations(q, field, order, branch, cico, round, seed, constant_vector_list):
    set_random_seed(seed)
    var_list = list(PolynomialRing(field,["X_{}".format(i) for i in range(cico)], order=order).gens())
    input = []
    for _ in range(branch-cico):
        input_element = field(0)
        for var in var_list:
            coef = field.random_element()
            while coef == field(0):
                coef = field.random_element()
            input_element += coef * var
        input.append(input_element)
    input_cico = vector([field(0)] * cico + input)
    permutation = Zerolith(field, branch, round, constant_vector_list)
    try:
        timer_gen_sys_of_eq = Chronograph("Generation system of equations Zerolith CICO-{}".format(cico))
        system_of_equations = list(permutation.permutation(input_cico))[0:cico]
        time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure() 
    except Exception as e:
        system_of_equations = None
        time_gen_sys_of_eq = None

    q.put((system_of_equations, time_gen_sys_of_eq))