#generate_song.py

from collections import defaultdict
import math
import numpy as np
import os
import pickle
import random as rng
import re
import subprocess
import tempfile
import wave


MEMORY_DECAY = .4 #the last last phoneme has about this as much effect as the last phoneme
MIN_ORDER = 2
MAX_ORDER = int(math.log(.01, MEMORY_DECAY)) #automatically stop memorising when the effect becomes negligible
PREF_LENGTH = 30

CHARACTER = list("\n _-,':?lOmEStak@#gnIeUopujidrTsVwZAhfbDNLvz0123")
INDEX = {ph:i for i,ph in enumerate(CHARACTER)}


def learn_english():
	transitions = [] #the list of transition dicts for each order up to the length of the input
	for i in range(MAX_ORDER):
		transitions.append(defaultdict(lambda:np.zeros(len(CHARACTER))))

	with open('input.txt','r') as f:
		inline = re.sub(r'\n+', ' ', f.read())
		proc = subprocess.run(['espeak','-v','en-us','-q','-x',inline], encoding='ascii', stdout=subprocess.PIPE)
		source = re.sub(r'[;!]', '', re.sub(r'\n ', '\n', proc.stdout)) #I've no idea from whence these ;s and !s come, but they ruin everything.
		print('"""')
		print(source)
		print('"""')
		for i in range(len(source)):
			for j in range(1,min(MAX_ORDER,i)): #skip the zeroth order transition matrix, because we will always start with at least a newline
				transitions[j][source[1-i:1-i+j]][INDEX[source[-i]]] += 1

	for i, m in enumerate(transitions):
		transitions[i] = dict(m)

	with open('data.pic', 'wb') as f:
		pickle.dump(transitions, f)

	return transitions


def markov_chain(seed, transitions, length=float('inf'), force_length=True, not_first=None):
	line = seed
	while True:
		vector = np.zeros(len(CHARACTER))
		for i in range(min(len(line), MIN_ORDER), min(len(line)+1, MAX_ORDER)):
			if line[:i] in transitions[i]:
				vector = vector + (MEMORY_DECAY**i) * (transitions[i][line[:i]]/transitions[i][line[:i]].sum())
			else:
				break
		if len(line) >= length and vector[INDEX['\n']]/vector.sum() > .01: #exit if we are at capacity and a newline next is plausible
			break
		if force_length: #there can be no newline if the length is fixed
			vector[INDEX['\n']] = 0
		if line == seed and not_first is not None: #prevent some character from happening next (for rhyming purposes)
			vector[INDEX[not_first]] = 0
		if vector.sum() == 0: #exit if there is literally no possible next step (unlikely)
			break
		else:
			line = np.random.choice(CHARACTER, p=vector/vector.sum()) + line
		if line[0] == '\n': #line-breaks signal the end of the thing
			line = line[1:]
			break
	return line


if __name__ == '__main__':

	fd, temp = tempfile.mkstemp()

	try:
		with open('data.pic', 'rb') as f:
			transitions = pickle.load(f)
	except IOError:
		transitions = learn_english()

	text = ""
	speech = []
	for i in range(8):
		lines = []
		lines.append(markov_chain("\n", transitions, length=PREF_LENGTH, force_length=False))
		lines.append(markov_chain("\n", transitions, length=len(lines[0])))
		for j in range(2):
			idx = lines[j].rfind("'")
			if idx > 0:
				lines.append(markov_chain(lines[j][idx:], transitions, length=len(lines[j]), not_first=lines[j][idx-1]))
			elif idx < 0:
				lines.append(markov_chain("\n", transitions, length=len(lines[j])))
			else:
				lines.append(lines[j])

		q_text = "".join([line.strip()+"_:_:_:\n" for line in lines])
		proc = subprocess.run(['espeak','-v','en-us','-s','120','-w',temp,'[['+q_text+']]'], stdout=subprocess.PIPE)
		w = wave.open(temp, 'rb')

		print(q_text, end='')
		text += q_text
		speech.append((w.getparams(), w.readframes(w.getnframes())))
		w.close()

	os.close(fd)
	os.remove(temp)

	with open('output.txt', 'w') as f:
		f.write(text)

	outf = wave.open('output.wav', 'wb')
	outf.setparams(speech[0][0])
	for params, frames in speech:
		outf.writeframes(frames)
	outf.close()
