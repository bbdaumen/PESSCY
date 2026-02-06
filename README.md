# Polynomial Equations Solving for Symmetric Cryptography (PESSCY)

PESSCY is a tool developed to allow practical analysis of algebraic attacks using the Gröbner basis theory over Oriented-Arithmetisation Primitives.

## Installation of the tool

**This tool must be used and installed in an environment containing SageMath.**

To install it, run in the folder where you clone this repository:

```sh
pip install -e .
```

Then, you will be able to use the tool with the command line `pesscy`.

Some tests are provided in the `tests` folder. If you want to try your installation, simply run:

```sh
bash tests/test.sh
```

## Modes of the tool

This tool may be used in different modes:

### 1. Generate

Generate system(s) of equations corresponding to the modelling of a problem on a primitive. Give as inputs:

- the permutation name (corresponds to the folder name in `permutations`)
- the number of branches
- the number of rounds
- the field characteristic
- the cico number
- the monomial ordering of the ring
- the number of times we generate the system
- the seed of randomness
- the sparsity of the constant vectors
- the timeout for the generation of the systems
- the name of the output folder (output_folder)

The results of the generation are stored in `results/generate/output_folder`. There are two files, the log one with some informations about the generation and a pickle one with the actual system(s) generated. See [Generation file](#generation-file) for more informations.

For more informations about the command line

```sh
pesscy generate -h
```

### 2. Solve

Solve the previous system(s) using algorithms to compute Gröbner basis or term order change algorithms proposed in SageMath using different libraries (Singular, Macaulay2, Giac, msolve and Magma).

Give as inputs:
- the algorithm to compute the Gröbner basis
- its options
- the algorithm to change the term order
- the timeout for the computation of the elimination basis
- the input folder name where to find the equations (must be in `results/generate/`)
- the output folder name (that will be stored in `results/solve/`)

There are two files in the output folder, one for the log of the resolution of the systems of equations and another one for the results of the computation. See [Solve file](#solve-file) for more informations.

For more informations about the command line

```sh
pesscy solve -h
```

### 3. Read 

Functions to easily read the previous results.

This command has two modes: `'generate'` or `'solve'` depending on whether we want to read results of the `generate` command or `solve` one. 
The second argument is the folder's name containing the files with the results.

For more informations about the command line

```sh
pesscy read -h
```

### 4. Benchmark

Perform a full benchmark of algebraic attacks over a permutation, on a range of parameters to freely choose.

The command line asks three compulsory options:

1. The name of the permutation or modeling approach (permutation)
2. The config ID, the configuration identifier corresponding to a given benchmark setup (configid)
3. The set ID, the identifier of the experiment set executed with that configuration (setid)

The input file containing the benchmark setup has to be stored in `experimentalSetup/permutation/permutation_set_configid.json`. The description of the input file is made in `public_doc/benchmark_input.txt`.

The generation of the parameter is such that all the combinations possible are made and every set of parameters is solved. The full list of set of parameters is in stored in the `parameters.pkl` file.

The folder containing the results and logs is stored in `results/benchmark/permutation_set_configid_setid`.

The benchmark mode takes advantage of the multithreading. Each sub-list of experiments is executed on a particular core. It has been observed that some may use more than one core. To optimise the full computation, it is advised to leave some cores of the processor free in order to be used for differents processes.

For more informations about the command line

```sh
pesscy benchmark -h
```

### 5. Random ideals comparisons

Generate random ideals from systems of equations sharing the same shape than the ones from benchmark.

This mode requires an input JSON file that must be stored in `experimentalSetup/random/`.

Documentation of the entries are given in `public_doc/comparisons.txt`.

The file name must be `random_set_i.json` with `i` the configuration number.

The folder input used for the comparison is in `results/benchmark`. 

The results of the comparisons are in `results/comparisons/` under the name `random_compare_permutation_configid_setid`.

IDs identify the two experiments compared between `results/benchmark/permutation_configid_setid/res/id.pkl` and `results/comparisons/random_compare_permutation_configid_setid/res/id.pkl`

The random ideal comparison mode takes advantage of the multithreading. Each sub-list of experiments is executed on a particular core. It has been observed that some may use more than one core. To optimise the full computation, it is advised to leave some cores of the processor free in order to be used for differents processes.

For more informations about the command line

```sh
pesscy random_comparison -h
```

### 6. Benchmark analysis

This functionnality aims to allow easy analysis of the benchmark results. Two modes are proposed:

1. analyse: compare the different ways of solving: directly elimination order or use terme order change algorithm. Solving degree, Macaulay bound, ideal degree and ideal degree upper bound are given when possible.
2. compare: compare the different time of computation taken by algorithms to compute the Gröbner basis or to change the term order.

For more informations about the command line

```sh
pesscy analysis_benchmark -h
```

### 7. Random comparisons analysis

This functionnality aims to allow easy analysis of the comparison results. Two modes are proposed:

1. analyse: compare the different ways of solving: directly elimination order or use terme order change algorithm for the primitives equationsand random ones. Solving degree, Macaulay bound, ideal degree and ideal degree upper bound are given when possible.
2. compare: compare the different time of computation taken by algorithms to compute the Gröbner basis or to change the term order for the primitive and the random ideals.

```sh
pesscy analysis_random -h
```

## Algorithms for Gröbner basis

All libraries and algorithms supported by SageMath to compute Gröbner basis are described in the [documentation](https://example.com).

There are all supported with their options (if the library is installed) except 'ginv'.

Singular and Magma gives access to detailed logs on the computation of the Gröbner basis. If the `prot` option is `true`, the logs are printed and if it is `'sage'`, they are nicely printed. This option can't be used yet. Some modifications in SageMath have been made and must be pulled.

Every algorithm may be called with some options. See the `public_doc/benchmark_input.txt` file for a description on how to call deactivate/activate them.

Documentation about the algorithms and options is available at `public_doc/groebner_basis_doc.py`

## Results and logs file

### Generation file

The result of generation of systems of equations are stored in a pickle file. They contain list of systems of equations with the time taken to generate them.

### Solve file

The result of a resolution of a system of equations is also stored in a pickle file. It contains many dictionnaries of 9 entries.

- 'system_of_equation_shape': the shape of the system of equations
- 'generation_time': the time to generate the system
- 'groebner_time': the time to compute the Gröbner basis
- 'solving_degree': the solving degree, the maximal degree reached during the computation of the Gröbner basis
- 'ideal_dimension': the dimension of the ideal
- 'transformation_basis_time': the time to transform the Gröbner basis to the lexicographic one
- 'radical_ideal': if the ideal is in shape position it returns whether it is radical or not
- 'shape_position': whether or not the ideal is in shape position
- 'ideal_degree': the ideal degree if the ideal has dimension 0

## Add a Permutation/Modelling

You may add easily a permutation in the `permutations` folder. You create a new python file. Give a name corresponding to the permutation/modelling. 

Then you follow the same structure than the one given in `permutations/template.py`.

## Solving the system of equations

The file managing the solving of the systems of equations is `utils/systems_solver.py`. It is seperated in two parts: the computation of the Gröbner basis and the execution of the term order change algorithm. This two step takes the largest time of the computation.

Moreover, we compute the dimension of the ideal, and for 0-dimensionnal ideal, the ideal degree. To do so, we use functions proposed by SageMath. In some cases, it appears that the computation is unexpectly long although a Gröbner has already been computed. 

If the dimension of the ideal is already known, it is advised to change it directly in the `systems_solver` file. For the ideal degree, we give another function to compute it in the case the ideal is in shape position. Otherwise, Singular is used.

## Documentation of the functions

Documentations generated by Sphinx is available for the functions of the tool.

## Contact

Any problem reports, help, and contributions are welcome!

If you have any questions, please feel free to contact me at `baptiste.daumen@inria.fr`.

## BibTex entry

```bibtex
@misc{PESSCY2K26,
title = {Polynomial Equations Solving for Symmetric Cryptography (PESSCY)},
year = {2026},
author = {Baptiste Daumen},
howpublished = {Available at \url{https://github.com/bbdaumen/PESSCY}}
}
``` 
