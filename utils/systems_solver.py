from sys import argv
import traceback
from sage.all import ideal, PolynomialRing, parent
from sage.libs.singular.option import opt, opt_ctx
from sage.libs.singular.function import singular_function
from pickle import load
from re import search

from utils.pickle_utils import change_dict_pkl
from utils.timer import Chronograph

def is_shape_position_polynomial_var(p, special_var):

    """ Check whether a polynomial has shape x_i - f_i(special_var), where f_i is a univariate polynomial in special_var
    
    :param p: Multivariate polynomial
    :param special_var: Variable from the multivariate polynomial ring

    :returns: Whether or not the polynomial is in shape position form as defined above
    :rtype: boolean
    """

    vars = p.variables() ## Find the variables of p

    if len(vars) != 2 or special_var not in vars: ## If more than 2 variables or special_var not in the vars it is not in shape position
        return False

    xi = next(v for v in vars if v != special_var) ## Find the other variable

    new_pol = p - xi ## Detect if this polynomial is univariate in special_var

    if len(new_pol.variables()) != 1 or new_pol.variables()[0] != special_var:
        return False
    
    return True

def computation_shape_position_and_ideal_degree(gb_lex:list):

    """The choice done in this function is to detect whether the ideal is in shape position.
        If shape position:
            Compute the ideal degree
            Return Shape position and ideal degree (ideal_degree)
        Else:
            Return Not shape position (-1)

        Return -2 in case it is of zero-dimension ideal. It should not happen if FGLM is used as it detects it and crashs before
    
    :param list gb_lex: Gröbner basis for the LEX order

    :returns: degree of the ideal and whether it is radical
    """

    if gb_lex == [1]:
        return 0
    
    else:
        univ_pols_degree = []
        """
            Find all the univariate polynomials and store their degree
        """
        for polynomial in gb_lex:
            if len(polynomial.variables()) == 1:
                univ_pols_degree.append((polynomial.degree(), polynomial.variables()[0]))
        
        if len(univ_pols_degree) == 0:
            return -2 ## Not 0-dimensional ideal
        
        nb_degree_not_one = 0
        for (degree,_) in univ_pols_degree:
            if degree != 1:
                nb_degree_not_one += 1
        
        if nb_degree_not_one > 1:
            return -1 ## Not in shape position

        else: ## We have at most one univariate polynomial such that degree > 1, we know have to detect whether it is in shape position
            for (degree, var) in univ_pols_degree:
                if degree != 1:
                    special_var = var

        degree = 0
        isRadical = False

        for polynomial in gb_lex:
            if len(polynomial.variables()) == 1 and polynomial.variables()[0] == special_var:
                R = polynomial.parent()

                ### We need the weight of the variable to divide the polynomial degree
                if R.term_order().weights() is not None: 
                    special_var_weight = R.term_order().weights()[R.gens().index(special_var)]
                else:
                    special_var_weight = 1
                degree = polynomial.degree()//special_var_weight
                field = polynomial.parent().base()
                R_univ = PolynomialRing(field, special_var)
                polynomial_univ = R_univ(polynomial)
                polynomial_univ_derivative = polynomial_univ.derivative()
                g = polynomial_univ_derivative.gcd(polynomial_univ)

                if g.degree() == 0:
                    isRadical = True

            elif len(polynomial.variables()) == 1 and polynomial.variables()[0] != special_var: ## this one is of degree one as checked before
                continue
            else:
                if not is_shape_position_polynomial_var(polynomial, special_var): ### test if the polynomial is in shape position
                    return -1, "Not shape position"
        
        return degree, isRadical
    
def solve(file_log_result_path:str, file_output_result_path:str, i:int, number_test:int, system_of_equations:list, algo_gb:str, monomial_order:str, algo_order_change:str, options:dict[str, list[dict[str, any]]]=None):

    """Compute the LEX groebner basis either by computing straight LEX or Monomial Order and Change order algorithm
    
    :param str file_log_result_path: Path to the log file
    :param str file_output_result_path: Path to the file containing result
    :param int i: Number of the system of equations to solve
    :param int number_test: Total number of systems of equations to solve
    :param list system_of_equations: System of equations to solve
    :param str algo_gb: Algorithm to compute the Gröbner basis
    :param str monomial_order: Monomial order to use for the computation of the first Gröbner basis
    :param str algo_order_change: Algorithm to use for the temr order change step
    :param dict[str, list[dict[str, any]]] options: Options for the Gröbner basis algorithm
    
    """

    ### Reset the options of Singular library
    opt.reset_default()

    R = system_of_equations[0].parent()
    field = R.base()
    variables_list = R.gens()
    reverse_variables_list = list(reversed(variables_list))

    R_reversed = PolynomialRing(field, reverse_variables_list, order=monomial_order) ### We reverse the order of the variable list as the last ones must be the one not to eliminate (for dimension 0, it is X_0)

    new_system_of_equations = []

    for equation in system_of_equations:
        equation = R_reversed(equation)
        new_system_of_equations.append(equation)

    I = ideal(new_system_of_equations)
    
    ### Init the solving degree to -1
    solving_degree = -1

    timer_find_groebner_basis = Chronograph("Gröbner basis computation using {}".format(algo_gb)) 

    ### Try to compute the first Gröbner basis

    try:
        if algo_gb.startswith("libsingular"):

            if algo_gb == 'libsingular:groebner_direct':

                if options is not None:
                    with opt_ctx(**options):
                        groebner = singular_function('groebner')
                        groebner_basis = groebner(I)

                else:
                    groebner = singular_function('groebner')
                    groebner_basis = std(I)

            elif algo_gb == 'libsingular:std_direct':

                if options is not None:
                    with opt_ctx(**options):
                        std = singular_function('std')
                        groebner_basis = std(I)

                else:
                    std = singular_function('std')
                    groebner_basis = std(I)

            elif algo_gb == 'libsingular:slimgb_direct':

                if options is not None:
                    with opt_ctx(**options):
                        slimgb = singular_function('slimgb')
                        groebner_basis = slimgb(I)

                else:
                    slimgb = singular_function('slimgb')
                    groebner_basis = slimgb(I)

            elif algo_gb == 'libsingular:stdhilb_direct':

                if options is not None:
                    with opt_ctx(**options):
                        stdhilb = singular_function('stdhilb')
                        groebner_basis = stdhilb(I)

                else:
                    stdhilb = singular_function('stdhilb')
                    groebner_basis = stdhilb(I)

            elif algo_gb == 'libsingular:stdfglm_direct':

                if options is not None:
                    with opt_ctx(**options):
                        stdfglm = singular_function('stdfglm')
                        groebner_basis = stdfglm(I)

                else:
                    stdfglm = singular_function('stdfglm')
                    groebner_basis = stdfglm(I)

            elif algo_gb == 'libsingular:sba_direct':

                if options is not None:

                    if "orders" in options.keys():
                        internal_module_order = options["orders"][0] ### https://www.singular.uni-kl.de/Manual/4-0-3/sing_391.htm#SEC430
                        rewrite_order = options["orders"][1] ### https://www.singular.uni-kl.de/Manual/4-0-3/sing_391.htm#SEC430
                        options.pop("orders", None)
                        with opt_ctx(**options):
                            sba = singular_function('sba')
                            groebner_basis = sba(I, internal_module_order, rewrite_order)
                    
                    else:
                        with opt_ctx(**options):
                            sba = singular_function('sba')
                            groebner_basis = sba(I)

                else:
                    sba = singular_function('sba')
                    groebner_basis = sba(I)

            else:

                if options is not None: 
                    if "prot" in options.keys():
                        prot = options["prot"]
                        options.pop("prot", None)
                        with opt_ctx(**options):
                            groebner_basis = I.groebner_basis(algo_gb, prot=prot)
                    else:
                        with opt_ctx(**options):
                            groebner_basis = I.groebner_basis(algo_gb)

                else:
                    groebner_basis = I.groebner_basis(algo_gb)

        elif algo_gb.startswith("singular"):

            if options is not None: 
                if "prot" in options.keys():
                    prot = options["prot"]
                    options.pop("prot", None)
                    with opt_ctx(**options):
                        groebner_basis = I.groebner_basis(algo_gb, prot=prot)
                    options["prot"] = prot
                else:
                    with opt_ctx(**options):
                        groebner_basis = I.groebner_basis(algo_gb)

            else:
                groebner_basis = I.groebner_basis(algo_gb)

        elif algo_gb == "magma:GroebnerBasis":

            if options is not None:

                groebner_basis = I.groebner_basis(algo_gb, prot=options["prot"])

            else:

                groebner_basis = I.groebner_basis(algo_gb)

        elif algo_gb == "giac:gbasis":

            ### invlex is not supported by Giac, we reverse the variables in the ring and use the lex order to have the same behaviour as invlex.

            if monomial_order == "invlex" or monomial_order == "Inverse lexicographic term order":
                R_giac_invlex = PolynomialRing(field, variables_list, order="lex")
                I = ideal([R_giac_invlex(equation) for equation in system_of_equations])
                groebner_basis = I.groebner_basis(algo_gb)

            else:
                groebner_basis = I.groebner_basis(algo_gb)

        elif algo_gb.startswith("eliminate:giac:"):

            ### Use the elimination_ideal function of Sage with Giac

            variables_to_eliminate_number = int(algo_gb[-1])
            variables_to_eliminate = variables_list[variables_to_eliminate_number+1:]
            groebner_basis = list(set(I.elimination_ideal(variables_to_eliminate, algorithm='giac:eliminate').gens()))
            vars_to_keep = [variables_list[i] for i in range(variables_to_eliminate_number+1)]

            groebner_basis_reduced = []

            for e in groebner_basis:
                if set(e.variables()) <= set(vars_to_keep) and e != field(0):
                    groebner_basis_reduced.append(e)

            groebner_basis_reduced = list(set(groebner_basis_reduced))
            groebner_basis=groebner_basis_reduced

        elif algo_gb.startswith("eliminate:libsingular:"):

            ### Use the elimination_ideal function of Sage with Singular

            variables_to_eliminate_number = int(algo_gb[-1])
            variables_to_eliminate = variables_list[variables_to_eliminate_number+1:]
            groebner_basis = list(set(I.elimination_ideal(list(reversed(variables_to_eliminate)), algorithm='libsingular:eliminate').gens()))

        else :

            """
                Only "prot" option is supported for now for Magma and Giac
                No options are available for msolve and Macaulay2
            """

            if options is not None:

                if algo_gb.startswith("msolve") or algo_gb.startswith("macaulay2"):
                    print("No option is possible for this algorithm")
                    groebner_basis = I.groebner_basis(algo_gb)

                else :
                    groebner_basis = I.groebner_basis(algo_gb, prot=options["prot"])

            else:

                groebner_basis = I.groebner_basis(algo_gb)

        groebner_computation_time = timer_find_groebner_basis.time_measure()

        ### Depending on the algorithm used to compute the Gröbner basis, the solving degree is returned. Then, we read the log file to return it

        if options is not None and "prot" in options.keys() and options["prot"] == "sage" and (algo_gb.startswith("singular") or algo_gb.startswith("magma:GroebnerBasis")):

            print("Intermediate Gröbner basis computed", flush=True)

            with open(file_log_result_path, "r") as f:
                last_line = f.readlines()[-2].strip()
            
            match = search(r":\s*(\d+)", last_line)
            if match:
                solving_degree = int(match.group(1))

        change_dict_pkl(file_output_result_path, i, number_test, "groebner_time", groebner_computation_time)
        change_dict_pkl(file_output_result_path, i, number_test, "solving_degree", solving_degree)
        
    except Exception as e:
        print(f"Error Gröbner computation: {e}")
        print(traceback.format_exc())
        return

    """
        Redefine the ideal from the Gröbner basis computed.
        Then we want to find a Gröbner basis for the LEX order.
    """

    I = ideal(groebner_basis)

    ### Compute the dimension of the ideal, what is supposed to be efficient starting from a Gröbner basis
    ideal_dimension = I.dimension() ### Too much time in some cases for positive dimension
    # ideal_dimension = 1 ### Possible to fix the dimension here

    change_dict_pkl(file_output_result_path, i, number_test, "ideal_dimension", ideal_dimension)

    if ideal_dimension > 0 and algo_order_change == "fglm":
        print("FGLM can't be used to compute a LEX basis for a positive dimensional ideal")
        change_dict_pkl(file_output_result_path, i, number_test, "transformation_basis_time", "Positive dimension for FLGM")
        change_dict_pkl(file_output_result_path, i, number_test, "ideal_degree", "Positive dimension for FLGM")
        change_dict_pkl(file_output_result_path, i, number_test, "shape_position", "Positive dimension for FLGM")
    
        return
    try:

        if monomial_order == "lex" or monomial_order == "Lexicographic term order" or monomial_order == "invlex" or monomial_order == "Inverse lexicographic term order" or monomial_order == "neglex" or algo_gb.startswith("eliminate"):
            """
                The original order is an elimination then nothing has to be done.
            """
            transformation_computation_time = 0
            new_groebner_basis = groebner_basis

        else:

            """
                Transform from the first order to an elimination order (lex by default)
            """

            timer_transform_groebner_basis = Chronograph("Transforming Groebner basis using {}".format(algo_order_change)) 
            new_groebner_basis = I.transformed_basis(algo_order_change)
            transformation_computation_time = timer_transform_groebner_basis.time_measure()
        
        change_dict_pkl(file_output_result_path, i, number_test, "transformation_basis_time", transformation_computation_time)

        if ideal_dimension == 0:
            
            ideal_degree, isRadical = computation_shape_position_and_ideal_degree(new_groebner_basis)
            print("Ideal degree:", ideal_degree, flush=True)
            I = ideal(new_groebner_basis)
            if ideal_degree == -1 or ideal_degree == -2:
                ideal_degree_singular = I.vector_space_dimension() #### This function may take a long time to be computed
                print("\nIdeal degree Singular:", ideal_degree_singular, flush=True)
            else:
                ideal_degree_singular = ideal_degree

            if ideal_degree == -1:
                shape_position = False
            else:
                shape_position = True
            
            change_dict_pkl(file_output_result_path, i, number_test, "ideal_degree", ideal_degree_singular)
            change_dict_pkl(file_output_result_path, i, number_test, "shape_position", shape_position)
            change_dict_pkl(file_output_result_path, i, number_test, "radical_ideal", isRadical)


        elif ideal_dimension == -1:

            change_dict_pkl(file_output_result_path, i, number_test, "ideal_degree", "Full Ring")
            change_dict_pkl(file_output_result_path, i, number_test, "shape_position", "Full Ring")
            change_dict_pkl(file_output_result_path, i, number_test, "radical_ideal", "Full Ring")

        else:

            change_dict_pkl(file_output_result_path, i, number_test, "ideal_degree", "Positive dimension")
            change_dict_pkl(file_output_result_path, i, number_test, "shape_position", "Positive dimension")
            change_dict_pkl(file_output_result_path, i, number_test, "radical_ideal", "Positive dimension")

        ### Print the last element of the lex Gröbner basis. For 0 dimensionnal ideal, the univariate polynomial is returned

        for e in new_groebner_basis:
            if set(e.variables()) <= set([variables_list[i] for i in range(ideal_dimension+1)]) and e != field(0):
                print("Generator of the elimination ideal:", e, "\n", flush=True)

    except Exception as e:
        print(f"Error Transformation computation: {e}")

if __name__ == "__main__":

    input_file = argv[1]

    ### The inputs of the solve function are stored in a file

    with open(input_file, "rb") as f:
        (file_log_result_path, file_output_result_path, i, number_test, system_of_equations, algo_gb, monomial_order, algo_order_change, options) = load(f)
    f.close()

    solve(file_log_result_path, file_output_result_path, i, number_test, system_of_equations, algo_gb, monomial_order, algo_order_change, options=options)
