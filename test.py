import pyphone_models as pie
import xlrd
import pyphone_utils as pie_utils
import sort_result

RegBook = {
    "*" : ".*"
}

#workbook = xlrd.open_workbook("ROOTS_excel_main.xls")
#dsheet = workbook.sheet_by_index(0)
#orths = set()

#for root in dsheet.col_values(0, 1):
#    for char in root:
#        orths.add(char)

#print("\t".join(orths))

phonbook = pie.PhonBook()
phonbook.read("piesps.xls")
#print(phonbook.phondesc)

C = pie.Corpus(phonbook, None)
C.load_corpus("sidsel.xls")

#roots = [sorted(root.phonedit, key= lambda x: len(x))[-1] for root in C._roots]

#indices, _ = sort_result.argsort_from_index(roots, phonbook.indices)

#print([C._roots[i].phonedit for i in indices])


f = open("roots.txt", "w")
f.write("\t".join(["index", "orthform", "formatted", "phonedit", "phonorig",])+"\n")

for root in C._roots:
	print(root.phonorig)
	print(root.phonedit)
	print(root.orthform)
	f.write("\t".join([str(root.index), root.orthform, root.formatted, ";".join(root.phonedit), ";".join(root.phonorig)])+"\n")#+"\t"+"\t".join([root.attributes[key] for key in C._attributes.keys()])+"\n")


#print([root.phonedit for root in C._roots])

#pie_utils.ambiguate_par("(s)he(j)")


#parser = pie.SearchString(phonbook, RegBook)
#searchstring = "unasp;*"
#s = parser.parse(searchstring)
#print("input:", searchstring)
#print("searchstring:", s)

#print([match.orthform for match in C.search(s)])

#print(s)

