from sage.all import *
from utils.timer import *
import random

############### Sparsity concept ###############

## Compute the number of monomials of maximal_degree with nb_var variables

def number_monomials(max_degree, nb_var):
    nb_monomials = 0
    for d in range(max_degree+1):
        for k in range(1, nb_var+1):
            nb_monomials += binomial(d-1, k-1) * binomial(nb_var, k)
    return nb_monomials

## Compute the sparsity of a polynomial

def sparsity_polynomial(nb_monomials, max_degree, nb_var):
    return Rational(nb_monomials/number_monomials(max_degree,nb_var))


def random_ideal_sparse_degree_variable(polynomial_ring, monomials_degree_variables_vector, seed):
    set_random_seed(seed)
    random.seed(seed)

    nb_equations = len(monomials_degree_variables_vector)

    field = polynomial_ring.base_ring()
    order = polynomial_ring.term_order()

    system_of_equations = []
    for i in range(nb_equations):
        nb_monomial_polynomial, variable_index_list, max_degree_polynomial = monomials_degree_variables_vector[i] 

        nb_var = len(variable_index_list)

        vector_list = [field(1)] * nb_monomial_polynomial + [field(0)] * (number_monomials(max_degree_polynomial, nb_var) - nb_monomial_polynomial)
        new_polynomial_ring = PolynomialRing(field, ["X_{}".format(i) for i in variable_index_list], order=order)
        polynomial = new_polynomial_ring(0)
        
        while polynomial.degree() != max_degree_polynomial:
            random.shuffle(vector_list)
            polynomial = 0
            cpt = 0
            if nb_var == 1:
                var = polynomial_ring.gens()[variable_index_list[0]]
                for i in range(max_degree_polynomial+1):
                    monomial = var**i
                    if vector_list[cpt] == field(1):
                        coef = field.random_element()
                        while coef == field(0):
                            coef = field.random_element()
                        polynomial += coef * monomial
                    cpt += 1
            else:
                for i in range(max_degree_polynomial+1):
                    monomials_deg = new_polynomial_ring.monomials_of_degree(i)
                    for monomial in monomials_deg:
                        if vector_list[cpt] == field(1):
                            coef = field.random_element()
                            while coef == field(0):
                                coef = field.random_element()
                            polynomial += coef * monomial
                        cpt += 1

        system_of_equations.append(polynomial_ring(polynomial))

    return system_of_equations


def generate_system_of_equations(q, field, order, monomials_degree_variables_vector, seed):

    var_index_list = []

    for polynomial_description in monomials_degree_variables_vector:
        var_index_list += polynomial_description[1]

    var_index_list = sorted(list(set(var_index_list)))
    nb_var = len(var_index_list)

    polynomial_ring = PolynomialRing(field,["X_{}".format(i) for i in var_index_list], order=order)

    timer_gen_sys_of_eq = Chronograph("Random systems CICO-{}".format(nb_var))
    system_of_equations = random_ideal_sparse_degree_variable(polynomial_ring, monomials_degree_variables_vector, seed)
    time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure()

    q.put((system_of_equations, time_gen_sys_of_eq))