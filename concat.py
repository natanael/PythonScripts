#!C:\Program Files\sap\hdbclient\Python\python.exe
"""
This script was designed to be used together with BODS in order to fulfill a functionality that did not exist (the pushdown of a cross-source query using WHERE IN clauses).

This script reads a file in the format:
1234
1234
...
1234
1234
And can convert it into the formats:
SB:
1234,1234,
1234,1234,
1234,1234
1234,1234,
1234,1234,
1234,1234
SKP (max of 1459 keys, Progress OpenEdge 10.2 limitation):
"1234","1234",
"1234","1234",
"1234","1234"
"1234","1234",
"1234","1234",
"1234","1234"
It was made so I could turn some keys into WHERE IN clauses and use it on the pushdown_sql clauses.
"""
import sys, math, os

def distribute(arr):
  full_v = []
	[[full_v.append(row) for row in line] for line in arr]
	full_v.sort(key=len)
	new_a = []
	for x in range(len(arr)): new_a.append([])
	while len(full_v)>0:
		count = 0
		for line in new_a:
			if len(full_v)==0: break
			if len(','.join(line)) > 997: continue
			else: count +=1
			line.append(full_v.pop())
		if count == 0:
			print "All lines are full, and the array is still %s items long." % (len(full_v))
			exit(0)
	return new_a

def concat(arr, variables):
	g=[]
	l=[]
	for x in arr:
		l.append(x)
		if len(l) % (variables*4)==0:
			g.append(l)
			l=[]
	if len(l):
		g.append(l)
	new_g = []
	for block in g:
		new_g.append(distribute(block))
	return new_g
	
def main_sb(min_of_variables=1):
	in_file = [ln[:-1] for ln in InFile]
	main(in_file,min_of_variables=min_of_variables)

def main_skp(min_of_variables=3):
	in_file = ["'%s'" % ln[:-1] for ln in InFile]
	main(in_file, max_items=1459, min_of_variables=min_of_variables)
	
def main(in_file, max_items=0,min_of_variables=1):
	tbl = []
	in_file.sort(key=len)
	
	min_of_queries = 1
	if max_items:
		min_of_queries = int(math.ceil(len(in_file)/float(max_items)))
		print "Lenght of the largest first max_items keys: %d" % len(','.join(in_file[:max_items]))
	print "To make an optimal query with the major max_items keys would take %d variables" % int(math.ceil(len(','.join(in_file[:max_items]))/4000.0))
	print "You choose to use %d variables." % min_of_variables
	
	min_of_lines = int(math.ceil((len(','.join(in_file))+2*min_of_queries)/1000.0))
	print "The number of lines calculated by the number of lines required is %d/%d" % (min_of_queries*min_of_variables*4, min_of_lines )
	if min_of_lines > min_of_queries*min_of_variables*4:
		print "The number of queries was adjusted to match the required lines, from %d to %d." % (min_of_queries, int(math.ceil(min_of_lines/float(min_of_variables*4))))
		min_of_queries = int(math.ceil(min_of_lines/float(min_of_variables*4)))
	
	print "The length of the file must be of at least %d chars." % (len(','.join(in_file))+2*min_of_queries)
	
	for x in range(min_of_queries):
		for y in range(min_of_variables*4):
			tbl.append([])
	
	lines = len(tbl)
	print "The output file will have %d lines." % lines
	
	tbl[0]=in_file
	
	liner = concat(distribute(tbl),min_of_variables)
	
	#Keeps the script from generating an output that will crash SKP
	for query in liner:
		if max_items:
			assert(len(query) <= max_items)
		#Keeps the script from generating lines larger than 1000 chars
		for line in query:
			assert(len(','.join(line)) < 1000)
	
	fline="\n".join(["%s" % ',\n'.join([','.join(b) for b in a]) for a in liner])
	
	OutFile.write(fline)
	
	print("lines: %d chars: %d keys: %d queries: %d" % (fline.count("\n")+1,len(fline),len(in_file),len(liner)))

if __name__ == '__main__':
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-t", "--type", dest="type", choices=("SKP","SB") , default=False, help="Sets the script for either SKP or SB.")
	parser.add_option("-n", "--number", dest="number" , default=0, help="Sets how many variables it should be split for. (each variable reads 4 lines of 1000 chars)", type="int")
	parser.add_option("-i", "--input", default='', dest="in_file", help="The path for the input file. It's taken for a file with a value per line.", type="string")
	parser.add_option("-o", "--output", default='', dest="out_file", help="The path for the output file. It will be overwritten.", type="string")
	opts, args = parser.parse_args()
	
	if not os.path.exists(opts.in_file) and not len(opts.out_file):
		parser.error("Usage: concat.py -i=<input_file.txt> -o=<output_file.txt>")
	else:	
		InFile = open(opts.in_file,'r')
		OutFile = open(opts.out_file,'w')	
	
	if opts.type == 'SKP':
		if opts.number:
			main_skp(min_of_variables=opts.number)
		else:
			main_skp()
	else:
		if opts.number:
			main_sb(min_of_variables=opts.number)
		else:
			main_sb()
