import codecs

def JxReadFile(File):
	"""Reads a tab separated text file and returns a list of tuples."""
	List = []
	File = codecs.open(File, "r", "utf8")
	for Line in File:
		List.append(tuple(Line.strip('\n').split('\t')))
	File.close()
	return List
