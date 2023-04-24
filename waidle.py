from nltk.corpus import words
import csv
import datetime as dt
import random
import copy
from datetime import datetime
from requests import get
import re
import os
import matplotlib.pyplot as plt


def main():
    w = Waidle()
    w.solve()


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


def source_wordle_list() -> object:
    url = "https://www.nytimes.com/games-assets/v2/wordle.1ddd50e23d5bc72353ab.js"
    r = get(url).text
    r = re.search(r'zymic",".*?]', r).group()[7:-1]
    r = r.replace('"', '').split(",")
    return r


def sum_sq(listed, count=False):
    sumsq = 0
    words_count = 0
    for i in list(listed):
        words_count += i[1]
        sumsq += i[0] * i[1]
    if count:
        return sumsq, words_count
    return sumsq


def plot_test_results(dists, heuristics, title="Comparison of Different Heuristic Values"):
    if len(dists) == 2:
        print(dists)
        avg1, count = sum_sq(dists[0].items(), count=True)
        avgs = [avg1 / count, sum_sq(dists[1].items()) / count]
        color = ("blue", "red", "green")
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex="all")
        xys_all, max_ax1 = [], []
        for h, i in enumerate(dists):
            xys = list(zip(*sorted(list(i.items()))))
            xys_all.append(xys)
            xs, ys = xys[0], xys[1]
            max_ax1.append(max(ys))
            ax1.plot(xs, ys, label=f"Heuristic Ratio: {heuristics[h]}, Average: {round(avgs[h], 2)}", color=color[h])
        xs = xys_all[0][0]
        diffs = [xys_all[0][1][x] - xys_all[1][1][x] for x in range(len(xys_all[0][0]))]
        ax2.plot(xs, diffs, color=color[2])
        ax2.plot([xys_all[0][0][0], xys_all[0][0][-1]], [0, 0], color="black")
        ax2.set_xlim(xys_all[0][0][0], xys_all[0][0][-1])
        max_y = max((abs(max(diffs)), abs(min(diffs))))
        ax2.set_ylim(-1 * max_y - 5, max_y + 5)
        ax2.set_xlabel("Number of Guesses")
        ax2.set_ylabel("Guess Difference Between Heuristics")
        ax1.set_ylabel("Number of Words")
        ax1.grid(which="both")
        ax2.grid(which="both")
        ax1.set_ylim(0, max(max_ax1) + max(max_ax1) * 0.05)
        ax1.legend()
        fig.suptitle(title)
        plt.tight_layout()
        plt.show()
    else:
        raise ValueError("Two distributions required for comparison")


# For performance, need to adjust this so that a qualification file can be used from default at creation of an object
# Rather than running prepare corpus on initialization
class WaidleCorpus:
    # Waidle Corpus object
    def __init__(self, verbose=True):
        self.corpus = dict()
        self.verbose = verbose

    def prepare_corpus(self, word_list=words.words(), chars=5, freq_cutoff=2e-06, curate=False):
        # Prepares corpus dictionary from a word list, drawing frequencies from load_word_freq_dict
        frequency_corpus = load_word_freq_dict(chars=chars)
        full_corpus = word_list
        full_corpus = {i.upper() for i in full_corpus}
        for i in full_corpus:
            if i in frequency_corpus:
                if i.isalpha() and len(i) == chars and frequency_corpus[i] > freq_cutoff:
                    self.corpus.update({i: {"score": 0, "match": 0, "exact": 0, "frequency": frequency_corpus[i]}})
            elif not curate:
                if i.isalpha() and len(i) == chars:
                    self.corpus.update({i: {"score": 0, "match": 0, "exact": 0, "frequency": 0}})

    # They are not currently used simultaneously, which may imply there could be a better design
    # Needs to be clear, this function only gets used if a char does exist in the answer
    def update_corpus(self, char, positions, not_positions):
        # Updates corpus to reflect possible answers eliminated by a character guess
        char = char.upper()
        for position in positions:
            self.corpus = {word: self.corpus[word] for word in self.corpus if word[position] == char}
        for position in not_positions:
            self.corpus = {word: self.corpus[word] for word in self.corpus if word[position] != char and char in word}
        return self.corpus

    def multiple_chars(self, char, counter):
        # This is the case of multiple of a character in a word, but less than or equal to the answer word
        # So it remains that there could be more characters in the word
        self.corpus = {word: self.corpus[word] for word in self.corpus if counter <= word.count(char)}
        return self.corpus

    def excess_chars(self, char, counter):
        # Removing all words that have more occurrences of a particular character than occur than counter
        # Used in the instance of a word guess with multiple of the same char finding the number total
        self.corpus = {word: self.corpus[word] for word in self.corpus if counter == word.count(char)}

    def qualify_corpus(self, heuristic=(1, 1.5), save=False):
        # Qualifies entire corpus based on maximax algorithm
        # Checks every word in the corpus, and assigns it a score based on shared characters/positions with...
        # Each other word in the corpus
        if heuristic[1] <= heuristic[0]:
            raise ValueError("Heuristic is invalid, index 1 must be greater than index 0")
        if self.verbose:
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
            if self.verbose:
                print(f"Completed word {counter}/{len(self.corpus)} - {word}: {score}", self.corpus[word]["frequency"])

        self.corpus = corpus_dict.copy()
        corpus_sorted = sorted(corpus_dict.items(), key=lambda item: item[1]["score"], reverse=True)
        if save:
            self.save_corpus()
        if self.verbose:
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

    def load_corpus(self, filename, chars=5):
        # Re-loads a qualified corpus for reference to reduce processing time
        corpus = dict()
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, ("Rank", "Word", "Score", "Match", "Exact", "Frequency"))
            next(reader, None)
            for row in reader:
                corpus.update({row["Word"]: {"score": float(row["Score"]), "match": int(row["Match"]),
                                             "exact": int(row["Exact"]), "frequency": float(row["Frequency"])}})
        file_word_length = len(list(corpus.keys())[0])
        if file_word_length != chars:
            raise ImportError(f"File contains word of length {file_word_length}, not {chars}. Please try a different"
                              f"file, or a different word.")
        self.corpus = corpus
        return corpus


class Waidle:
    # Main Waidle game object
    def __init__(self, word=None, heuristic=(1, 1.5), chars=5, file=None, word_list=source_wordle_list(), verbose=True):
        # Initializes with a WaidleCorpus object. If word is left None, a random word from the corpus is selected.
        # If chars is left as 5, the randomly selected word will be of length 5
        # chars will be ignored if a word is specified
        self.corpus = WaidleCorpus(verbose=verbose)
        self.chars = chars
        if word is None:
            if not file:
                self.corpus.prepare_corpus(chars=chars, word_list=word_list)
            else:
                self.corpus.load_corpus(file, chars=chars)
            self.randomize_word()
            while self.corpus.corpus[self.word]["frequency"] < 60e-06:
                self.randomize_word()
        else:
            self.word = word.upper()
            if not file:
                self.corpus.prepare_corpus(chars=len(self.word), word_list=word_list)
            else:
                self.corpus.load_corpus(file, chars=len(self.word))
            if self.word not in self.corpus.corpus:
                raise KeyError("Word not recognized as valid word")
        self.heuristic = heuristic

    def randomize_word(self):
        self.word = random.choice(list(self.corpus.corpus.keys()))

    def check_guess(self, guess_word, printout=True):
        # Checks whether a guess is the correct answer
        if guess_word == self.word:
            if printout:
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
        # Updates corpus based on a guess result (i.e. character correctness and position)
        # This needs to be optimized, it got really messy when dealing with multiple characters, and took some damage
        for char in result:
            word_char_count = self.word.count(char)
            if result[char]["count"] > word_char_count:
                self.corpus.excess_chars(char, word_char_count)
            elif result[char]["count"] <= word_char_count:
                self.corpus.multiple_chars(char, word_char_count)
            for x, s in enumerate(result[char]["score"]):
                if s == self.heuristic[1]:
                    self.corpus.update_corpus(char, [result[char]["pos"][x]], [])
                elif s == self.heuristic[0] and result[char]["count"] >= 1:
                    self.corpus.update_corpus(char, [], [result[char]["pos"][x]])

    def recommend(self, number=1):
        # Recommends a list of suggested gyesses of length == number based on first score, then frequency
        ordered = sorted(self.corpus.corpus.items(), key=lambda item: (item[1]["score"],
                                                                       item[1]["frequency"]), reverse=True)
        return ordered[0:number]

    def solve(self, starting_qualification_file="Waidle Corpus (2309 20230424).txt"):
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

    def test_setup(self, plot=False):
        # Tests a game of WAIdle for each word in a corpus, to assess effectiveness of the algorithm
        # Takes a long time to perform, especially with a larger corpus: O(n**2)
        word_list = self.corpus.corpus.keys()
        results = dict()
        distribution = dict()
        counter = 0
        total = len(word_list)
        heuristic_backup = copy.copy(self.heuristic)
        for word in word_list:
            counter += 1
            b = Waidle(word, heuristic=heuristic_backup, file="Waidle Corpus (2309 20230424).txt", verbose=False)
            c = b.solve()
            if c in distribution:
                distribution[c] += 1
            else:
                distribution.update({c: 1})
            results.update({word: c})
            print(f"\nCompleted word {counter} / {total}")

        avg = sum_sq(distribution.items()) / len(self.corpus.corpus)
        print(f"Average number of guesses: {avg}")

        out_file = "results_file.csv"
        if out_file not in os.listdir():
            guess_headers = ""
            for x in range(1, 12):
                guess_headers += f"Guess {x},"
            with open(out_file, 'w') as f:
                f.write(f"Char Number,Corpus Size,Match,Exact,Average Score,{guess_headers}\n")
        with open(out_file, 'a') as f:
            f.write(f"{len(self.word)},{len(self.corpus.corpus)},{self.heuristic[0]},{self.heuristic[1]},{avg}")
            dist_numbers = sorted(list(distribution.items()))
            for i in dist_numbers:
                f.write(f",{i[1]}")
            f.write("\n")

        return results, distribution, avg


class QWaidle:
    # Starting to assemble the beones of a reinforcment learning approach to solving a game
    def __init__(self, game=Waidle(), alpha=0.5, epsilon=0.3, gamma=0.1):
        self.game = game
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.state_dict = dict()
        self.create_new_state(self.sort_state(self.game.corpus.corpus))

    @staticmethod
    def sort_state(state):
        return tuple(sorted(state.keys()))

    def create_new_state(self, new_state):
        # Produces dictionary with 1 key, the initial state, with an action for each word, with a value
        # This dictionary will be updated with each new state
        if new_state not in self.state_dict:
            di = {word: 0 for word in new_state}
            self.state_dict.update({new_state: di})

    def update(self, old_state, word, new_state, reward):
        old = self.get_q_value(old_state, word)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, word, old, reward, best_future)

    def get_q_value(self, state, word):
        if state in self.state_dict:
            return self.state_dict[state][word]
        else:
            return 0

    def best_future_reward(self, state):
        if len(state) == 0:
            return 0
        q_options = [self.get_q_value(state, word) for word in state]
        return max(q_options)

    def update_q_value(self, state, word, old_q, reward, future_rewards):
        self.state_dict[state][word] = old_q + self.alpha * (reward + future_rewards - old_q)

    def choose_action(self, state, epsilon=True):
        if state in self.state_dict:
            options = self.state_dict[state]
        else:
            self.create_new_state(state)
            options = self.state_dict[state]
        sorted(options, key=lambda item: item[1])
        if epsilon:
            random_move = random.choices((False, True), (1 - self.epsilon, self.epsilon))
            if random_move:
                return random.choice(tuple(options))
        return max(options, key=lambda item: item[1])

    def train(self, n):
        progress_increment = n / 100
        percent = 0
        corp = copy.copy(self.game.corpus)
        t0 = datetime.now()
        print("Training Started...")
        for x in range(n):
            c = 1
            state = self.sort_state(self.game.corpus.corpus)
            self.create_new_state(state)
            guess = self.choose_action(state)
            while not self.game.check_guess(guess, printout=False):
                c += 1
                old_state = state
                # print(guess, self.game.word)
                self.game.update_from_guess(self.game.guess(guess))
                state = self.sort_state(self.game.corpus.corpus)
                self.create_new_state(state)
                self.update(old_state, guess, state, 0)
                guess = self.choose_action(state)

            new_state = self.sort_state(self.game.corpus.corpus)
            self.create_new_state(new_state)
            if c <= 6:
                reward = 1
            else:
                reward = -1
            self.update(state, guess, new_state, reward)
            self.game.corpus = copy.copy(corp)
            self.game.randomize_word()
            if x % progress_increment == 0:
                percent += 1
                print(f"Training {x} / {n} - {percent}% Complete")
        td = datetime.now() - t0
        print(f"Training completed in {td}")


if __name__ == "__main__":
    main()
    a = Waidle(heuristic=(1, 2.68))
    a.corpus.qualify_corpus(heuristic=(1, 2.68), save=True)
    r, d, av = a.test_setup()

    a = Waidle(heuristic=(1, 2.69))
    a.corpus.qualify_corpus(heuristic=(1, 2.69), save=True)
    r2, d2, av2 = a.test_setup()

    # r, d = a.test_setup()

    # y = zip(*list(sorted(d.items())))

    """
    a = QWaidle()

    a.train(10000)
    print("DONE")
    b = list(sorted(a.state_dict))
    c = a.state_dict[b[1]].items()
    sorted(c, key=lambda item: item[1])
    """
