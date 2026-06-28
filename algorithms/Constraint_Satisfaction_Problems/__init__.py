from .Backtracking_Search import solve_backtracking
from .Forward_Checking import solve_forward_checking
#from .Min_Conflicts import solve_min_conflicts
from .Bomb_Solver       import (solve_bomb_backtracking,
<<<<<<< HEAD
                                solve_bomb_forward_checking)
                               #, solve_bomb_min_conflicts)
=======
                                solve_bomb_forward_checking,
                                solve_bomb_min_conflicts)
>>>>>>> 5b2449288be8d57fa581c5eacb5622cd6c6732bb

__all__ = [
    "solve_backtracking", "solve_forward_checking", "solve_min_conflicts",
    "solve_bomb_backtracking", "solve_bomb_forward_checking", "solve_bomb_min_conflicts",
]