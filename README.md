# fixture-scheduler

A small Python library for generating round-robin sports fixtures: the
kind of schedule where every team in a league plays every other team
once, or twice for a home-and-away season.

Working this out by hand gets tedious past a handful of teams, and
it's easy to get wrong — a team playing itself, a pairing repeated in
the same round, nobody accounting for who sits out when the team count
is odd. This library uses the standard "circle method" for round-robin
scheduling: one team is held fixed and the rest rotate through the
pairing table each round. Byes are handled automatically for odd team
counts, and home/away sides are flipped each round so nobody ends up
playing every match at home or away.

Standard library only, no dependencies.

## Usage

```python
from fixture_scheduler import round_robin

teams = ["Alpha", "Bravo", "Charlie", "Delta"]
rounds = round_robin(teams)

for round_matches in rounds:
    for fixture in round_matches:
        print(f"Round {fixture.round_no}: {fixture.home} vs {fixture.away}")
```

Four teams produces three rounds, with everyone playing everyone else
exactly once:

```
Round 1: Alpha vs Delta
Round 1: Bravo vs Charlie
Round 2: Charlie vs Alpha
Round 2: Bravo vs Delta
Round 3: Alpha vs Bravo
Round 3: Charlie vs Delta
```

An odd number of teams works the same way, with one team resting each
round:

```python
rounds = round_robin(["Alpha", "Bravo", "Charlie"])
# 3 rounds, 1 match per round, one team sitting out each time
```

For a home-and-away season, pass `double_round=True` to get a second
leg with sides reversed:

```python
rounds = round_robin(teams, double_round=True)
```

## Tests

```
python -m unittest discover tests
```

## Status

The core scheduler works. See the roadmap in the project notes for
what's planned next — things like avoiding back-to-back home games and
exporting a schedule to a calendar file aren't done yet.
