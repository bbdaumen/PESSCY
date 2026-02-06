from pickle import load
import numpy as np
import math

ALGOS_COLOR = {
    'libsingular:groebner': '#1f77b4',
    'libsingular:std': '#ff7f0e',
    'libsingular:slimgb': '#2ca02c',
    'libsingular:stdhilb': '#d62728',
    'libsingular:stdfglm': '#9467bd',
    'libsingular:sba': '#000000',

    'singular:groebner': '#1f77b4',
    'singular:std': '#ff7f0e',
    'singular:slimgb': '#2ca02c',
    'singular:stdhilb': '#d62728',
    'singular:stdfglm': '#9467bd',

    'libsingular:groebner_direct': '#8c564b',
    'libsingular:std_direct': '#e377c2',
    'libsingular:slimgb_direct': '#7f7f7f',
    'libsingular:stdhilb_direct': "#d627a1",
    'libsingular:stdfglm_direct': "#67bd8e",
    'libsingular:sba_direct': '#000000',

    'macaulay2:gb': '#17becf',
    'macaulay2:f4': '#8dd3c7',
    'macaulay2:mgb': '#ff9896',

    'giac:gbasis': '#bcbd22',

    'msolve': '#24378e',

    'magma:GroebnerBasis': "#86152D",

    'eliminate:giac': '#8f7ffe',
    'eliminate:libsingular': '#123456',

    'fglm': '#1f77b4',
    'gwalk': '#ff7f0e',
    'awalk1': '#2ca02c',
    'awalk2': '#d62728',
    'twalk': '#9467bd',
    'fwalk': '#8c564b'

    }

ALGOS_MARKER= {
    'libsingular:groebner': '.',
    'libsingular:std': 'v',
    'libsingular:slimgb': 'x',
    'libsingular:stdhilb': '+',
    'libsingular:stdfglm': 's',

    'singular:groebner': '.',
    'singular:std': 'v',
    'singular:slimgb': 'x',
    'singular:stdhilb': '+',
    'singular:stdfglm': 's',

    'giac:gbasis': '*',
    'msolve': 'p',
    'magma:GroebnerBasis': "o",

    'eliminate:giac': "d",
    'eliminate:libsingular': "1",

    'fglm': '.',
    'gwalk': 'v',
    'awalk1': 'x',
    'awalk2': '+',
    'twalk': 's',
    'fwalk': '*'
    }

NAMES_NICE_PRINTING = {
    'permutation' : 'Permutation',
    'algo_gb' : 'Gröbner basis algorithm',
    'algo_order_change' : 'Term change order algorithm',
    'field_char' : 'Field characteristic',
    'cico' : 'CICO',
    'round' : 'Round',
    'branch' : 'Branch',
    'constant_sparsity' : 'Constant sparsity',
    'monomial_order' : 'Monomial order',
    'number_test' : 'Number test',

    'system_of_equation_shape' : 'System of equation shape',
    'generation_time' : 'Generation time',
    'groebner_time' : 'Gröbner time',
    'regularity_degree' : 'Regularity degree',
    'transformation_basis_time' : 'Term order change time',
    'ideal_degree' : 'Ideal degree'
    }

def all_equals(list:list):

    """Are all the elements of the list equal?
    
    :param list: Input list

    """

    return all(x == list[0] for x in list) if list else True

def all_none(list:list):

    """Are all the elements of the list None or np.nan?
    
    :param list: Input list

    """

    return all(x is None or x is np.nan for x in list) if list else True

def all_inf_lowerbound(list:list, lowerbound:int):

    """
        Are all the elements of the list inferior to a lowerbound?
    """

    return all(x < lowerbound for x in list if x is not None) if list else True


def statistics_analysis(data_list:list, algo_time_computed:str):

    """

    Compute mean and standard deviation of the list (log)
    
    :param data_list: List of data
    :type data_list: list
    :param algo_time_computed: Key of the items to analyse in the dictionnary
    :type algo_time_computed: str
    
    """

    times = []

    for data in data_list:
        time = data[algo_time_computed]
        if time in ["timeout", "skipped", "failed", "timeout_generation", "Positive dimension for FLGM"] or time == 0:
            continue

        else:
            times.append(np.log10(time))

    if len(times) == 0:
        return np.nan, np.nan
    
    mean_time = np.mean(times)
    ecart_type_time = np.std(times)

    return mean_time, ecart_type_time


def statistics_analysis_no_log(data_list:list[dict], algo_time_computed:str):

    """

    Compute mean and standard deviation of the list (no log)
    
    :param data_list: List of data
    :type data_list: list
    :param algo_time_computed: Key of the items to analyse in the dictionnary
    :type algo_time_computed: str
    
    """

    times = []

    for data in data_list:
        time = data[algo_time_computed]
        if time in ["timeout", "skipped", "failed", "timeout_generation", "Positive dimension", "Positive dimension for FLGM"]:
            continue

        else:
            times.append(time)

    if len(times) == 0:
        return np.nan, np.nan
    
    
    if len(times) == 1:
        return times[0], 0
    
    mean_time = float(np.mean(times))
    ecart_type_time = float(np.std(times))

    if math.floor(mean_time) == mean_time:
        mean_time = math.floor(mean_time)
    
    if math.floor(ecart_type_time) == ecart_type_time:
        ecart_type_time = math.floor(ecart_type_time)

    return mean_time, ecart_type_time

def first_monomial_order_plus_transformation_statistics_analysis(data_list:list[dict]):

    """
    Compute mean and standard deviation of the addition of the computation of the Gröbner basis and the term order change (log)
    
    :param data_list: List of data
    :type data_list: list[dict]
    
    """    

    times = []

    for data in data_list:
        time_gb = data["groebner_time"]
        time_tf = data["transformation_basis_time"]
        if time_gb in ["timeout", "skipped", "failed"] or time_tf in ["timeout", "skipped", "failed"]:
            continue
        else:
            times.append(np.log10(time_gb + time_tf))

    if len(times) == 0:
        return np.nan, np.nan
    
    mean_time = np.mean(times)
    ecart_type_time = np.std(times)

    return mean_time, ecart_type_time

def read_pickle_parameters(folder_results:str):

    """
    Read the file containing all the parameter dictionnaries for the experiment

    :param folder_results: Name of the folder with results
    :type folder_results: str

    """

    parameters = []
    with open("./" + folder_results + "/parameters.pkl", "rb") as f_pkl:
        try:
            while True :
                parameters.append(load(f_pkl))
        except EOFError:
            pass
    return parameters

def read_pickle_parameter_id(folder_results:str, id:int):

    """
    Read the parameter dictionnary corresponding to a certain ID
    
    :param folder_results: Name of the folder with results
    :type folder_results: str
    :param id: Numberof ID of the experiment
    :type id: int
    
    """

    i = -1
    with open("./" + folder_results + "/parameters.pkl", "rb") as f_pkl:
        while i != id :
            try:
                param = load(f_pkl)
            except EOFError:
                print("Error")
            i += 1
    return param

def read_pickle_experiment(folder_results:str, id:int):

    """
    Read the result dictionnary corresponding to a certain ID
    
    :param folder_results: Name of the folder with results
    :type folder_results: str
    :param id: Numberof ID of the experiment
    :type id: int

    """

    data_list = []

    filename = "./" + folder_results + "/res/" + str(id) + ".pkl"
    try :
        with open(filename, "rb") as f_pkl:
            while True:
                try:
                    data = load(f_pkl)
                    data_list.append(data)
                except EOFError:
                    return data_list
    except Exception as e:
        return None

def read_all_experiments(folder_results:str):

    """
    Read all the result dictionnaries for the experiment
    
    :param folder_results: Name of the folder with results
    :type folder_results: str
    
    """

    id = 1
    while True:
        filename = "./" + folder_results + "/res/" + str(id) + ".pkl"
        try :
            with open(filename, "rb") as f_pkl:
                try:
                    data = load(f_pkl)
                except EOFError:
                    print("Cannot read data")
        except Exception as e:
            print("Error reading id", id)

        id += 1

def dict_keys_equal_except_keys_specified(d1:dict, d2:dict, keys_to_ignore:list=None):

    """
    Return if two dictionnaries have the same values for all the keys except the ones in the list keys_to_ignore
    
    :param d1: First dictionnary
    :type d1: dict
    :param d2: Second dictionnary
    :type d2: dict
    :param keys_to_ignore: List of keys to ignore
    :type keys_to_ignore: list
    
    """

    if keys_to_ignore is None:
        keys_to_ignore = []

    cles_communes = set(d1.keys()) & set(d2.keys())
    cles_a_comparer = cles_communes - set(keys_to_ignore)

    for cle in cles_a_comparer:
        if d1.get(cle) != d2.get(cle):
            return False
    return True

def to_list_info(list:list):
    list_info = []
    for el in list:
        if el is None or el is np.nan or el == 'n' or el == 's':
            break
        else:
            list_info.append(el)
    return list_info