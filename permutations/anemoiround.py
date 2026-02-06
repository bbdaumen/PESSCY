from sage.all import *
import itertools
from utils.timer import *
# Linear layer generation

def is_mds(m):
    # Uses the Laplace expansion of the determinant to calculate the (m+1)x(m+1) minors in terms of the mxm minors.
    # Taken from https://github.com/mir-protocol/hash-constants/blob/master/mds_search.sage.

    # 1-minors are just the elements themselves
    if any(any(r == 0 for r in row) for row in m):
        return False

    N = m.nrows()
    assert m.is_square() and N >= 2

    det_cache = m

    # Calculate all the nxn minors of m:
    for n in range(2, N+1):
        new_det_cache = dict()
        for rows in itertools.combinations(range(N), n):
            for cols in itertools.combinations(range(N), n):
                i, *rs = rows

                # Laplace expansion along row i
                det = 0
                for j in range(n):
                    # pick out c = column j; the remaining columns are in cs
                    c = cols[j]
                    cs = cols[:j] + cols[j+1:]

                    # Look up the determinant from the previous iteration
                    # and multiply by -1 if j is odd
                    cofactor = det_cache[(*rs, *cs)]
                    if j % 2 == 1:
                        cofactor = -cofactor

                    # update the determinant with the j-th term
                    det += m[i, c] * cofactor

                if det == 0:
                    return False
                new_det_cache[(*rows, *cols)] = det
        det_cache = new_det_cache
    return True

def M_2(x_input, b):
    """Fast matrix-vector multiplication algorithm for Anemoi MDS layer with l = 1,2."""

    x = x_input[:]
    x[0] += b*x[1]
    x[1] += b*x[0]
    return x

def M_3(x_input, b):
    """Fast matrix-vector multiplication algorithm for Anemoi MDS layer with l = 3.

    From Figure 6 of [DL18](https://tosc.iacr.org/index.php/ToSC/article/view/888)."""

    x = x_input[:]
    t = x[0] + b*x[2]
    x[2] += x[1]
    x[2] += b*x[0]
    x[0] = t + x[2]
    x[1] += t
    return x


def M_4(x_input, b):
    """Fast matrix-vector multiplication algorithm for Anemoi MDS layer with l = 4.

    Figure 8 of [DL18](https://tosc.iacr.org/index.php/ToSC/article/view/888)."""

    x = x_input[:]
    x[0] += x[1]
    x[2] += x[3]
    x[3] += b*x[0]
    x[1]  = b*(x[1] + x[2])
    x[0] += x[1]
    x[2] += b*x[3]
    x[1] += x[2]
    x[3] += x[0]
    return x


def circulant_mds_matrix(field, l, coeff_upper_limit=None):
    if coeff_upper_limit == None:
        coeff_upper_limit = l+1
    assert(coeff_upper_limit > l)
    for v in itertools.combinations_with_replacement(range(1,coeff_upper_limit), l):
        mat = matrix.circulant(list(v)).change_ring(field)
        if is_mds(mat):
            return(mat)
    # In some cases, the method won't return any valid matrix,
    # hence the need to increase the limit further.
    return circulant_mds_matrix(field, l, coeff_upper_limit+1)

def get_mds(field, l):
    if l == 1:
        return identity_matrix(field, 1)
    if l <= 4: # low addition case
        a = field.multiplicative_generator()
        b = field.one()
        t = 0
        while True:
            # we construct the matrix
            mat = []
            b = b*a
            t += 1
            for i in range(0, l):
                x_i = [field.one() * (j == i) for j in range(0, l)]
                if l == 2:
                    mat.append(M_2(x_i, b))
                elif l == 3:
                    mat.append(M_3(x_i, b))
                elif l == 4:
                    mat.append(M_4(x_i, b))
            mat = Matrix(field, l, l, mat).transpose()
            if is_mds(mat):
                return mat
    else: # circulant matrix case
        return circulant_mds_matrix(field, l)

# AnemoiPermutation class

class AnemoiPermutation:
    def __init__(self,
                 n_rounds,
                 q,
                 constant_vector_list,
                 alpha=None,
                 mat=None,
                 n_cols=1,
                 security_level=128):

        self.q = q
        self.prime_field = is_prime(q)  # if true then we work over a
                                        # prime field with
                                        # characteristic just under
                                        # 2**N, otherwise the
                                        # characteristic is 2**self
        self.n_cols = n_cols # the number of parallel S-boxes in each round
        self.security_level = security_level

        self.F = GF(self.q)
        if self.prime_field:
            if alpha != None:
                if gcd(alpha, self.q-1) != 1:
                    raise Exception("alpha should be co-prime with the characteristic!")
                else:
                    self.alpha = alpha
            else:
                self.alpha = 3
                while gcd(self.alpha, self.q-1) != 1:
                    self.alpha += 1
            self.QUAD = 2
            self.to_field   = lambda x : self.F(x)
            self.from_field = lambda x : Integer(x)
        else:
            self.alpha = 3
            self.QUAD = 3
            self.to_field   = lambda x : self.F.fetch_int(x)
            self.from_field = lambda x : x.integer_representation()
        self.g = self.F.multiplicative_generator()
        self.beta = self.g
        self.delta = self.g**(-1)
        self.alpha_inv = inverse_mod(self.alpha, self.q-1)

        self.n_rounds = n_rounds

        self.C = []
        self.D = []
        for r in range(0, self.n_rounds):
            self.C.append(list(constant_vector_list[r])[:self.n_cols])
            self.D.append(list(constant_vector_list[r])[self.n_cols:])

        self.mat = get_mds(self.F, self.n_cols)

# !SECTION! Sub-components

def linear_layer(mat, _x, _y):

    x, y = _x[:], _y[:]
    x = mat*vector(x)
    y = mat*vector(y[1:] + [y[0]])

    # Pseudo-Hadamard transform on each (x,y) pair
    y += x
    x += y
    return list(x), list(y)

def get_polynomial_variables(field, order, round, branch):
    """Returns polynomial variables from the appropriate multivariate
    polynomial ring to work with this Anemoi instance.

    """
    n_cols = branch//2
    n_rounds= round
    x_vars = []
    y_vars = []
    all_vars = []
    for r in range(0, n_rounds+1):
        # x_vars.append(["X{:02d}{:02d}".format(r, i) for i in range(0, n_cols)])
        # y_vars.append(["Y{:02d}{:02d}".format(r, i) for i in range(0, n_cols)])
        x_vars.append(["X_{}".format(n_cols * r + i) for i in range(0, n_cols)])
        all_vars += x_vars[-1]
    for r in range(0, n_rounds+1):
        y_vars.append(["X_{}".format((n_cols * r + i) + n_cols * (n_rounds+1)) for i in range(0, n_cols)])
        all_vars += y_vars[-1]

    pol_ring = PolynomialRing(field, (n_rounds+1)*2*n_cols, all_vars, order=order)
    pol_gens = pol_ring.gens()
    result = {"X" : [], "Y" : []}
    for r in range(0, n_rounds+1):
        result["X"].append([])
        result["Y"].append([])
        for i in range(0, n_cols):
            result["X"][r].append(pol_gens[n_cols*2*r + i])
            result["Y"][r].append(pol_gens[n_cols*2*r + i + n_cols])
    
    return result


def verification_polynomials(pol_vars, mat, alpha, QUAD, beta, delta, round, branch, cico, constant_vector_list):
    """Returns the list of all the equations that all the intermediate
    values must satisfy. It implicitely relies on the open Flystel
    function."""
    n_cols = branch//2
    n_rounds= round

    C = []
    D = []
    for r in range(0, n_rounds):
        C.append(list(constant_vector_list[r])[:n_cols])
        D.append(list(constant_vector_list[r])[n_cols:])
    equations = []

    assert cico <= len(pol_vars["X"][0]) + len(pol_vars["Y"][0])

    for r in range(0, n_rounds):

        # the outputs of the open flystel are the state variables x, y at round r+1
        u = pol_vars["X"][r+1]
        v = pol_vars["Y"][r+1]
        # the inputs of the open flystel are the state variables
        # x, y at round r after undergoing the constant addition
        # and the linear layer
        x, y = pol_vars["X"][r], pol_vars["Y"][r]

        if r == 0:
            cpt = 0
            while cpt <= cico-1:
                if cpt <= n_cols -1:
                    equations.append(x[cpt])
                else:
                    equations.append(y[cpt-n_cols])
                cpt +=1


        x = [x[i] + C[r][i] for i in range(0, n_cols)]
        y = [y[i] + D[r][i] for i in range(0, n_cols)]
        x, y = linear_layer(mat, x, y)
        for i in range(0, n_cols):
            equations.append(
                (y[i]-v[i])**alpha + beta*y[i]**QUAD + delta - x[i]
            )
            equations.append(
                (y[i]-v[i])**alpha + beta*v[i]**QUAD - u[i]
            )

        if r == n_rounds - 1:
            u, v = linear_layer(mat, u, v)
            cpt = 0
            while cpt <= cico-1:
                if cpt <= n_cols -1:
                    equations.append(u[cpt])
                else:
                    equations.append(v[cpt-n_cols])
                cpt +=1

    return equations


def generate_system_of_equations(q, field, order, branch, cico, round, seed, constant_vector_list):
    """Simply prints the equations modeling a full call to this
    AnemoiPermutation instance in a user (and computer) readable
    format.

    The first lines contains a comma separated list of all the
    variables, and the second contains the field size. The
    following ones contain the equations. This format is intended
    for use with Magma.

    """
    set_random_seed(seed)
    p = field.characteristic()
    if is_prime(p):
        alpha = 3
        while gcd(alpha, p-1) != 1:
            alpha += 1
        QUAD = 2
    else:
        alpha = 3
        QUAD = 3
    g = field.multiplicative_generator()
    beta = g
    delta = g**(-1)
    mat = get_mds(field, branch//2)

    try:
        timer_gen_sys_of_eq = Chronograph("Generation system of equations Anemoi Round CICO-{}".format(cico))
        p_vars = get_polynomial_variables(field, order, round, branch)
        eqs = verification_polynomials(p_vars, mat, alpha, QUAD, beta, delta, round, branch, cico, constant_vector_list)
        time_gen_sys_of_eq = timer_gen_sys_of_eq.time_measure() 

    except Exception as e:
        eqs = None
        time_gen_sys_of_eq = None

    q.put((eqs, time_gen_sys_of_eq))