"""Round-robin fixture generation using the circle method.

Given a list of team names, produce a schedule where every team plays
every other team once (or twice, for a double round-robin), with
home/away assignments alternated across rounds and correct handling of
an odd number of teams (one team gets a bye each round).
"""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Fixture:
    round_no: int
    home: str
    away: str


def round_robin(teams: Sequence[str], double_round: bool = False) -> list[list[Fixture]]:
    """Return a list of rounds, each a list of Fixture objects.

    Uses the circle method: one team stays fixed in the pairing table
    and the rest rotate by one position each round. An odd number of
    teams gets a placeholder bye slot; any pairing that lands on it is
    simply dropped, which is what makes that team sit out the round.
    """
    names = list(dict.fromkeys(teams))
    if len(names) != len(teams):
        raise ValueError("duplicate team names")
    if len(names) < 2:
        raise ValueError("need at least two teams")

    bye = object() if len(names) % 2 else None
    slots = names + [bye] if bye is not None else list(names)
    n = len(slots)

    fixed, rotating = slots[0], slots[1:]
    rounds: list[list[Fixture]] = []

    for round_no in range(n - 1):
        pairing = [fixed] + rotating
        matches = []
        for i in range(n // 2):
            a, b = pairing[i], pairing[n - 1 - i]
            if a is bye or b is bye:
                continue
            # flip which side is "home" every other round so it evens out
            home, away = (a, b) if round_no % 2 == 0 else (b, a)
            matches.append(Fixture(round_no + 1, home, away))
        rounds.append(matches)
        rotating = rotating[-1:] + rotating[:-1]

    if double_round:
        offset = len(rounds)
        second_leg = [
            [Fixture(f.round_no + offset, f.away, f.home) for f in rnd]
            for rnd in rounds
        ]
        rounds += second_leg

    return rounds
