from waidle import *
import random
from pytest import raises

a = Waidle("ORANGE")
print(len(a.corpus.corpus))


def test_check_char():
    assert check_char("A", 0, "APPLE") == 2
    assert check_char("A", 1, "APPLE") == 1
    assert check_char("P", 1, "APPLE") == 2
    assert check_char("P", 2, "APPLE") == 2
    assert check_char("P", 3, "APPLE") == 1
    assert check_char("Q", 1, "APPLE") == 0
    assert check_char("A", 0, "APPLE", heuristic=(1, 5)) == 5
    assert check_char("A", 1, "APPLE", heuristic=(3, 5)) == 3
    with raises(IndexError):
        check_char("A", 6, "APPLE")


def test_corpus_5():
    a = Waidle("LEAFY")
    c = a.corpus.corpus
    assert len(c) == 9972
    assert "BANANA" not in c
    assert "APPLE" in c
    assert "BGHBG" not in c


def test_corpus_6():
    a = Waidle("ORANGE")
    c = a.corpus.corpus
    assert len(c) == 17464
    assert "ORANGE" in c
    assert "BANANA" in c
    assert "APPLE" not in c
    a.corpus.prepare_corpus(chars=7)
    assert len(a.corpus.corpus) == 23714
    assert "PRETEND" in a.corpus.corpus


def test_update_corpus():
    a = Waidle("LEAFY")
    c = a.corpus.update_corpus("A", [2], [])
    assert "LEAFY" in c
    assert "SPACE" in c
    assert "TRACE" in c
    assert "APPLE" not in c
    c = a.corpus.remove_char_from_corpus("P")
    assert "LEAFY" in c
    assert "TRACE" in c
    assert "SPACE" not in c
    c = a.corpus.update_corpus("E", [], [4])
    assert "LEAFY" in c
    assert "TRACE" not in c


def test_guess_multiple_chars():
    a = Waidle("APPLE")
    a.guess("APCBN")
    assert "APPLE" in a.corpus.corpus
    a.guess("BAPCL")
    assert "APPLE" in a.corpus.corpus
    a.guess("BAPPV")
    assert "APPLE" in a.corpus.corpus
    a.guess("BAKLP")
    assert "APPLE" in a.corpus.corpus
    a.guess("AAJKL")
    assert "APPLE" in a.corpus.corpus
    a.guess("PAALE")
    assert "APPLE" in a.corpus.corpus
    a.guess("ALALA")
    assert "APPLE" in a.corpus.corpus

    a = Waidle("APPLE")
    a.guess("POLAR")
    assert "APPLE" in a.corpus.corpus
    a.guess("PAPER")
    assert "APPLE" in a.corpus.corpus

    a = Waidle("APPLE")
    a.corpus.prepare_corpus(freq_cutoff=0)
    a.guess("NNNAN")
    assert "ALALA" in a.corpus.corpus
    a.guess("NANAN")
    assert "ABACA" not in a.corpus.corpus
    assert "ALALA" not in a.corpus.corpus
    assert "APPLE" in a.corpus.corpus
