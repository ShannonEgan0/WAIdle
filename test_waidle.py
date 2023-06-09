from waidle import *
import random
from pytest import raises

a = Waidle("ORANGE")
print(len(a.corpus.corpus))


def test_check_char():
    assert check_char("A", 0, "APPLE") == 1.5
    assert check_char("A", 1, "APPLE") == 1
    assert check_char("A", 0, "APPLE", heuristic=(1, 2)) == 2
    assert check_char("A", 1, "APPLE", heuristic=(1, 2)) == 1
    assert check_char("P", 1, "APPLE", heuristic=(1, 2)) == 2
    assert check_char("P", 2, "APPLE", heuristic=(1, 2)) == 2
    assert check_char("P", 3, "APPLE", heuristic=(1, 2)) == 1
    assert check_char("Q", 1, "APPLE", heuristic=(1, 2)) == 0
    assert check_char("A", 0, "APPLE", heuristic=(1, 5)) == 5
    assert check_char("A", 1, "APPLE", heuristic=(3, 5)) == 3
    with raises(IndexError):
        check_char("A", 6, "APPLE")


def test_corpus_5():
    a = Waidle("LEAFY")
    c = a.corpus.corpus
    assert "BANANA" not in c
    assert "APPLE" in c
    assert "BGHBG" not in c


def test_corpus_6():
    a = Waidle("ORANGE")
    c = a.corpus.corpus
    assert "ORANGE" in c
    assert "BANANA" in c
    assert "APPLE" not in c
    a.corpus.prepare_corpus(chars=7)
    assert "PRETEND" in a.corpus.corpus


def test_update_corpus():
    a = Waidle("LEAFY")
    c = a.corpus.update_corpus("A", [2], [])
    assert "LEAFY" in c
    assert "SPACE" in c
    assert "TRACE" in c
    assert "APPLE" not in c
    c = a.corpus.excess_chars("P", counter=0)
    assert "LEAFY" in c
    assert "TRACE" in c
    assert "SPACE" not in c
    c = a.corpus.update_corpus("E", [], [4])
    assert "LEAFY" in c
    assert "TRACE" not in c


def test_guess_multiple_chars():
    a = Waidle("APPLE")
    a.update_from_guess(a.guess("APCBN"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("BAPCL"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("BAPPV"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("BAKLP"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("AAJKL"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("PAALE"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("ALALA"))
    assert "APPLE" in a.corpus.corpus

    a = Waidle("APPLE")
    a.update_from_guess(a.guess("POLAR"))
    assert "APPLE" in a.corpus.corpus
    a.update_from_guess(a.guess("PAPER"))
    assert "APPLE" in a.corpus.corpus

    a = Waidle("APPLE")
    a.corpus.prepare_corpus(freq_cutoff=0)
    a.update_from_guess(a.guess("NNNAN"))
    assert "ALALA" in a.corpus.corpus
    a.update_from_guess(a.guess("NANAN"))
    assert "ABACA" not in a.corpus.corpus
    assert "ALALA" not in a.corpus.corpus
    assert "APPLE" in a.corpus.corpus

    a = Waidle("DIMER")
    a.update_from_guess(a.guess("REEVE"))
    assert "DIMER" in a.corpus.corpus
