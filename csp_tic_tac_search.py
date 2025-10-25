
import sys
sys.path.append("./aima-python")
from csp import NaryCSP, Constraint, ac_solver

def read_board():
	"""Reads the board from line by line input until EOF or empty line."""
	board = []
	try:
		while True:
			line = input()
			if line.strip() == '':
				break
			board.append(list(line.strip()))
	except EOFError:
		pass
	if(is_initially_valid_board(board)):
		return board
	else:
		sys.exit(1)

def is_initially_valid_board(board):
	"""Checks if board is valid."""
	n = len(board)
 
	#Check if board is square
	for row in board:
		if len(row) != n:
			print("Error: El tablero debe tener el mismo número de filas y de columnas.", file=sys.stderr)
			return False
 
	#Check if board contains only valid characters
	valid_chars = {'x', 'o', '_'}
	for row in board:
		for cell in row:
			if cell not in valid_chars:
				print(f"Error: Caracter inválido '{cell}'. Solo se permite usar 'x', 'o' ó '_'.", file=sys.stderr)
				return False
  
	#Check if board is already solved
	if is_complete(board) and is_goal(board):
		print("El tablero ya está resuelto.", file=sys.stderr)
		return False
  
  #Check if board initially valid (no three consecutive symbols)
	return valid_board(board)

def count_in_row(row, symbol):
	"""Counts the number of occurrences of 'symbol' in the given row."""
	return row.count(symbol)

def count_in_col(board, col, symbol):
	"""Counts the number of occurrences of 'symbol' in the given col."""
	return sum(1 for row in board if row[col] == symbol)


def has_three_consecutive_symbol(line, symbol):
	"""Checks if there are three consecutive 'symbol'"""
	return symbol*3 in ''.join(line)

def valid_board(board):
	"""Checks if the board is valid"""
	n = len(board)
	for i in range(n):
		row = board[i]
		if has_three_consecutive_symbol(row, 'x') or has_three_consecutive_symbol(row, 'o'):
			return False
		col = [board[j][i] for j in range(n)]
		if has_three_consecutive_symbol(col, 'x') or has_three_consecutive_symbol(col, 'o'):
			return False
	return True

def is_complete(board):
	"""Checks if the board is completely filled (no '_' cells remain)."""
	return all(cell != '_' for row in board for cell in row)

def print_board(board):
	"""Prints the board."""
	if isinstance(board, dict):
		n = int(len(board) ** 0.5)
		# Try to infer n from keys
		n = max(i for (i, j) in board.keys()) + 1
		for i in range(n):
			print(''.join(board[(i, j)] for j in range(n)))
	else:
		for row in board:
			print(''.join(row))

def is_goal(board):
	"""Checks if the board is a goal state: valid, balanced, and each row/column has the 
 	correct number of 'x' and 'o'."""
	n = len(board)
	target = count_in_row(board[0], 'o')
	for i in range(n):
		row = board[i]
		if has_three_consecutive_symbol(row, 'x') or has_three_consecutive_symbol(row, 'o'):
			return False
		if count_in_row(row, 'o') != target:
			return False
 
	for j in range(n):
		col = [board[i][j] for i in range(n)]
		if has_three_consecutive_symbol(col, 'x') or has_three_consecutive_symbol(col, 'o'):
			return False
		if count_in_col(board, j, 'o') != target:
			return False
	
	return True

def make_row_eq(n):
  return lambda *vals: sum(1 for v in vals[:n] if v == 'o') == sum(1 for v in vals[n:] if v == 'o')
def make_col_eq(n):
  return lambda *vals: sum(1 for v in vals[:n] if v == 'o') == sum(1 for v in vals[n:] if v == 'o')

def build_csp(board):
	n = len(board)
	domains = {}
	for i in range(n):
		for j in range(n):
			if board[i][j] == '_':
				domains[(i, j)] = {'x', 'o'}
			else:
				domains[(i, j)] = {board[i][j]}

	constraints = []
	# No three consecutive in rows
	def not_three(a, b, c):
		return not (a == b == c)
	for i in range(n):
		for j in range(n - 2):
			scope = ((i, j), (i, j+1), (i, j+2))
			constraints.append(Constraint(scope, lambda a, b, c, f=not_three: f(a, b, c)))
	# No three consecutive in columns
	for j in range(n):
		for i in range(n - 2):
			scope = ((i, j), (i+1, j), (i+2, j))
			constraints.append(Constraint(scope, lambda a, b, c, f=not_three: f(a, b, c)))
	# Global constraint: all rows and all columns must have the same number of 'o' when fully assigned
	def all_rows_cols_equal_o(*vals):
		# vals: all board values row-wise
		board_vals = [list(vals[i*n:(i+1)*n]) for i in range(n)]
		# Check if any '_' remains
		if any('_' in row for row in board_vals):
			return True
		row_counts = [row.count('o') for row in board_vals]
		col_counts = [sum(1 for i in range(n) if board_vals[i][j] == 'o') for j in range(n)]
		all_counts = row_counts + col_counts
		return all(c == all_counts[0] for c in all_counts)
	# Add a single global constraint over all variables
	constraints.append(Constraint(tuple((i, j) for i in range(n) for j in range(n)), all_rows_cols_equal_o))
	return NaryCSP(domains, constraints)

def main():
	board = read_board()
	csp = build_csp(board)
	solution = ac_solver(csp)
	if solution:
		print_board(solution)
	else:
		print("No hay solución.")

if __name__ == "__main__":
	main()
 

