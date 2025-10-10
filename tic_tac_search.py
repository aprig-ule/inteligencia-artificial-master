import sys
sys.path.append("./aima-python")
from search import Problem
import copy

def read_board():
	board = []
	try:
		while True:
			line = input()
			if line.strip() == '':
				break
			board.append(list(line.strip()))
	except EOFError:
		pass
	return board

def count_in_row(row, symbol):
	return row.count(symbol)

def count_in_col(board, col, symbol):
	return sum(1 for row in board if row[col] == symbol)

def has_three_consecutive(line, symbol):
	return symbol*3 in ''.join(line)

def valid_board(board):
	n = len(board)
	for i in range(n):
		row = board[i]
		if has_three_consecutive(row, 'x') or has_three_consecutive(row, 'o'):
			return False
		col = [board[j][i] for j in range(n)]
		if has_three_consecutive(col, 'x') or has_three_consecutive(col, 'o'):
			return False
	return True

def balanced(board):
	n = len(board)
	for i in range(n):
		row = board[i]
		if abs(count_in_row(row, 'x') - count_in_row(row, 'o')) > n % 2:
			return False
		col = [board[j][i] for j in range(n)]
		if abs(count_in_row(col, 'x') - count_in_row(col, 'o')) > n % 2:
			return False
	return True

def is_complete(board):
	return all(cell != '_' for row in board for cell in row)

def is_goal(board):
	n = len(board)
	for i in range(n):
		row = board[i]
		if has_three_consecutive(row, 'x') or has_three_consecutive(row, 'o'):
			return False
		if count_in_row(row, 'x') != n // 2 or count_in_row(row, 'o') != n // 2:
			return False
		col = [board[j][i] for j in range(n)]
		if has_three_consecutive(col, 'x') or has_three_consecutive(col, 'o'):
			return False
		if count_in_row(col, 'x') != n // 2 or count_in_row(col, 'o') != n // 2:
			return False
	return True

class TicTacProblem(Problem):
	def __init__(self, initial):
		super().__init__(initial)
		self.n = len(initial)

	def actions(self, state):
		actions = []
		for i in range(self.n):
			for j in range(self.n):
				if state[i][j] == '_':
					actions.append((i, j, 'x'))
					actions.append((i, j, 'o'))
		return actions

	def result(self, state, action):
		i, j, symbol = action
		new_state = copy.deepcopy(state)
		new_state[i][j] = symbol
		return new_state

	def goal_test(self, state):
		return is_complete(state) and is_goal(state)

	def value(self, state):
		return 0

	def constraints(self, state):
		return valid_board(state) and balanced(state)

def backtrack(problem):
	def recursive(state):
		if problem.goal_test(state):
			return state
		for action in problem.actions(state):
			new_state = problem.result(state, action)
			if problem.constraints(new_state):
				result = recursive(new_state)
				if result:
					return result
		return None
	return recursive(problem.initial)

def main():
	board = read_board()
	problem = TicTacProblem(board)
	solution = backtrack(problem)
	if solution:
		for row in solution:
			print(''.join(row))
	else:
		print("No hay solución.")

if __name__ == "__main__":
	main()
