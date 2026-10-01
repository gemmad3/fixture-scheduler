import unittest
from collections import Counter

from fixture_scheduler import Fixture, round_robin


def names(n):
    return [f"T{i}" for i in range(n)]


def pair_counts(rounds):
    return Counter(frozenset((f.home, f.away)) for rnd in rounds for f in rnd)


class EvenTeamsTest(unittest.TestCase):
    def test_four_teams_exact_output(self):
        rounds = round_robin(["Alpha", "Bravo", "Charlie", "Delta"])
        got = [(f.round_no, f.home, f.away) for rnd in rounds for f in rnd]
        self.assertEqual(
            got,
            [
                (1, "Alpha", "Delta"),
                (1, "Bravo", "Charlie"),
                (2, "Charlie", "Alpha"),
                (2, "Bravo", "Delta"),
                (3, "Alpha", "Bravo"),
                (3, "Charlie", "Delta"),
            ],
        )

    def test_every_pair_meets_once(self):
        for n in (2, 4, 6, 8):
            rounds = round_robin(names(n))
            counts = pair_counts(rounds)
            self.assertEqual(len(rounds), n - 1)
            self.assertEqual(len(counts), n * (n - 1) // 2)
            self.assertEqual(set(counts.values()), {1})

    def test_everyone_plays_every_round(self):
        for rnd in round_robin(names(6)):
            players = [t for f in rnd for t in (f.home, f.away)]
            self.assertEqual(len(players), 6)
            self.assertEqual(len(set(players)), 6)


class OddTeamsTest(unittest.TestCase):
    def test_round_and_match_counts(self):
        for n in (3, 5, 7):
            rounds = round_robin(names(n))
            self.assertEqual(len(rounds), n)
            for rnd in rounds:
                self.assertEqual(len(rnd), (n - 1) // 2)

    def test_every_pair_meets_once(self):
        for n in (3, 5, 7):
            counts = pair_counts(round_robin(names(n)))
            self.assertEqual(len(counts), n * (n - 1) // 2)
            self.assertEqual(set(counts.values()), {1})

    def test_each_team_sits_out_exactly_once(self):
        n = 5
        teams = names(n)
        byes = Counter()
        for rnd in round_robin(teams):
            playing = {t for f in rnd for t in (f.home, f.away)}
            resting = set(teams) - playing
            self.assertEqual(len(resting), 1)
            byes.update(resting)
        self.assertEqual(byes, Counter({t: 1 for t in teams}))

    def test_no_team_twice_in_a_round(self):
        for rnd in round_robin(names(7)):
            players = [t for f in rnd for t in (f.home, f.away)]
            self.assertEqual(len(players), len(set(players)))

    def test_no_bye_placeholder_leaks_into_fixtures(self):
        teams = names(5)
        for rnd in round_robin(teams):
            for f in rnd:
                self.assertIn(f.home, teams)
                self.assertIn(f.away, teams)


class DoubleRoundTest(unittest.TestCase):
    def test_round_count_doubles(self):
        for n in (3, 4, 5, 6):
            single = round_robin(names(n))
            double = round_robin(names(n), double_round=True)
            self.assertEqual(len(double), 2 * len(single))

    def test_first_leg_matches_single(self):
        single = round_robin(names(6))
        double = round_robin(names(6), double_round=True)
        self.assertEqual(double[: len(single)], single)

    def test_each_ordered_pair_once(self):
        for n in (4, 5):
            rounds = round_robin(names(n), double_round=True)
            ordered = Counter((f.home, f.away) for rnd in rounds for f in rnd)
            self.assertEqual(len(ordered), n * (n - 1))
            self.assertEqual(set(ordered.values()), {1})

    def test_second_leg_reverses_sides(self):
        single = round_robin(names(5))
        double = round_robin(names(5), double_round=True)
        offset = len(single)
        for first, second in zip(single, double[offset:]):
            self.assertEqual(
                [Fixture(f.round_no + offset, f.away, f.home) for f in first],
                second,
            )

    def test_round_numbers_are_contiguous(self):
        rounds = round_robin(names(5), double_round=True)
        for i, rnd in enumerate(rounds, start=1):
            self.assertTrue(all(f.round_no == i for f in rnd))

    def test_each_team_home_and_away_equally_over_season(self):
        teams = names(6)
        rounds = round_robin(teams, double_round=True)
        home = Counter(f.home for rnd in rounds for f in rnd)
        away = Counter(f.away for rnd in rounds for f in rnd)
        for t in teams:
            self.assertEqual(home[t], len(teams) - 1)
            self.assertEqual(away[t], len(teams) - 1)


class ValidationTest(unittest.TestCase):
    def test_duplicate_names_rejected(self):
        with self.assertRaises(ValueError):
            round_robin(["A", "B", "A"])

    def test_too_few_teams_rejected(self):
        with self.assertRaises(ValueError):
            round_robin([])
        with self.assertRaises(ValueError):
            round_robin(["Solo"])

    def test_two_teams(self):
        rounds = round_robin(["A", "B"])
        self.assertEqual(rounds, [[Fixture(1, "A", "B")]])

    def test_input_not_mutated(self):
        teams = names(5)
        copy = list(teams)
        round_robin(teams)
        self.assertEqual(teams, copy)


if __name__ == "__main__":
    unittest.main()
