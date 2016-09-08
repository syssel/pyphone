from collections import defaultdict

def invertdict1(d):
	inverted = defaultdict(set)

	for k, v in d.items():
		for value in v:
			inverted[value].add(k)
	
	return inverted

def invertdict2(d):
	inverted = dict()

	for k, v in d.items():
		for value in v:
			inverted[value] = k
	
	return inverted

def get_window_indices(center, size, max_i=float("inf"), min_i=-1):
	""" Returns all possible splits of size {1, size}
		around center index"""
	
	windows = []
	
	for i in range(center - size, (center + size) +1):
		if i <= max_i and i >= min_i:
			for j in range(i, -1, -1):
				if len(list(range(i, j-1, -1))) <= (size+1) and center in range(i, j-1, -1):
					windows.append((j, i+1))
	
	return(windows)

def ambiguate_par(input_string):

	partition = []
	
	s = input_string
	i = -1

	while i < len(input_string)-1:
		i += 1
		char = input_string[i]
		s = input_string[i:]

		if char == "(":
			j = input_string.index(")", i)
			char = input_string[i:j+1]
			i = j
		
		partition.append(char)

	stack = [partition.pop(0)]
	paths = [[],]

	while stack:
		current_node = stack.pop(0)

		if partition:
			stack.append(partition.pop(0))

		if current_node.startswith("("):
			
			new_path = []
			
			for i in range(len(paths)):
				new_path.append(paths[i]+[current_node.strip("()")])

			paths = paths + new_path

		else:
			for i in range(len(paths)):
				paths[i].append(current_node)



	return paths


def dfs(points, input_string):
	""" Search paths through list of 
		 points of shape ( (start, end), ?value )
		 in a depth-first manner
		
		Returns list possible paths through points"""

	
	start_i = 0 
	end_i   = len(input_string)
	#print(points)
	# Initialize
	stack = [element for element in points if element[0][0]==start_i]
	paths = []
	path = []
	
	while stack:
		#print(stack)
		current_node = stack.pop(0)
		end_node = current_node[0][-1]
		path.append(current_node)
		
		children = [point for point in points if point[0][0] == end_node]
		if (end_node == end_i): 
			paths.append(path)
			if stack: path = [e for e in path if e[0][-1] <= stack[0][0][0]]
		elif (len(children) == 0) and stack:
			path = [e for e in path if e[0][-1] <= stack[0][0][0]]
		else:
			stack = children + stack

	return paths




