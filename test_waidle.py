from waidle import *
import random
import pytest

a = WordleCorpus()
a.prepare_corpus()

minimum = 1000000000

b = update_corpus('A', None, [1, 2, 3], a.corpus)
print(len(b))
for x in range(5):
    print(random.choice(list(b)))



print(check_char('A', 1, 'APPLE') == 1,
check_char('A', 0, 'APPLE') == 2,
check_char('Z', 0, 'APPLE') == 0)

print("RUNNING...")
corpus_dict = dict()
counter = 0
for word in a.corpus:
    counter += 1
    score = 0
    for test_word in a.corpus:
        checked_chars = create_alphabet_dict()
        for position, char in enumerate(word):
            checked = check_char(char, position, test_word)
            if checked[0]:
                if checked[1] > checked_chars[char][1]:
                    score += checked[0]
                    checked_chars[char][1] += 1
                    checked_chars[char][0] = checked[0]
                elif checked[0] > checked_chars[char][0]:
                    score = score - 1 + checked[0]

    corpus_dict.update({word: score})
    print(f"Completed word {counter} / {len(a.corpus)} - {word}: {score}")

d = sorted(corpus_dict.items(), key=lambda item: item[1])
print("FINISHED.")

best = ("", 0)
for i in a:
    if corpus_dict[i] > best[1]:
        best = (i, corpus_dict[i])