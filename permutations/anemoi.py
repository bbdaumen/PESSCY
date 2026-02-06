from sage.all import *
from utils.constants_generation import *
from utils.matrices_generation import *
from utils.timer import *


def compute_exponent(field):
    d = 2
    while gcd(d, field.characteristic()-1) != 1:
        d +=1
    return d


class Anemoi:
    def __init__(self, field, branch, round, constant_vector_list, a):
        self.field = field
        self.branch = branch
        self.round = round
        self.constant_vector_list = constant_vector_list
        self.d = compute_exponent(self.field)
        self.d_inv = inverse_mod(self.d, self.field.characteristic()-1)
        self.matrix = matrix_mds("anemoi", self.field, self.branch)
        self.a = a
        self.a_inv = a**(-1)


    def NonLinearLayer(self, x):
        y = vector([0]*self.branch).change_ring(x.base_ring())
        y[0] = x[0] - self.a * x[1] ** 2 - self.a_inv + self.a * (x[1] - (x[0] - self.a * x[1]**2 - self.a_inv)**self.d_inv)**2
        y[1] = x[1] - (x[0] - self.a * x[1]**2 - self.a_inv)**self.d_inv
        return y
    
    def round_function(self, x, i):
        return self.NonLinearLayer(self.matrix * (x + self.constant_vector_list[i]))
    
    def permutation(self, x):
        for i in range(self.round):
            x = self.round_function(x, i)
        x = self.matrix * x
        return x
    
    def NonLinearLayer_CICO1_solve(self, x, new_var):
        y = vector([- self.field(2) * self.a * new_var * x[1] + self.a * new_var**2 + x[0] - self.a_inv, x[1] - new_var])
        eq = new_var ** self.d + self.a * x[1]**2 - x[0] + self.a_inv
        return y, eq
    
    def round_function_CICO1_solve(self, x, new_var, i):
        y = self.matrix * (x + self.constant_vector_list[i])
        z, eq = self.NonLinearLayer_CICO1_solve(y, new_var)
        return z, eq
    
    def permutation_CICO1_solve(self, x, extra_vars):
        system_of_equations = []
        for i in range(self.round):
            x, new_eq = self.round_function_CICO1_solve(x, extra_vars[i], i)
            system_of_equations.append(new_eq)
        x = self.matrix * x
        system_of_equations.append(x[0])
        return system_of_equations

def generate_system_of_equations(q, field, order, branch:int, cico, round, seed, constant_vector_list) -> tuple[list | None, float | None]:

    set_random_seed(seed)    
    R = PolynomialRing(field,["X_{}".format(i) for i in range(round+1)], order=order)
    var_list = list(R.gens())

    input = []
    for _ in range(branch-1):
        input_element = field(0)
        coef1 = field.random_element()
        while coef1 == field(0):
            coef1 = field.random_element()
        input_element += coef1 * var_list[0]
        coef0 = field.random_element()
        while coef0 == field(0):
            coef0 = field.random_element()
        input_element += coef0
        input.append(input_element)
    input_cico = vector([field(0)] * cico + input)

    a = field(0)
    while a == field(0):
        a = field.random_element()
    permutation = Anemoi(field, branch, round, constant_vector_list, a)

    timer_gen_sys_of_eq = Chronograph("Generation system of equations Anemoi CICO-{}".format(cico))

    try:
        system_of_equations = permutation.permutation_CICO1_solve(input_cico, var_list[1:])
        time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure() 
    except Exception as e:
        system_of_equations = None
        time_gen_sys_of_eq = None

    q.put((system_of_equations, time_gen_sys_of_eq))