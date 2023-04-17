import csv
from nltk.corpus import words

with open("frequency-alpha-alldicts.txt", 'r') as f:
    reader = csv.reader(f, delimiter=' ')
    new = []
    for row in reader:
        new.append(row)


newest = [[j for j in k if j != ''] for k in new]
print(newest[0])
newest = [i for i in newest if len(i[1]) == 5]

new_dict = {i[1].upper(): float(i[3][:-1]) for i in newest}
for i in newest:
    i[1] = i[1].upper()
    i[3] = float(i[3][:-1])

# a = list(filter(lambda item: (item[3] > 5e-06), newest))
a = list(zip(*newest))

full_corpus = words.words()
corpus = set()
for i in full_corpus:
    if i.isalpha() and len(i) == 5:
        corpus.add(i)

counter = 0
for i in corpus:
    if i.upper() not in a[1]:
        counter += 1
        print(i)

print("FINISHED")
print(counter)
