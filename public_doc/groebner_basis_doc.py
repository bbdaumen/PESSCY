from sage.all import *
from sage.libs.singular.option import opt_verb
from sage.libs.singular.option import opt

#### Gröbner basis algorithm

algos_singular = ['singular:groebner', 'singular:std', 'singular:slimgb', 'singular:stdhilb', 'singular:stdfglm'] ### The algorithms to use for Singular
algos_libsingular  = ['libsingular:groebner', 'libsingular:std', 'libsingular:slimgb', 'libsingular:stdhilb', 'libsingular:stdfglm']
algos_libsingular_direct  = ['libsingular:groebner_direct', 'libsingular:std_direct', 'libsingular:slimgb_direct', 'libsingular:stdhilb_direct', 'libsingular:stdfglm_direct', 'libsingular:sba_direct']
algos_macaulay2 = ['macaulay2:gb', 'macaulay2:f4', 'macaulay2:mgb']
algos_giac = ['giac:gbasis']
algos_msolve = ['msolve']
algos_magma = ['magma:GroebnerBasis']
eliminate = ["eliminate:giac:i", "eliminate:libsingular:i"] ### Elimination ideal functions, i is the number of variables to keep in the elmination ideal

#### Term order change algorithm

algos_term_order = ["fglm", "gwalk", "awalk1", "awalk2", "twalk", "fwalk"]

#### Singular options

print("Options \n")

# opt['prot'] = True

# print("returnSB :", opt['returnSB']) ## not used for Gröbner basis
# print("fastHC :", opt['fastHC']) ## not used for global orderings
print("intStrategy :", opt['intStrategy']) 
# print("lazy :", opt['lazy']) ## not supported 
# print("length :", opt['length']) ## not supported 
print("notSugar :", opt['notSugar'])
print("notBuckets :", opt['notBuckets'])
print("oldStd :", opt['oldStd'])
print("prot :", opt['prot'])
print("redSB :", opt["redSB"])
print("redTail :", opt["redTail"])
print("redThrough :", opt["redThrough"])
print("sugarCrit :", opt['sugarCrit'])
print("weightM :", opt["weightM"])
# print("degBound :", opt["degBound"]) ## not relevant in our case, as we need the Gröbner bases and the input is inhomogeneous
# print("multBound :", opt["multBound"])## not relevant for global orderings

#### Verbosity options

print("\nVerbosity Options \n")

print("mem :", opt_verb["mem"])
print("yacc :", opt_verb["yacc"])
print("redefine :", opt_verb["redefine"])
print("reading :", opt_verb["reading"])
print("loadLib :", opt_verb["loadLib"])
print("debugLib :", opt_verb["debugLib"])
print("loadProc :", opt_verb["loadProc"])
print("defRes :", opt_verb["defRes"])
print("usage :", opt_verb["usage"])
print("Imap :", opt_verb["Imap"])
print("notWarnSB :", opt_verb["notWarnSB"])
print("contentSB :", opt_verb["contentSB"])
print("cancelunit :", opt_verb["cancelunit"])


#### Code for std options

from itertools import product

keys = ["intStrategy", "notSugar", "notBuckets", "oldStd", "redSB", "redTail", "redThrough", "sugarCrit", "weightM"]

# weightM : keep to False

fixed = {"prot": False}
combinations = list(product([False, True], repeat=len(keys)))
options_singular_std = []

for combo in combinations:
    d = dict(zip(keys, combo))
    d.update(fixed)  # ajouter prot=True
    options_singular_std.append(d)

#### Singular sba options

"""
    options_singular_sba = [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1), (3,0), (3,1)] #### For details https://www.singular.uni-kl.de/Manual//4-0-3/sing_391.htm#SEC430 so optional arguments are (internal module order, rewrite order)
"""