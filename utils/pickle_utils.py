from pickle import load, dump, UnpicklingError

def change_dict_pkl(filename:str, i:int, n:int, key, new_value):

    """
    Change values in the dictionnaries in the result pickle file
    
    :param filename: Name of the file
    :type filename: str
    :param i: Number of the experiment in the pickle file
    :type i: int
    :param n: Total number of experiment
    :type n: int
    :param key: Key of the dictionnary to change
    :param new_value: New value of the key
    """

    dict_list = []

    with open(filename, 'rb') as f_pkl:
        j = 0
        while j < n:
            res_dict = load(f_pkl)
            if j==i:
                res_dict[key] = new_value
            dict_list.append(res_dict)
            j+=1
    f_pkl.close()

    with open(filename, 'wb') as f_pkl:
        for res_dict in dict_list:
            dump(res_dict, f_pkl)
            f_pkl.flush()
    f_pkl.close()


def change_dict_failed_to_timeout(filename:str, i:int, n:int):

    """
    Change all the "failed" value to "timeout" in the dictionnaries result
    
    :param filename: Name of the file
    :type filename: str
    :param i: Number of the experiment in the pickle file
    :type i: int
    :param n: Total number of experiment
    :type n: int
    """

    timeout_algo = 6

    dict_list = []
    with open(filename, 'rb') as f_pkl:
        j = 0
        while j < n:
            res_dict = load(f_pkl)
            changed = False
            if j==i:
                if res_dict["groebner_time"] == "failed":
                    res_dict["groebner_time"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 0

                if res_dict["solving_degree"] == "failed":
                    res_dict["solving_degree"] = "timeout"

                if res_dict["ideal_dimension"] == "failed":
                    res_dict["ideal_dimension"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 1

                if res_dict["transformation_basis_time"] == "failed":
                    res_dict["transformation_basis_time"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 2

                if res_dict["radical_ideal"] == "failed":
                    res_dict["radical_ideal"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 3

                if res_dict["shape_position"] == "failed":
                    res_dict["shape_position"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 4

                if res_dict["ideal_degree"] == "failed":
                    res_dict["ideal_degree"] = "timeout"
                    if not changed:
                        changed = True
                        timeout_algo = 5

            dict_list.append(res_dict)
            j+=1
    f_pkl.close()
    
    with open(filename, 'wb') as f_pkl:
        for res_dict in dict_list:
            dump(res_dict, f_pkl)
            f_pkl.flush()
    f_pkl.close()

    return timeout_algo


def change_dict_failed_to_skipped(filename:str, i:int, n:int):

    """
    Change all the "failed" value to "skipped" in the dictionnaries result
    
    :param filename: Name of the file
    :type filename: str
    :param i: Number of the experiment in the pickle file
    :type i: int
    :param n: Total number of experiment
    :type n: int
    """


    dict_list = []
    with open(filename, 'rb') as f_pkl:
        j = 0
        while j < n:
            res_dict = load(f_pkl)
            if j==i:
                if res_dict["groebner_time"] == "failed":
                    res_dict["groebner_time"] = "skipped"

                if res_dict["solving_degree"] == "failed":
                    res_dict["solving_degree"] = "skipped"

                if res_dict["ideal_dimension"] == "failed":
                    res_dict["ideal_dimension"] = "skipped"

                if res_dict["transformation_basis_time"] == "failed":
                    res_dict["transformation_basis_time"] = "skipped"

                if res_dict["radical_ideal"] == "failed":
                    res_dict["radical_ideal"] = "skipped"

                if res_dict["shape_position"] == "failed":
                    res_dict["shape_position"] = "skipped"

                if res_dict["ideal_degree"] == "failed":
                    res_dict["ideal_degree"] = "skipped"
                    
            dict_list.append(res_dict)
            j+=1
    f_pkl.close()
    
    with open(filename, 'wb') as f_pkl:
        for res_dict in dict_list:
            dump(res_dict, f_pkl)
            f_pkl.flush()
    f_pkl.close()


def read_pkl_file(filepath:str):

    """
    Read pickle file
    
    :param filepath: Path to the file
    :type filepath: str
    """
    
    try:
        with open(filepath, 'rb') as file:
            try:
                data = load(file)
            except EOFError:
                print("Can't read data")
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except UnpicklingError:
        print("Error: File could not be unpickled.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return data

def read_and_print_pkl_file(filepath:str):

    """
    Read and print pickle file
    
    :param filepath: Path to the file
    :type filepath: str
    """
    
    try:
        with open(filepath, 'rb') as file:
            while True:
                try:
                    data = load(file)
                    print(data)
                except EOFError:
                    break
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except UnpicklingError:
        print("Error: File could not be unpickled.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return data