from pyphone_utils import get_window_indices, dfs, invertdict1, invertdict2, ambiguate_par
from collections import defaultdict
import re
import xlrd

class Corpus(object):

	def __init__(self, phonbook, regbook):
		self._phonbook = phonbook
		self._regbook = regbook		
		self._roots = []
		self._attributes = dict()


	def load_corpus(self, fpath, regex="\*(.*?)\-"):
		workbook = xlrd.open_workbook(fpath)
		dsheet = workbook.sheet_by_index(0)
		roots = dsheet.col_values(0, 1)
		attributes = dsheet.row_values(0, 1)
		
		self._attributes = {attr: None for attr in attributes}

		for i, root in enumerate(roots):
			root_attr = self._attributes.copy()

			if regex:
				try:
					m = re.search(regex, root)
					span = m.span()

					edit = root[span[0]+1: span[1]-1]
					prefix = root[:span[0]+1]
					suffix = root[span[1]-1:].strip("{1}")

				except AttributeError:
					edit = root[:]


			for j, attr in zip(range(1, len(attributes)+1), attributes):
				root_attr[attr] = dsheet.cell_value(i+1, j)



			self.add_root(edit, i+2, prefix, suffix, root_attr)


	def add_root(self, orth, index, prefix, suffix, attr):
		root = Root(self._phonbook)

		root.update(orth, index, prefix, suffix, attr)

		self._roots.append(root)
		#print(root.orthform)
		#print(root.formatted)
		#print(root.error)
		#print()

	def search(self, regpattern):
		matches = []
		for root in self._roots:
			match = False
			for form in root.phonedit:
				if re.match(regpattern, form):
					match = True
				
			if match: matches.append(root)

		return matches




class SearchString(object):

	def __init__(self, phonbook, regbook):
		self.phonbook = phonbook
		self.invertbook = invertdict1(phonbook.phondesc)
		self.regbook = regbook
		self.sep1 = ";"
		self.sep2 = ","
		self.errors = {
					"Intersection" : "No intersection found between elements.",
					"Syntax"       : "Not a valid search pattern.",
					"Features"     : "Not all features found in known descriptions.",
				}

	def validate(self, instring):
		pass

	def parse(self, instring):
		# Validate
		self.validate(instring)

		# Parse
		positions = instring.split(self.sep1)
		searchstring = ""

		for position in positions:
			
			# If regex expression
			if position in self.regbook:
				searchstring+=self.regbook[position]
				continue

			# If feature pattern
			ands = position.split(self.sep2)
			include = set([s for v in self.invertbook.values() for s in v])
			
			# Find intersection of phonemes containing all ands
			for feature in ands:
				if not self.invertbook[feature]:
					raise ValueError(self.errors["Features"]+" "+feature)
				include = include & self.invertbook[feature]

			# If no intersection found
			if not include: raise ValueError(self.errors["Intersection"])

			searchstring+="["+"".join(include)+"]"

		return "^"+searchstring+"$"



class PhonBook(object):

	def __init__(self):
		self.orth2phon  = {}
		self.phondesc   = defaultdict(lambda: set())
		self.formatting = {}
		self.indices    = defaultdict()

	def read(self, fpath):
		workbook = xlrd.open_workbook(fpath)
		dsheet = workbook.sheet_by_index(0)

		start_phon	  = 2
		start_feature = 5

		features = dsheet.row_values(1, start_feature)
		phonemes = dsheet.col_values(0, start_phon)

		for p, i in zip(phonemes, range(start_phon, len(phonemes)+start_phon)):
			if p:

				# Get piesps code
				self.orth2phon[p] = dsheet.cell_value(i, 1)

				# Add alpha index
				self.indices[self.orth2phon[p]] = int(dsheet.cell_value(i, 3))				

				# Get format code
				self.formatting[self.orth2phon[p]] = dsheet.cell_value(i, 2)

				# Get phone description
				for f, j in zip(features, range(start_feature, len(features)+start_feature)):
					invalue = dsheet.cell_value(i, j)

					if invalue:
						self.phondesc[self.orth2phon[p]].add(f)
						#if f not in self.phondesc[self.orth2phon[p]]: self.phondesc[self.orth2phon[p]].append(f)
						
						if invalue == "?":
							self.phondesc[self.orth2phon[p]].add("-"+f)

					else:
						self.phondesc[self.orth2phon[p]].add("-"+f)


				for char in phonemes:
					if char != p: self.phondesc[self.orth2phon[p]].add("-"+char)

		print(self.indices)
	def validate(self):
		pass


class Root(object):

	def __init__(self, phonbook):
		self._phonbook = phonbook
		self.orthform = None
		self.phonorig = None
		self.phonedit = None
		self.formatted = ""
		self.prefix   = ""
		self.suffix   = ""
		self.index    = -1
		self.error  = False
		self.attributes = dict()

	def __str__(self):
		if not self.orthform:
			raise ValueError("Orthographic form not found. Please run update(orthform)")
		else:
			return self.orthform

	def update(self, orthform, index, prefix, suffix, attr = dict()):
		self.prefix = prefix
		self.suffix = suffix
		self.orthform   = orthform
		self.attributes = attr
		self.index = index
		try:
			self.decode()
			self.formatted = self.format(self.phonedit[-1])
		except ValueError:
			self.phonedit = orthform
			self.phonorig = orthform
			self.error = True

	def _translate(self, nodes):
		phonemes = ""
		for (i, j), orth_sequence in nodes:
			phonemes += self._phonbook.orth2phon[orth_sequence]

		return phonemes

	def format(self, phonemes):
		formatted = ""
		for phone in phonemes:
			formatted += self._phonbook.formatting[phone]
		return self.prefix+formatted+self.suffix

	def decode(self):
		if not self.orthform: 
			raise ValueError("Orthographic form not found. Please run update(s)")

		# Disambiguate parenthesis forms

		parenthesis_forms = ["".join(form) for form in ambiguate_par(self.orthform)]

		# Get possible phoneme-partionings of orthform
		possible_phonemes = []
		parses = []		
		#print(parenthesis_forms)
		#print(self._phonbook.orth2phon)
		for form in parenthesis_forms:
			phonemes = set()
			#print(form)
			for i, c in enumerate(form):
				for start, end in get_window_indices(i, max([len(form) for form in self._phonbook.orth2phon.keys()]), max_i=len(form)-1):
					orth = form[start:end]
					if orth in self._phonbook.orth2phon:
						phonemes.add(tuple([(start, end), (orth)]))
			
			# Search through possible phoneme sequences
			parses += [path for path in dfs(phonemes, form)]


		if not parses:
			raise ValueError("Could not parse orthographic form {}".format(self.orthform), "Unknown character or sequence of characters")

		# Mark if ambigious and choose shortest path
		#if len(parses) > 1:
		#	parses = sorted(parses, key=lambda l: len(l))
		#	parse = parses.pop(0)
		#	self.ambigous = parses
		#else:
		#	parse = parses[0]

		# Translate parse into phoneme string

		translated = [self._translate(parse) for parse in parses]

		if self.phonorig == self.phonedit:
			self.phonedit = translated

		self.phonorig = translated

