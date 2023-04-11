from nltk.corpus import words
import csv
import datetime as dt


def main():
    pass


def check_char(char, position, word, heuristic=(1, 2)):
    # Returns score for a char in a specific position
    if char in word:
        if word[position] == char:
            return heuristic[1]
        else:
            return heuristic[0]
    return 0


def create_alphabet_dict():
    # Format of dict tuple is (Max Score, Count of chars)
    return {c: [0, 0] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def update_corpus(char, positions, not_positions, corpus, counter=1):
    char = char.upper()
    for position in positions:
        corpus = {word for word in corpus if word[position] == char}
    for position in not_positions:
        corpus = {word for word in corpus if word[position] != char and char in word}
    corpus = {word for word in corpus if counter <= word.count(char)}
    return corpus


class WordleCorpus:
    def __init__(self):
        self.corpus = set()

    def prepare_corpus(self, chars=5):
        full_corpus = words.words()
        for i in full_corpus:
            if i.isalpha() and len(i) == chars:
                self.corpus.add(i.upper())

    def qualify_corpus(self, heuristic=(1, 2)):
        print("Evaluating Corpus...")
        corpus_dict = dict()
        counter = 0
        for word in self.corpus:
            counter += 1
            score = 0
            for test_word in self.corpus:
                checked_chars = create_alphabet_dict()
                for position, char in enumerate(word):
                    checked = check_char(char, position, test_word, heuristic)
                    if checked:
                        if test_word.count(char) > checked_chars[char][1]:
                            score += checked
                            checked_chars[char][1] += 1
                            checked_chars[char][0] = checked
                        elif test_word.count(char) > checked_chars[char][0]:
                            score = score - 1 + checked

            corpus_dict.update({word: score})
            print(f"Completed word {counter} / {len(self.corpus)} - {word}: {score}")

        d = sorted(corpus_dict.items(), key=lambda item: item[1], reverse=True)
        print("Saving qualified corpus to file...")
        date = dt.datetime.now().date().strftime("%Y%m%d")
        with open(f"Waidle Corpus ({len(d)} {date}).txt", 'w') as f:
            writer = csv.DictWriter(f, ("Word", "Score"))
            writer.writeheader()
            counter = 0
            for row in d:
                counter += 1
                writer.writerow({"Rank": counter, "Word": row[0], "Score": row[1]})

        print("FINISHED.")
        return d


class Waidle:
    def __init__(self, word, heuristic=(1, 2)):
        self.word = word.upper()
        self.corpus = WordleCorpus()
        self.corpus.prepare_corpus(chars=len(self.word))
        self.corpus = self.corpus.corpus
        self.heuristic = heuristic

        if self.word not in self.corpus:
            raise KeyError("Word not recognized as valid word")

    def guess(self, guess_word):
        result = {char: {"score": [], "pos": [], "count": 0} for char in guess_word}
        for pos, char in enumerate(guess_word):
            char_number = guess_word.count(char)
            score = check_char(char, pos, self.word, self.heuristic)
            result[char]["score"].append(score)
            result[char]["pos"].append(pos)
            result[char]["count"] = char_number
        print(result)
        for char in result:
            for x, s in enumerate(result[char]["score"]):
                if s == 2:
                    result[char]["count"] -= 1
                    self.corpus = update_corpus(char, [result[char]["pos"][x]], [], self.corpus)
            for x, s in enumerate(result[char]["score"]):
                if s == 1 and result[char]["count"] >= 1:
                    self.corpus = update_corpus(char, [], [result[char]["pos"][x]], self.corpus,
                                                counter=result[char]["count"])
                    # Need to recheck if this is redundant or if the previous section is redundant
                    result[char]["count"] -= 1
            for x, s in enumerate(result[char]["score"]):
                if s == 0:
                    self.corpus = self.corpus = {word for word in self.corpus if char not in word}
        print(self.corpus)
        print(len(self.corpus))


if __name__ == "__main__":
    main()
    a = Waidle("LEAFY")
