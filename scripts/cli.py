from os import chdir, killpg
from signal import SIGINT
from pathlib import Path
from subprocess import Popen
from argparse import ArgumentParser
from argcomplete import autocomplete

from sage.all import *

from utils.pickle_utils import read_and_print_pkl_file

from analysis import analysis_primitives
from analysis import compare_primitives_random

def run_benchmark(args):

    child_process = None

    try:

        """Run the benchmark script
        
        :param args: arguments from the command line
        """

        ### Start the benchmark
        child_process = Popen(["bash", "benchmark/benchmark.sh", args.permutation, args.configid, args.setid], start_new_session=True)
        child_process.wait()

    except KeyboardInterrupt as e:
        if child_process is not None:
            killpg(child_process.pid, SIGINT)

def comparison_random(args):

    child_process = None

    try:

        """Run the benchmark script
        
        :param args: arguments from the command line
        """

        ### Start the benchmark
        child_process = Popen(["bash", "comparisons_random/comparisons.sh", args.configid], start_new_session=True)
        child_process.wait()

    except KeyboardInterrupt as e:
        if child_process is not None:
            killpg(child_process.pid, SIGINT)


def generate_equations(args):
        
    """Generate a single set of equations
    
    :param args: arguments from the command line
    """

    try:

        ### Start the generation of equations using output folder name, field, monomial order, permutation name, cioc number, number of rounds, number of branches, the random seed and constant sparsities
        child_process = Popen(["python3", "generate/generate.py", args.output, str(args.field), args.monomialorder, args.permutation, str(args.cico), str(args.round), str(args.number), str(args.branch), str(args.seed), str(args.constantsparsity), str(args.timeoutgeneration)], start_new_session=True)
        child_process.wait()

    except KeyboardInterrupt as e:
        child_process.send_signal(SIGINT)

def solve_equations(args):

    """Compute the LEX Gröbner basis of system(s) of equations stored in a file
    
    :param args: arguments from the command line
    """

    try:

        child_process = Popen(["python3", "solve/algebraic_attack.py", args.output, args.input, args.algo_gb, args.options, args.algo_order_change, str(args.timeoutcomputation)], start_new_session=True)
        child_process.wait()

    except KeyboardInterrupt as e:
        child_process.send_signal(SIGINT)

def read(args):
    
    if args.mode == 'generate':

        file_to_read = f"results/generate/{args.folder}/{args.folder}.pkl"
        read_and_print_pkl_file(file_to_read)

    elif args.mode == 'solve':

        file_to_read = f"results/solve/{args.folder}/{args.folder}.pkl"
        read_and_print_pkl_file(file_to_read)

    else:
        print("Not supported mode")

def analysis_benchmark(args):

    if args.mode == 'analyse':
        analysis_primitives.compare_solving_methods(f"results/benchmark/{args.folder}", args.variable)

    elif args.mode == 'compare':
        analysis_primitives.algorithms_comparison(f"results/benchmark/{args.folder}", args.variable, args.algo)

    else:
        print("Not supported mode")


def analysis_random_comparison(args):

    if args.mode == 'analyse':
        compare_primitives_random.compare_solving_methods(f"results/benchmark/{args.folder}", f"results/comparisons/random_compare_{args.folder}", args.variable)

    elif args.mode == 'compare':
        compare_primitives_random.algorithms_comparison(f"results/benchmark/{args.folder}", f"results/comparisons/random_compare_{args.folder}", args.variable, args.algo)

    else:
        print("Not supported mode")


"""

    Main function to deal with the command pesscy

"""

def main():

    # Ensure working directory is the script's directory
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    chdir(PROJECT_ROOT)

    parser = ArgumentParser(description="PESSCY CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Benchmark mode ---
    parser_benchmark = subparsers.add_parser("benchmark", help="Run a full set of experiments")
    parser_benchmark.add_argument("-p", "--permutation", help="Permutation/Modelling", required=True)
    parser_benchmark.add_argument("-c", "--configid", help="Configuration ID", required=True)
    parser_benchmark.add_argument("-s", "--setid", help="Set ID", required=True)
    parser_benchmark.set_defaults(func=run_benchmark)

    # --- Comparison random mode ---
    parser_random = subparsers.add_parser("random_comparison", help="Run comparisons with random ideals of the same shape")
    parser_random.add_argument("-c", "--configid", help="Configuration ID", required=True)
    parser_random.set_defaults(func=comparison_random)

    # --- Equation generation mode ---
    parser_gen = subparsers.add_parser("generate", help="Generate a system of equations")
    parser_gen.add_argument("-p", "--permutation", type=str, help="Permutation/Modelling", required=True)
    parser_gen.add_argument("-b", "--branch", type=int, help="Number of branches", required=True)
    parser_gen.add_argument("-r", "--round", type=int, help="Number of rounds", required=True)
    parser_gen.add_argument("-f", "--field", type=int, help="Field size", required=True)
    parser_gen.add_argument("-c", "--cico", type=int, help="CICO Number", required=True)
    parser_gen.add_argument("-m", "--monomialorder", type=str, default="degrevlex",help="Monomial order of the ring")
    parser_gen.add_argument("-n", "--number", type=int, default=1, help="Number of systems to generate")
    parser_gen.add_argument("-s", "--seed", type=int, default=11, help="Randomness seed")
    parser_gen.add_argument("-cs", "--constantsparsity", type=int, default=0, help="Constant sparsity")

    parser_gen.add_argument("-tg", "--timeoutgeneration", type=int, default=10, help="Timeout generation of equation")

    parser_gen.add_argument("-o", "--output", default="generate", help="Output folder name")
    parser_gen.set_defaults(func=generate_equations)

    # --- Equation solve mode ---
    parser_solve = subparsers.add_parser("solve", help="Execute the algebraic attack on the system")

    parser_solve.add_argument("-g", "--algo_gb", default="singular:groebner", type=str, help="Gröbner basis algorithm")
    parser_solve.add_argument("-op", "--options", default="None", type=str, help="Options of the Gröbner basis algorithm")
    parser_solve.add_argument("-oc", "--algo_order_change", default="gwalk", type=str, help="Term order change algorithm")
    parser_solve.add_argument("-tc", "--timeoutcomputation", type=int, default=10, help="Timeout algebraic attack")

    parser_solve.add_argument("-i", "--input", type=str, help="Input file with system(s) of equations to solve")
    parser_solve.add_argument("-o", "--output", default="solve", help="Output folder name")
    parser_solve.set_defaults(func=solve_equations)

    # --- Read mode ---

    parser_read = subparsers.add_parser("read", help="Read a system of equations or results of algebraic attacks")
    parser_read.add_argument("-m", "--mode", type=str, help="'generate' or 'solve'", required=True)
    parser_read.add_argument("-f", "--folder", type=str, help="Folder with file to read", required=True)
    parser_read.set_defaults(func=read)

    # --- Analyse benchmark results mode ---

    parser_analysis_benchmark = subparsers.add_parser("analysis_benchmark", help="Analysis of a benchmark")
    parser_analysis_benchmark.add_argument("-m", "--mode", type=str, help="'compare' or 'analyse'")
    parser_analysis_benchmark.add_argument("-f", "--folder", type=str, help="Folder with benchmark results")
    parser_analysis_benchmark.add_argument("-v", "--variable", type=str, default="round", help="Variable for x-axis")
    parser_analysis_benchmark.add_argument("-a", "--algo", type=str, default="groebner_time", help="Timing to analyse: Gröbner basis computation or Term order change")
    
    parser_analysis_benchmark.set_defaults(func=analysis_benchmark)

    # --- Analyse random comparison mode ---

    parser_analysis_random_comparison = subparsers.add_parser("analysis_random", help="Analysis of a comparison to random ideals")
    parser_analysis_random_comparison.add_argument("-m", "--mode", type=str, help="'compare' or 'analyse'")
    parser_analysis_random_comparison.add_argument("-f", "--folder", type=str, help="Folder with benchmark results")
    parser_analysis_random_comparison.add_argument("-v", "--variable", type=str, help="Variable for x-axis")
    parser_analysis_random_comparison.add_argument("-a", "--algo", type=str, default="groebner_time", help="Timing to analyse: Gröbner basis computation or Term order change")
    
    parser_analysis_random_comparison.set_defaults(func=analysis_random_comparison)
    autocomplete(parser)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()