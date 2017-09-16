#generate_song.py

from collections import defaultdict
import pickle
import random as rng
import subprocess
from urllib import request, error

from kirshenbaum import _unicode_to_ascii
from morewords import more_words

ORDER = 3
pronounciation_guide = dict(more_words)


def lookup(word):
	""" Looks it up on Wiktionary """
	response = request.urlopen(request.Request('http://en.wiktionary.org/wiki/{}'.format(word)))
	return response.read().decode(response.headers.get_content_charset())


def to_kirshenbaum(line):
	kirshenbaum = []
	for word in line.split():
		word = word.strip(' \n,.?!)(][-"\':').lower()
		if word in pronounciation_guide:
			if pronounciation_guide[word] is not None:
				kirshenbaum.append(pronounciation_guide[word])
		else:
			try:
				wiktionary_page = lookup(word)
			except error.HTTPError:
				if len(word) > 2 and word[-2:] == 'in':
					try:
						wiktionary_page = lookup(word[:-2]+'ing')
					except error.HTTPError:
						wiktionary_page = None
					else:
						ing_to_in = True
				else:
					try:
						wiktionary_page =lookup(word.capitalize())
					except error.HTTPError:
						wiktionary_page = None

			if wiktionary_page is None:
				print('"{}" is not a word apparently'.format(word))
				pronounciation_guide[word] = None
			else:
				if '<span class="IPA">/' in wiktionary_page:
					wiktionary_page = wiktionary_page[wiktionary_page.index('<span class="IPA">/')+19:]
					ipa_word = wiktionary_page[:wiktionary_page.index('/')]
					ascii_word = _unicode_to_ascii(ipa_word)
					pronounciation_guide[word] = ascii_word
					kirshenbaum.append(ascii_word)
				else:
					raise Exception('How do you pronounce "{}"?'.format(word))
					pronounciation_guide[word] = None

	return ' '.join(kirshenbaum)


if __name__ == '__main__':
	try:
		with open('dictionary.pic', 'rb') as f:
			pronounciation_guide.update(pickle.load(f))
	except FileNotFoundError:
		pass

	transition = defaultdict(lambda:[])
	chars = ' '*ORDER
	with open('input.txt','r') as f:
		for line in f:
			for char in to_kirshenbaum(line):
				transition[chars].append(char.lower())
				chars = chars[1:]+char.lower()

	with open('dictionary.pic', 'wb') as f:
		pickle.dump(pronounciation_guide, f)

	thing = rng.choice(list(transition))
	for i in range(300):
		if thing[-ORDER:] in transition:
			thing += rng.choice(transition[thing[-ORDER:]])
		else:
			break

	print(thing)
	# with open('output.txt', 'w') as f:
	# 	f.write(thing)
	subprocess.call(["espeak", "-v", "en", "[["+thing+"]]"])
