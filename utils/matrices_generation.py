from sage.all import matrix, random_matrix, random, zero_matrix

def matrix_identity(field, size:int):

    """
    Generate the identity matrix
    
    :param field: Field of the matrix
    :param size: Size of the matrix
    :type size: int
    """
    return matrix.identity(field, size)

def matrix_zero(field, size:int):
    """
    Generate the zero matrix

    :param field: Field of the matrix
    :param size: Size of the matrix
    :type size: int
    """
    return matrix.zero(field, size)

def matrix_random_invertible(field, size:int):

    """
    Generate a random invertible matrix
    
    :param field: Field of the matrix
    :param size: Size of the matrix
    :type size: int
    """
    rd_matrix = random_matrix(field, size, size)
    while not rd_matrix.is_invertible():
        rd_matrix = random_matrix(field, size, size)
    return rd_matrix

def matrix_sparse_invertible(field, size:int, p:float):
    """
    Generate a random sparse matrix 
    It is done by giving higher probability to 0 to be drawn.

    :param field: Field of the matrix
    :param size: Size of the matrix
    :type size: int
    :param p: probability to get a 0
    :type p: float
    """

    matrix_generated = zero_matrix(field, size, size)
    while not matrix_generated.is_invertible():
        matrix_list = []
        for _ in range(size):
            matrix_list.append([field.random_element() if random() < 1-p else 0 for _ in range(size)])
            ### p in probability to get a 0
        matrix_generated = matrix(field, matrix_list)
    return matrix_generated

def matrix_mds(permutation:str, field, size:int):

    """
    Define MDS matrix depending on the permutation.

    For Zerolith the matrix is a 32x32 MDS matrix given in https://eprint.iacr.org/2023/1025 

    For Anemoi the matrix is given in https://eprint.iacr.org/2024/347

    For Griffin the matrices are given in https://eprint.iacr.org/2022/403

    For Polocolo the matrices are given in https://eprint.iacr.org/2025/926

    :param permutation: Name of the permutation
    :type permutation: str

    :param field: Field of the matrix
    :param size: Size of the matrix
    :type size: int

    """

    if permutation == "zerolith":

        matrix_circ_hex = [0x536C316,0x1DD20A84,0x43E26541,0x52B22B8D,0x37DABDF0,0x540EC006,0x3015718D,0x5A99E14C,0x23637285,0x4C8A2F76,0x5DEC4E6E,0x374EE8D6,0x27EDA4D8,0x665D30D3,0x32E44597,0x43C7E2B3,0x67C4C603,0x78A8631F,0x452F77E3,0x39F03DF,0x743DBFE0,0x4DA05A48,0x5F027940,0x8293632,0x50F2C76A,0x7B773729,0x577DE8B0,0x73B1EAC6,0x58DA7D29,0x67AA4375,0xDBA9E33,0x2655E5A1]
        matrix_circulant_list = []
        for e in matrix_circ_hex:
            matrix_circulant_list.append(field(int(e)))
        matrix_MDS = matrix.circulant(matrix_circulant_list)[0:size, 0:size]

        return matrix_MDS

    elif permutation == "anemoi":

        matrix_MDS = matrix(field, [[2,1],[1,1]])

        return matrix_MDS
    
    elif permutation == "griffin":

        if size == 3:

            matrix_MDS = matrix(field, [[2,1,1], [1,2,1], [1,1,2]])

            return matrix_MDS
        
        else:

            matrix_MDS = matrix(field, [[5,7,1,3],[4,6,1,1],[1,3,5,7],[1,1,4,6]])

            return matrix_MDS
        
    elif permutation == "polocolo":

        if size == 3:

            matrix_MDS = matrix(field, [[2,1,1], [1,2,1], [1,1,2]])

            return matrix_MDS
        
        elif size == 4:

            matrix_MDS = matrix(field, [[5,7,1,3], [4,6,1,1], [1,3,5,7], [1,1,4,6]])

            return matrix_MDS

        elif size == 5:

            matrix_MDS = matrix(field, [[39, 6, 10, 28, 8], [174, 28, 32, 80, 16], [348, 58, 42, 84, 2], [39, 4, 54, 100, 44], [204, 20, 300, 560, 244]])

            return matrix_MDS
        
        elif size == 6:

            matrix_MDS = matrix(field, [[1011, 1470, 42, 140, 508, 1700], [232, 70, 48, 48, 264, 1280], [4227, 7371, 3, 490, 1420, 2900], [6744, 11760, 60, 844, 2272, 4670], [13281, 23163, 9, 1540, 4460, 9100], [48, 84, 12, 35, 40, 200]])

            return matrix_MDS
        
        elif size == 7:

            matrix_MDS = matrix(field, [[3538, 3090, 768, 480, 720, 96, 336], [470862, 470750, 1120, 16380, 94284, 136, 924], [10112885, 10113269, 24960, 352496, 2023200, 768, 18048], [3799380, 3799524, 9024, 132256, 760128, 288, 6783], [94120, 94080, 232, 3276, 18816, 5, 198], [1357780, 1357788, 3240, 47268, 271632, 101, 2454], [270260, 270260, 640, 9402, 54108, 64, 480]])

            return matrix_MDS
        
        elif size == 8:

            matrix_MDS = matrix(field, [[3840, 24, 4728, 2952, 258912, 99840, 94222, 74400], [1386, 78, 280, 1218, 32256, 13044, 8120, 6496], [6180, 743, 10416, 4428, 508032, 194858, 193984, 153056], [432, 400, 1920, 144, 73728, 27776, 30400, 23936], [10122, 1246, 5320, 8526, 346752, 136724, 108570, 86184], [950, 1052, 5424, 240, 202944, 76333, 84683, 66656], [2564, 16, 3072, 1920, 172128, 66380, 62528, 49408], [661, 35, 908, 585, 43008, 16448, 14512, 11456]])

            return matrix_MDS