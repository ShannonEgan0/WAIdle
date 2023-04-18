from nltk.corpus import words
import csv
import datetime as dt
import random


def main():
    a = Waidle()
    a.play()


def check_char(char, position, word, heuristic=(1, 1.5)):
    # Checks a char and position relative to a word, and returns a value based on the correlation
    if char in word:
        if word[position] == char:
            return heuristic[1]
        else:
            return heuristic[0]
    return 0


def create_alphabet_dict():
    # Format of dict tuple is (Max Score, Count of chars)
    return {c: [0, 0] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def load_word_freq_dict(filename="frequency-alpha-alldicts.txt", chars=5):
    # Loads a corpus of tab spaced words with a frequency of occurrence from Google Ngrams
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        new = []
        for row in reader:
            new.append(row)
    newest = [[j for j in k if j != ''] for k in new]
    new_dict = {i[1].upper(): float(i[3][:-1]) for i in newest if len(i[1]) == chars}
    return new_dict


class WaidleCorpus:
    # Waidle Corpus object
    def __init__(self):
        self.corpus = dict()

    def prepare_corpus(self, word_list=words.words(), chars=5, freq_cutoff=2e-06):
        # Prepares corpus dictionary from a word list, drawing frequencies from load_word_freq_dict
        frequency_corpus = load_word_freq_dict(chars=chars)
        full_corpus = word_list
        self.corpus = dict()
        full_corpus = {i.upper() for i in full_corpus}
        for i in full_corpus:
            if i in frequency_corpus:
                if i.isalpha() and len(i) == chars and frequency_corpus[i] > freq_cutoff:
                    self.corpus.update({i: {"score": 0, "match": 0, "exact": 0, "frequency": frequency_corpus[i]}})

    # They are not currently used simultaneously, which may imply there could be a better design
    # Needs to be clear, this function only gets used if a char does exist in the answer
    def update_corpus(self, char, positions, not_positions, counter=1):
        # Updates corpus to reflect possible answers eliminated by a character guess
        char = char.upper()
        for position in positions:
            self.corpus = {word: self.corpus[word] for word in self.corpus if word[position] == char}
        for position in not_positions:
            self.corpus = {word: self.corpus[word] for word in self.corpus if word[position] != char and char in word}
        self.corpus = {word: self.corpus[word] for word in self.corpus if counter <= word.count(char)}
        return self.corpus

    def remove_char_from_corpus(self, char):
        # Removes all words in corpus that contain char
        self.corpus = {word: self.corpus[word] for word in self.corpus if char not in word}
        return self.corpus

    def remove_multiple_chars(self, char, counter):
        # Removing all words that have more occurrences of a particular character than occur than counter
        # Used in the instance of a word guess with multiple of the same char finding the number total
        self.corpus = {word: self.corpus[word] for word in self.corpus if counter == word.count(char)}

    def qualify_corpus(self, heuristic=(1, 1.5), save=False):
        # Qualifies entire corpus based on maximax algorithm
        # Checks every word in the corpus, and assigns it a score based on shared characters/positions with...
        # Each other word in the corpus
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

            corpus_dict.update({word: {"score": score, "match": match, "exact": exact,
                                       "frequency": self.corpus[word]["frequency"]}})
            print(f"Completed word {counter} / {len(self.corpus)} - {word}: {score}", self.corpus[word]["frequency"])

        self.corpus = corpus_dict.copy()
        corpus_sorted = sorted(corpus_dict.items(), key=lambda item: item[1]["score"], reverse=True)
        if save:
            self.save_corpus()

        print("FINISHED.")
        return corpus_sorted

    def save_corpus(self, suffix="Waidle Corpus"):
        # Saves a qualified corpus to file with prescribed suffix for later reference
        d = sorted(self.corpus.items(), key=lambda item: item[1]["score"], reverse=True)
        print("Saving qualified corpus to file...")
        date = dt.datetime.now().date().strftime("%Y%m%d")
        filename = f"{suffix} ({len(d)} {date}).txt"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, ("Rank", "Word", "Score", "Match", "Exact", "Frequency"))
            writer.writeheader()
            counter = 0
            for row in d:
                counter += 1
                writer.writerow({"Rank": counter, "Word": row[0], "Score": row[1]["score"],
                                 "Match": row[1]["match"], "Exact": row[1]["exact"],
                                 "Frequency": row[1]["frequency"]})
        print(f"File saved as {filename}.")

    def load_corpus(self, filename):
        # Re-loads a qualified corpus for reference to reduce processing time
        corpus = dict()
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, ("Rank", "Word", "Score", "Match", "Exact", "Frequency"))
            next(reader, None)
            for row in reader:
                corpus.update({row["Word"]: {"score": float(row["Score"]), "match": int(row["Match"]),
                                             "exact": int(row["Exact"]), "frequency": float(row["Frequency"])}})
        self.corpus = corpus
        return corpus


class Waidle:
    # Main Waidle game object
    def __init__(self, word=None, heuristic=(1, 1.5), chars=5):
        # Initializes with a WaidleCorpus object. If word is left None, a random word from the corpus is selected.
        # If chars is left as 5, the randomly selected word will be of length 5
        # chars will be ignored if a word is specified
        self.corpus = WaidleCorpus()
        self.chars = chars
        if word is None:
            self.corpus.prepare_corpus(chars=chars)
            self.word = random.choice(list(self.corpus.corpus.keys()))
            while self.corpus.corpus[self.word]["frequency"] < 60e-06:
                self.word = random.choice(list(self.corpus.corpus.keys()))
        else:
            self.word = word.upper()
            self.corpus.prepare_corpus(chars=len(self.word))
            if self.word not in self.corpus.corpus:
                raise KeyError("Word not recognized as valid word")
        self.heuristic = heuristic

    def check_guess(self, guess_word):
        # Checks whether a guess is the correct answer
        if guess_word == self.word:
            print(f"{guess_word.upper()} is the correct answer!")
            return True
        else:
            return False

    def guess(self, guess_word):
        # Performa guess in the sense of the game
        # Checks each char in word for correctness, and then stores these for updating the corpus
        guess_word = guess_word.upper()
        result = {char: {"score": [], "pos": [], "count": 0} for char in guess_word}
        for pos, char in enumerate(guess_word):
            char_number = guess_word.count(char)
            score = check_char(char, pos, self.word, self.heuristic)
            result[char]["score"].append(score)
            result[char]["pos"].append(pos)
            result[char]["count"] = char_number
        return result

    def update_from_guess(self, result):
        # Updates corpus based on a guess result (ie. character correctness and position)
        for char in result:
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

    def recommend(self, number=1):
        # Recommends a list of suggested gyesses of length == number based on first score, then frequency
        ordered = sorted(self.corpus.corpus.items(), key=lambda item: (item[1]["score"],
                                                                       item[1]["frequency"]), reverse=True)
        return ordered[0:number]

    def solve(self, starting_qualification_file="Waidle Corpus (4203 20230413).txt"):
        # Solves a game by guesses recommended guesses until the correct guess is found
        if starting_qualification_file:
            self.corpus.load_corpus(starting_qualification_file)
        else:
            self.corpus.qualify_corpus()
        counter = 0
        guessed = []
        while True:
            counter += 1
            guess = self.recommend()[0][0]
            guessed.append(guess)
            if self.check_guess(guess):
                print(f"SOLVED with the answer {guess} in {counter} guesses!")
                for i in guessed:
                    print(f" -> {i}", end="")
                print()
                return counter
            self.update_from_guess(self.guess(guess))
            self.corpus.qualify_corpus()

    def play(self):
        # Allows a human to play a WAIdle game directly in the console
        guess = self.make_guess()
        while not self.check_guess(guess):
            for x, char in enumerate(guess):
                checked = check_char(char, x, self.word)
                if checked == self.heuristic[1]:
                    checked = char
                elif checked == 0:
                    checked = "_"
                elif checked == self.heuristic[0]:
                    checked = char.lower()
                print(checked, end='')
            print()
            guess = self.make_guess()

    def make_guess(self):
        # Calls for a human guess in a game
        guess = input("Enter your guess: ").upper()
        while len(guess) != self.chars:
            print(f"Incorrect guess, must be {self.chars} characters long.")
            guess = input("Enter your guess: ").upper()
        return guess

    def test_setup(self):
        # Tests a game of WAIdle for each word in a corpus, to assess effectiveness of the algorithm
        # Takes a long time to perform, especially with a larger corpus: O(n**2)
        word_list = self.corpus.corpus.keys()
        results = dict()
        distribution = dict()
        counter = 0
        total = len(word_list)
        for word in word_list:
            counter += 1
            b = Waidle(word)
            c = b.solve()
            if c in distribution:
                distribution[c] += 1
            else:
                distribution.update({c: 1})
            results.update({word: c})
            print()
            print(f"Completed word {counter} / {total}")
        return results, distribution


class QWaidle:
    # Starting to assemble the beones of a reinforcment learning approach to solving a game
    def __init__(self, game=Waidle(), alpha=0.5, epsilon=0.1):
        self.game = game
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        pass

    def get_q_value(self, state, action):
        pass


if __name__ == "__main__":
    main()
