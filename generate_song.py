#generate_song.py

from collections import defaultdict
import pickle
import random as rng
import re
import subprocess
from urllib import request, error

ORDER = 4
pronounciation_guide = dict()


def to_kirshenbaum(line):
	proc = subprocess.run(['espeak','-v','en-us','-q','-x',line], encoding='ascii',stdout=subprocess.PIPE)
	return proc.stdout


if __name__ == '__main__':

	transition = defaultdict(lambda:[])
	chars = ' '*ORDER
	line_endings = []
	with open('input.txt','r') as f:
		phonetics = to_kirshenbaum(f.read())
		phonetics = re.sub(r'\n+', '\n', phonetics)
		for char in reversed(phonetics):
			transition[chars].append(char)
			if chars[-1] == '\n':
				line_endings.append((char+chars).split('\n')[-2])
			chars = char+chars[:-1]

	song = ""
	for i in range(10):
		lines = []
		for j in range(2):
			line = rng.choice(line_endings)
			while True:
				if line[:ORDER] in transition:
					line = rng.choice(transition[line[:ORDER]]) + line
					if line[0] == '\n':
						line = line[1:]
						break
				else:
					break
			lines.append(line)

		for j in range(2):
			line = max(lines[j][max(0,lines[j].rfind("'")):], lines[j][-ORDER:], key=len)
			while len(line.replace('\n','')) < len(lines[j]):
				if line[:ORDER] in transition:
					line = rng.choice(transition[line[:ORDER]]) + line
				else:
					print("{} was not in the transition matrix!!!".format(repr(line[:ORDER])))
					break
			lines.append(line.replace('\n',''))

		song += "_:_:_:\n".join(lines)+"_:_:_:\n"

	print(song)
	with open('output.txt', 'w') as f:
		f.write(song)
	subprocess.call(['espeak','-v','en-us','-s','100','[['+song+']]'])
