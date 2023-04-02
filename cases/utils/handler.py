from typing          import Callable
from multiprocessing import Process


def init_proc(_func : Callable, _args) -> Process:
    return Process(target=_func, args=_args)

def start_proc(proc : Process) -> Process:
    proc.start()
    return proc

def kill_proc(proc : Process) -> Process:
    proc.kill()
    return 

