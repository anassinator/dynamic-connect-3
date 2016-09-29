# Dynamic Connect-3

This is an AI agent that plays Dynamic Connect-3 for the first assignment of
McGill Universsty's ECSE 526 - Artificial Intelligence course. Details can
be found [here](http://www.cim.mcgill.ca/~jer/courses/ai/assignments/as1.html).

## Details

This AI uses a combination of iterative-deepening minimax search with
alpha-beta pruning and reinforcement learning to try to play an optimal game.

The heuristics are kept simple in favor of increased performance and depth in
search. Since the heuristics do not always provide an accurate picture of the
"goodness" of one game situation over another, the agent also attempts to learn
from it or its opponents' mistakes at the end of a game. This is done by
backtracking through the game's moves until it finds the likely source of error
and then storing this information in a local SQLite database to avoid making it
again.

Another approach to improving the depth the agent can reach is by storing
inspected nodes and their corresponding heuristics in a transposition table.
This transposition table is also stored on disk in order to speed up subsequent
runs of the program. The values stored in this table are also updated to
reflect what the agent learns as it wins or loses.

Moreover, in order to speed up the training of the agent, the agent can play
itself for as long as the user wants. The agents keep playing and learning from
each other's mistakes until they both reach consistent stalemates. When that
occurs, the process is then repeated with additional time allocated for each
agent to pick a move. This allows for the agents to search deeper and build a
more comprehensive knowledge base.

Finally, in order to help the agent perform better in situations it hadn't
faced before, a hill climber is used in order to determine which heuristics are
worth more than others by weighing them randomly and competing them against
each other iteratively.

## Running

Simply run:

```bash
python3 connect3.py --help
```

for a list of valid commands and options.

### Player vs. player

In order to play a PvP game, simply run:

```bash
python3 connect3.py pvp [--large]
```

where `--large` allows you to play on a larger board.

### Player vs. agent

In order to play a PvE game, simply run:

```bash
python3 connect3.py pve [--large] [--black] [--max-time N]
```

where `--large` allows you to play on a larger board, `--black` lets you play
as black, and `--max-time N` sets the allocated time for the agent to think to
`N` seconds.
More advanced options can be found in `--help`.

### Agent vs. agent

In order to play a spectator game, simply run:

```bash
python3 connect3.py watch [--large] [--max-time N]
```

where `--large` allows you to play on a larger board, and `--max-time N` sets
the allocated time for the agent to think to `N` seconds.
More advanced options can be found in `--help`.

### Remote play

In order to play a remote game, simply run:

```bash
python3 connect3.py remote HOSTNAME PORT GAME_ID [--large] [--black] [--max-time N]
```

where `HOSTNAME` and `PORT` are the hostname and port of the server to connect
to, `GAME_ID` is the game ID to play under,`--large` allows you to play on a
larger board, and `--max-time N` sets the allocated time for the agent to think
to `N` seconds.
More advanced options can be found in `--help`.

The remote server is a simple TCP server that connects two agents on the same
game ID together and echoes back each other's moves.

### Training

In order to train your agents, simply run:

```bash
python3 connect3.py train [--large]
```

where `--large` allows you to play on a larger board.
More advanced options can be found in `--help`.

This will keep running forever until it is interrupted via `^C`.
