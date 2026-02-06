import sys
from importlib import import_module
from os import dup2
from psutil import Process, wait_procs, NoSuchProcess

def redirect_all_output(log_file_path:str):

    """
    Redirect all the outputs to a file
    
    :param log_file_path: Path to the file
    :type log_file_path: str
    """
    log_file = open(log_file_path, 'w')

    sys.stdout = log_file
    sys.stderr = log_file

    dup2(log_file.fileno(), 1)
    dup2(log_file.fileno(), 2)

def import_perm(permutation:str):

    """
    Import the generation function of systems of the permutation
    
    :param permutation: The name of the permutation that is the same than the file in the permutations folder.
    :type permutation: str
    """

    module_name = f"permutations.{permutation}"
    module = import_module(module_name)

    try:
        return module.generate_system_of_equations
    except AttributeError:
        raise ImportError(
            f"{module_name} must define generate_system_of_equations()"
        )
    
def kill_process_tree(proc):
    """
    DKill the process and all its children
    
    :param proc: Process to kill, coming from the Process class in Python
    """
    try:
        parent = Process(proc.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        _, still_alive = wait_procs(children, timeout=3)
        for child in still_alive:
            child.kill()
        parent.terminate()
        parent.wait(1)
    except NoSuchProcess:
        pass
