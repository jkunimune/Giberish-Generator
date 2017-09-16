#generate_song.py

from collections import defaultdict
import pickle
import random as rng
import subprocess
from urllib import request, error

ORDER = 3
pronounciation_guide = dict()


def to_kirshenbaum(line):
	print("start")
	proc = subprocess.run(['espeak','-v','en','-s','1000','-x',line], encoding='ascii',stdout=subprocess.PIPE)
	print("done")
	return proc.stdout


if __name__ == '__main__':

	transition = defaultdict(lambda:[])
	chars = ' '*ORDER
	with open('input.txt','r') as f:
		for char in to_kirshenbaum(f.read()):
			transition[chars].append(char.lower())
			chars = chars[1:]+char.lower()

	thing = rng.choice(list(transition))
	for i in range(300):
		if thing[-ORDER:] in transition:
			thing += rng.choice(transition[thing[-ORDER:]])
		else:
			break

	print(thing)
	with open('output.txt', 'w') as f:
		f.write(thing)
	subprocess.call(["espeak", "-v", "en", "-s", "100", "[["+thing+"]]"])
