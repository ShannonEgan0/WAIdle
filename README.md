# WAIdle

-- WORK IN PROGRESS --

AI for prioritising wordle words with manageable heuristics to solve a general wordle format game for any particular 
word as efficiently as possible. This is functions fluidly for any particular 

Algorithmically WAIdle uses a maximax model to select word choices that minimize the possible word list by the greatest 
degree by matching character positions.

Note that WAIdle will only attempt answers that could potentially be correct, rather than the alternative strategy of 
selecting guesses which will eliminate as many chars as possible to reduce possible answers. At some point, that 
strategy should be tested, as it may lower the number of guesses in the distribution, but will have less successes with 
a low number of guesses (ie, 2 or 3) which is my personally preferred goal.

By default, WAIdle will attribute a value of 1.5 to a character that is in the correct position of a possible answer, 
and a value of 1 to a character which exists in the word but is in the incorrect position. The intent is to iterate on 
this heuristic iteratively using a gradient ascent model, testing the system with different heuristics across a random
subset of the corpus (to minimize processing time) to find more optimal heuristic values.<br>
Slightly concerned with this approach, it would be a logical step, and would certainly improve performance, but will 
actively be moving away from a generalized design, as different heuristic values will be found for different initial
corpuses, eg. when different answer string lengths are selected, or when the initial starting word list is changed.

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
- Include curated Wordle word list as an initial corpus option to improve performance when answering actual wordle games
  (this reduces the corpus size from ~4200 words to ~2300)
- If Wordle word list is implemented, include the possibility of excluding previous Wordle answers
- Finish Readme including usage details
- Add additional comments to the program for clarity
- Add further tests to test file to guarantee function

### Credit
Credit goes to Josh Wardle for creating such a satisfying game principle.
