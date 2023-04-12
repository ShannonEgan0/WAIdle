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


class WordleCorpus:
    def __init__(self):
        self.corpus = dict()

    def prepare_corpus(self, chars=5):
        full_corpus = words.words()
        self.corpus = dict()
        for i in full_corpus:
            if i.isalpha() and len(i) == chars:
                self.corpus.update({i.upper(): {"score": 0, "match": 0, "exact": 0}})

    def update_corpus(self, char, positions, not_positions, counter=1, exact=None):
        char = char.upper()
        for position in positions:
            self.corpus = {word for word in self.corpus if word[position] == char}
        for position in not_positions:
            self.corpus = {word for word in self.corpus if word[position] != char and char in word}
        if exact is None:
            self.corpus = {word for word in self.corpus if counter <= word.count(char)}
        else:
            self.corpus = {word for word in self.corpus if counter == word.count(char)}
        return self.corpus

    def remove_char_from_corpus(self, char):
        self.corpus = {word for word in self.corpus if char not in word}
        return self.corpus

    def remove_multiple_chars(self, char, counter):
        self.corpus = {word for word in self.corpus if counter == word.count(char)}

    def qualify_corpus(self, heuristic=(1, 2), save=False):
        if heuristic[1] <= heuristic[0]:
            raise ValueError("Heuristic is invalid, index 1 must be greater than index 0")
        print("Evaluating Corpus...")
        corpus_dict = dict()
        counter = 0
        for word in self.corpus:
            counter += 1
            score, match, exact = 0, 0, 0
            for test_word in self.corpus:
                checked_chars = create_alphabet_dict()
                for position, char in enumerate(word):
                    checked = check_char(char, position, test_word, heuristic)
                    if checked:
                        if test_word.count(char) > checked_chars[char][1]:
                            match += 1
                            if checked == heuristic[1]:
                                exact += 1
                            score += checked
                            checked_chars[char][1] += 1
                            checked_chars[char][0] = checked
                        elif checked > checked_chars[char][0]:
                            score = score - heuristic[0] + checked
                            exact += 1

            corpus_dict.update({word: {"score": score, "match": match, "exact": exact}})
            print(f"Completed word {counter} / {len(self.corpus)} - {word}: {score}")

        self.corpus = corpus_dict.copy()

        d = sorted(corpus_dict.items(), key=lambda item: item[1]["score"], reverse=True)
        if save:
            self.save_corpus()

        print("FINISHED.")
        return d

    def save_corpus(self, suffix="Waidle Corpus"):
        d = sorted(self.corpus.items(), key=lambda item: item[1]["score"], reverse=True)
        print("Saving qualified corpus to file...")
        date = dt.datetime.now().date().strftime("%Y%m%d")
        filename = f"{suffix} ({len(d)} {date}).txt"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, ("Rank", "Word", "Score", "Match", "Exact"))
            writer.writeheader()
            counter = 0
            for row in d:
                counter += 1
                writer.writerow({"Rank": counter, "Word": row[0], "Score": row[1]["score"],
                                 "Match": row[1]["match"], "Exact": row[1]["exact"]})
        print(f"File saved as {filename}.")

    def load_corpus(self, filename):
        corpus = dict()
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, ("Rank", "Word", "Score", "Match", "Exact"))
            next(reader, None)
            for row in reader:
                corpus.update({row["Word"]: {"score": float(row["Score"]),
                                             "match": int(row["Match"]), "Exact": int(row["Exact"])}})
        self.corpus = corpus
        return corpus


class Waidle:
    def __init__(self, word, heuristic=(1, 1.5)):
        self.word = word.upper()
        self.corpus = WordleCorpus()
        self.corpus.prepare_corpus(chars=len(self.word))
        self.heuristic = heuristic
        if self.word not in self.corpus.corpus:
            raise KeyError("Word not recognized as valid word")

    def check_guess(self, guess_word):
        if guess_word == self.word:
            print(f"{guess_word.upper()} is the correct answer!")
            return True
        else:
            return False

    def guess(self, guess_word):
        guess_word = guess_word.upper()
        result = {char: {"score": [], "pos": [], "count": 0} for char in guess_word}
        for pos, char in enumerate(guess_word):
            char_number = guess_word.count(char)
            score = check_char(char, pos, self.word, self.heuristic)
            result[char]["score"].append(score)
            result[char]["pos"].append(pos)
            result[char]["count"] = char_number
        print(result)
        for char in result:
            # Issue remains here for multiple characters in guess vs result
            word_char_count = self.word.count(char)
            if result[char]["count"] > self.word.count(char):
                self.corpus.remove_multiple_chars(char, word_char_count)
            for x, s in enumerate(result[char]["score"]):
                if s == self.heuristic[1]:
                    result[char]["count"] -= 1
                    self.corpus.update_corpus(char, [result[char]["pos"][x]], [])
            for x, s in enumerate(result[char]["score"]):
                if s == self.heuristic[0] and result[char]["count"] >= 1:
                    result[char]["count"] -= 1
                    self.corpus.update_corpus(char, [], [result[char]["pos"][x]], counter=result[char]["count"])
            for x, s in enumerate(result[char]["score"]):
                if s == 0:
                    self.corpus.remove_char_from_corpus(char)
        print(self.corpus.corpus)
        print(len(self.corpus.corpus))
        self.check_guess(guess_word)

    def recommend(self, number=1):
        ordered = sorted(self.corpus.corpus.items(), key=lambda item: item[1]["score"], reverse=True)
        return ordered[0:number]


if __name__ == "__main__":
    main()
    a = Waidle("BORAX")
    a.corpus.load_corpus("Waidle Corpus (9972 20230411).txt")
    a.guess("RAISE")
    a.corpus.qualify_corpus()
