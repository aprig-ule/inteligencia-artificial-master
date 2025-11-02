import sys
sys.path.append("./aima-python")
from games4e import Game, alpha_beta_cutoff_search as alphabeta_search
import time
import csv
import os
import sys

class CrossingGame(Game):
    """Game implementation for the described n x n board.

    Players: 'P1' (left->right) and 'P2' (top->down).
    State: (p1_pos, p2_pos, to_move) where p1_pos/p2_pos are tuples of (r,c).
    """

    def __init__(self, n):
        self.n = n
        self.rows = n + 2
        self.cols = n + 2
        self.players = ('P1', 'P2')

    def initial_state(self):
        """Return the initial game state."""
        p1 = tuple((r, 0) for r in range(1, self.n + 1))
        p2 = tuple((0, c) for c in range(1, self.n + 1))
        return (p1, p2, 'P1')

    #  Game moves
    def to_move(self, state):
        return state[2]

    def opponent(self, player):
        return 'P2' if player == 'P1' else 'P1'

    def actions(self, state):
        """Return list of legal actions for player to move.

        Action format: ((r_from,c_from),(r_to,c_to)).
        """
        p1_pos, p2_pos, to_move = state
        occupied = set(p1_pos) | set(p2_pos)
        actions = []

        if to_move == 'P1':
            for (r, c) in p1_pos:
                # forward one to the right
                f = (r, c + 1)
                if self._on_board(f) and f not in occupied:
                    actions.append(((r, c), f))
                # jump over opponent
                over = (r, c + 1)
                land = (r, c + 2)
                if (self._on_board(over) and self._on_board(land)
                        and over in p2_pos and land not in occupied):
                    actions.append(((r, c), land))
        else:  # P2
            for (r, c) in p2_pos:
                f = (r + 1, c)
                if self._on_board(f) and f not in occupied:
                    actions.append(((r, c), f))
                # jump over opponent
                over = (r + 1, c)
                land = (r + 2, c)
                if (self._on_board(over) and self._on_board(land)
                        and over in p1_pos and land not in occupied):
                    actions.append(((r, c), land))

        # If no moves, the player must pass; we represent pass as None
        if not actions:
            return [None]
        return actions

    def result(self, state, action):
        """Return the new state after applying action. If action is None -> pass."""
        p1_pos, p2_pos, to_move = state
        if action is None:
            return (p1_pos, p2_pos, self.opponent(to_move))

        (r0, c0), (r1, c1) = action
        if to_move == 'P1':
            p1 = list(p1_pos)
            # find the piece
            idx = p1.index((r0, c0))
            p1[idx] = (r1, c1)
            new_p1 = tuple(sorted(p1))
            new_p2 = p2_pos
        else:
            p2 = list(p2_pos)
            idx = p2.index((r0, c0))
            p2[idx] = (r1, c1)
            new_p2 = tuple(sorted(p2))
            new_p1 = p1_pos
        return (new_p1, new_p2, self.opponent(to_move))

    def is_goal(self, state):
        """Terminal when either player has all pieces in their goal border."""
        p1_pos, p2_pos, _ = state
        if all(c == self.cols - 1 for (_r, c) in p1_pos):
            return True
        if all(r == self.rows - 1 for (r, _c) in p2_pos):
            return True
        return False

    def utility(self, state, player):
        """Utility from the viewpoint of player (1 for win, -1 for loss, 0 otherwise).

        The utility is +inf/-inf for terminal wins/losses to avoid ties from heuristics.
        games4e's alphabeta uses utility(state, root_player) typically; keep symmetric.
        """
        p1_pos, p2_pos, _ = state
        if all(c == self.cols - 1 for (_r, c) in p1_pos):
            return float('inf') if player == 'P1' else float('-inf')
        if all(r == self.rows - 1 for (r, _c) in p2_pos):
            return float('inf') if player == 'P2' else float('-inf')
        return 0

    def display(self, state):
        p1_pos, p2_pos, to_move = state
        board = [['.' for _ in range(self.cols)] for __ in range(self.rows)]
        # Player pieces
        for (r, c) in p1_pos:
            board[r][c] = 'X'
        for (r, c) in p2_pos:
            board[r][c] = 'O'
            
        print('To move:', to_move)
        for r in range(self.rows):
            print(''.join(board[r]))

    def _on_board(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols


# Heuristic for cutoff search 

def simple_heuristic(state, player, game: CrossingGame):
    """A simple evaluation: sum of distances to goal (the smaller the better).

    We compute material + progress: for P1 we want columns as large as possible;
    for P2 we want rows as large as possible. Heuristic returns a number where
    higher is better for the player parameter.
    """
    p1_pos, p2_pos, _ = state
    # Distance to goal for player (lower -> better)
    p1_dist = sum((game.cols - 1 - c) for (_r, c) in p1_pos)
    p2_dist = sum((game.rows - 1 - r) for (r, _c) in p2_pos)

    # We combine as opponent distance minus own distance so bigger -> better
    if player == 'P1':
        return float(p2_dist - p1_dist)
    else:
        return float(p1_dist - p2_dist)

if __name__ == '__main__':
  
    try:
        n = input('Introduce el tamaño del tablero (n, por defecto 3): ').strip()
        n = int(n) if n else 3
    except Exception:
        n = 3
        print('El tamaño del tablero no es válido.')
        sys.exit(1)
        
    g = CrossingGame(n)
    state = g.initial_state()

    print('Initial state:')
    g.display(state)

    root_player = g.to_move(state)
    def eval_fn(s):
        return simple_heuristic(s, root_player, g)

    # Depth per player (can be tuned); store to report later
    d_p1 = 4
    d_p2 = 6

    # Timing records: lists of durations (seconds) per player
    times = {'P1': [], 'P2': []}

    # Player 1 and Player 2 play automatically using alpha-beta search
    current_state = state
    move_num = 1
    # Start total game timer
    game_start = time.time()
    while not g.is_goal(current_state):
        player = g.to_move(current_state)
        print(f"\nTurno {move_num}: {player}")
        try:
            root_player = player
            def eval_fn(s):
                return simple_heuristic(s, root_player, g)
            # Select depth based on player
            d = d_p1 if player == 'P1' else d_p2
            start = time.time()
            move = alphabeta_search(current_state, g, d=d, cutoff_test=None, eval_fn=eval_fn)
            duration = time.time() - start
            # record duration for this player
            times[player].append(duration)
            print('Movimiento seleccionado:', move)
            current_state = g.result(current_state, move)
            g.display(current_state)
        except Exception as e:
            print('Error ejecutando el algoritmo de búsqueda:', e)
            break
        move_num += 1
        
    # Display final results
    print("\nJuego terminado.")
    winner = None
    if all(c == g.cols - 1 for (_r, c) in current_state[0]):
        winner = 'P1'
    elif all(r == g.rows - 1 for (r, _c) in current_state[1]):
        winner = 'P2'
    if winner:
        print(f"Ganador: {winner}")
    else:
        print("Empate o sin ganador claro.")

    # Total game time
    total_time = time.time() - game_start
    print(f"Tiempo total de la partida: {total_time:.4f} s")

    # Compute average times per player
    results = {}
    for p, d in (('P1', d_p1), ('P2', d_p2)):
        lst = times.get(p, [])
        avg = sum(lst) / len(lst) if lst else 0.0
        results[p] = (n, d, avg)

    print('\nTiempos medios por jugador (n, d, avg_seconds):')
    for p in ('P1', 'P2'):
        n_val, d_val, avg_val = results[p]
        print(f"{p}: n={n_val}, d={d_val}, avg_time={avg_val:.4f} s over {len(times[p])} moves")

    # Store in csv
    csv_path = os.path.join(os.path.dirname(__file__), 'results.csv')
    write_header = not os.path.exists(csv_path)
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(['n', 'd', 'tiempo_promedio', 'tiempo_partida'])
            for p in ('P1', 'P2'):
                n_val, d_val, avg_val = results[p]
                writer.writerow([n_val, d_val, f"{avg_val:.6f}", f"{total_time:.6f}"])
        print(f"Resultados añadidos a {csv_path}")
    except Exception as e:
        print('No se pudo escribir el archivo CSV:', e)
