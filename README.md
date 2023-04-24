# WAIdle

-- WORK IN PROGRESS --

#### External Libraries required:    
    requests
    nltk
    matplotlib

AI for prioritising wordle words with manageable heuristics to solve a general wordle format game for any particular 
word as efficiently as possible.

Algorithmically WAIdle uses a maximax model to select word choices that minimize the possible word list to the greatest 
degree by matching character positions.

Note that WAIdle will only attempt answers that could potentially be correct, rather than the alternative strategy of 
selecting guesses which will eliminate as many chars as possible to reduce possible answers. At some point, that 
strategy should be tested, as it may lower the number of guesses in the distribution, but will have fewer successes with 
a low number of guesses (ie, 2 or 3) which is my personally preferred goal.

By default, WAIdle will attribute a value of 1.5 to a character that is in the correct position of a possible answer, 
and a value of 1 to a character which exists in the word but is in the incorrect position. An iterative gradient ascent 
model can be used to test the system with different heuristics to find more optimal heuristic ratios.

For the oiginal Wordle corpus of 2309 words, the following distribution can be found for heuristics of 1.5 and 3:
<img src="Original Wordle Heuristic Results.png">
In this case, it was found that increasing the ratio of 2.7 and above reduced the number of average guesses for 
words in the corpus to 3.46 from 3.48. In exchange, this loses out on some impressively low guesses of 2 and 3.
The effect the ratio has on the number of guesses taken is quite small, since the corpus size is low, impact is minimal.
At very low ratio values, the average number of guesses is increased by a non insignificant amount.

Note that different heuristic ratios will be found for different initial corpuses, e.g. when different answer 
string lengths are selected, or when the initial starting word list is changed.

A reinforcement learning algorithm will be implemented as a comparison to the maximax approach, to see if it can gain 
additional insights, and I think it will provide an educational example of the difference between these styles of 
techniques.

Credit to https://github.com/hackerb9/gwordlist for the currently used word list. The list is filtered according to 
frequency of usage in Google Ngrams. An alternative would be to use the specific Wordle word list, which is heavily 
curated, and this option should be included.

## Usage

waidle.**Waidle**(word=None, heuristic=(1, 1.5), chars=5)
    
    Return a Waidle object with answer == word. If word is left None, a random word with len == chars 
    will be selected from the corpus of possible answers. Index 0 of heuristic defines the value of a
    char that is in the incorrect position, but occurs in the answer, and index 1 defines the value
    of a char that is in the correct position.
    Waidle object is initialized with a WaidleCorpus object as self.corpus.

waidle.**WaidleCorpus**()
    
    Return a Waidle corpus object, which can be used to load in a corpus for usage with WAIdle, and
    progressive qualification/filtering as possible answers are eliminated from the program.

### To do:
- Implement alternate method of AI with a reinforcement learning technique
- Implement heuristic optimization through gradient ascent and iteration
- Source the daily wordle answer from an API to allow the program to solve the current answer without being manually 
referred to
- Include the possibility of excluding previous Wordle answers
- Finish Readme including usage details
- Add additional comments to the program for clarity
- Add further tests to test file to guarantee function

### Credit
Credit goes to Josh Wardle for creating such a satisfying game principle.
