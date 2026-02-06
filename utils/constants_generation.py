from sage.all import vector, zero_vector
from random import randint, shuffle, seed

def constants_zero(field, size:int):
    """
    Zero vector
    
    :param field: Field of the vector
    :param size: Size of the vector
    :type size: int
    """
    return zero_vector(field, size)

def constants_random(field, size:int):
    """
    Random vector
    
    :param field: Field of the vector
    :param size: Size of the vector
    :type size: int
    """
    return vector([field.random_element() for _ in range(size)])

def constants_random_sparsity(field, size:int, sparsity:int, seed_nb:int):
    """
    Random vector with the sparsity equals to the number of non-zero entry
    
    :param field: Field of the vector
    :param size: Size of the vector
    :type size: int
    :param sparsity: Number of non-zero entry
    :type sparsity: int
    :param seed_nb: Seed for randomness
    :type seed_nb: int
    """
    assert sparsity <= size
    seed(seed_nb)
    constants_list = [field(randint(1, field.characteristic()-1)) for _ in range(sparsity)] + [field(0)] * (size-sparsity)
    shuffle(constants_list)
    return vector(constants_list)