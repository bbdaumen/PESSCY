from sage.all import *
from utils.constants_generation import *
from utils.matrices_generation import *
from utils.timer import *


def compute_exponent(field):
    d = 2
    while gcd(d, field.characteristic()-1) != 1:
        d +=1
    return d

def L_i(gamma_i, z0, z1, z2):
    return gamma_i*z0 + z1 + z2

def G_i(alpha_i, beta_i, z_i):
    return z_i**2 + alpha_i*z_i + beta_i

def build_alphas_betas(field, branch):
    # first generate alpha2 and beta2
    while True:
        alpha2 = field.random_element()
        beta2  = field.random_element()
        c = alpha2**2 - 4*beta2
        if not c.is_square():
            break
    return ([field(0), field(0), alpha2] + [(i-1)*alpha2 for i in range(3, branch)], [field(0), field(0), beta2] + [(i-1)**2*beta2 for i in range(3,branch)])

class Griffin:
    # def __init__(self, field, branch, round, constants_list, beta_eq):
    def __init__(self, field, branch, round, constants_list):
        self.field = field
        self.branch = branch
        self.round = round
        self.constants_list = constants_list
        self.d = compute_exponent(self.field)
        self.d_inv = inverse_mod(self.d, self.field.characteristic()-1)
        self.alpha, self.beta = build_alphas_betas(self.field, self.branch)
        self.gamma = [self.field(0),self.field(0)] + [self.field(i-1) for i in range(2, self.branch)]

        # self.beta_eq = beta_eq

        # build the matrix M from M4, i.e M = circ([2*M4, M4, ..., M4])

        if self.branch == 3 or self.branch == 4:
            self.matrix = matrix_mds("griffin", self.field, self.branch)

        elif self.branch % 4 == 0:
            matrix = matrix_mds("griffin", self.field, 4)
            n=self.branch//4
            blocks = [2*matrix] + [matrix for _ in range(n-1)]
            rows = []
            for i in range(n):
                row_blocks = [blocks[(j - i) % n] for j in range(n)]
                row = block_matrix(1, n, row_blocks)
                rows.append(row)
            self.matrix = block_matrix(n, 1, rows)

        else:
            raise ValueError("The number of branch must be 3, 4, 8, 12, 16, 20 or 24")

    def NonLinearLayer(self, x):
        y = vector([0]*self.branch).change_ring(x.base_ring())

        y[0] = x[0]**self.d_inv
        y[1] = x[1]**self.d
        y[2] = x[2] * G_i(self.alpha[2], self.beta[2], L_i(self.gamma[2], y[0], y[1], 0))

        for i in range(3,self.branch):
            y[i] = x[i] * G_i(self.alpha[i], self.beta[i], L_i(self.gamma[i], y[0], y[1], x[i-1]))

        return y
    
    def LinearLayer(self, x, c_i):
        return self.matrix * x + c_i

    def round_function(self, i, x):
        return self.LinearLayer(self.NonLinearLayer(x), self.constants_list[i])

    def permutation(self, x):
        x = self.matrix * x
        for i in range(self.round):
            x = self.round_function(i, x)
        return x
    
    def NonLinearLayer_CICO1_solve(self, x, new_var):
        y = vector([0]*self.branch).change_ring(x.base_ring())

        y[0] = new_var
        y[1] = pow(x[1], self.d)
        y[2] = x[2] * G_i(self.alpha[2], self.beta[2], L_i(self.gamma[2], y[0], y[1], 0))

        for i in range(3,self.branch):
            y[i] = x[i] * G_i(self.alpha[i], self.beta[i], L_i(self.gamma[i], y[0], y[1], x[i-1]))

        # eq = reduce_degrees_mod_p(x[0] ** int(self.beta_eq), self.field.cardinality()-1) - new_var ** int(mod(self.d * self.beta_eq, self.field.cardinality()-1))
        eq = x[0] - new_var ** int(self.d)
        
        return y, eq
    
    def round_function_CICO1_solve(self, x, i, new_var):
        y, eq = self.NonLinearLayer_CICO1_solve(x, new_var)
        return self.LinearLayer(y, self.constants_list[i]), eq
    
    def permutation_CICO1_solve(self, x, extra_vars):
        system_of_equations = []
        for i in range(len(x)):
            x[i] = x[i] ** self.d
        x = self.matrix * x
        for i in range(self.round):
            x, new_eq = self.round_function_CICO1_solve(x, i, extra_vars[i])
            system_of_equations.append(new_eq)
        # system_of_equations.append(reduce_degrees_mod_p(x[0], self.field.cardinality()-1))
        system_of_equations.append(x[0])
        return system_of_equations
    
# def reduce_degrees_mod_p(f, p):
#     """
#     Réduit les exposants de chaque variable modulo p
#     dans un polynôme multivarié f.
#     """
#     R = f.parent()
#     # print(R)
#     gens = R.gens()
#     # print(gens)
#     result = R.zero()
#     # print(result)

#     for mon, coeff in f.dict().items():
#         new_mon = 1
#         for g, e in zip(gens, mon):
#             # print("mon", mon)
#             new_mon *= g**(e % p)
#             # print("new_mon", new_mon)
#         result += coeff * new_mon

#     return result

def generate_system_of_equations(q, field, order, branch, cico, round, seed, constant_vector_list):

    # p=field.cardinality()

    # inv_element = [a for a in range(p) if gcd(a, p-1) == 1]
    # print([(inv_element[i], i) for i in range(len(inv_element))])
    # print([(mod(3*e, field.cardinality()-1), e) for e in inv_element])
    # beta_eq = inv_element[11]
    # beta_eq = inv_element[17]

    set_random_seed(seed)    

    R = PolynomialRing(field,["X_{}".format(i) for i in range(round+1)], order=order)
    var_list = list(R.gens())

    input = []
    for _ in range(branch-cico):
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

    constants_list = constant_vector_list[:-1] + [constants_zero(field, branch)]
    # permutation = Griffin(field, branch, round, constants_list, beta_eq)
    permutation = Griffin(field, branch, round, constants_list)

    timer_gen_sys_of_eq = Chronograph("Generation system of equations Griffin CICO-{}".format(cico))
    system_of_equations = permutation.permutation_CICO1_solve(input_cico, var_list[1:])
    time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure()

    q.put((system_of_equations, time_gen_sys_of_eq))