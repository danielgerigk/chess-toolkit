# -*- coding: utf-8 -*-

import sys
import chess
import pgn
import chess.pgn

# -----------------------------------------------------------------------------
if len(sys.argv) == 1:
    print('[Error] No command given.', file = sys.stderr)
    sys.exit(1)

command = sys.argv[1]

if not (command in ['complete']):
    print("[Error] '%s' is not a valid command." % command, file = sys.stderr)
    sys.exit(2)

if len(sys.argv) == 2:
    print('[Error] No .pgn file given.')
    sys.exit(3)

if len(sys.argv) > 3:
    print('[Error] Too many arguments given.', file = sys.stderr)
    sys.exit(4)

pgn_filename = sys.argv[2]

try:
    f = open(pgn_filename)
    pgn_text = f.read()
except:
    print("[Error] Loading of '%s' failed." % pgn_filename, file = sys.stderr)
    sys.exit(5)
finally:
    f.close()

game = pgn.loads(pgn_text)[0]
# -----------------------------------------------------------------------------
MAX_LOG_LEVEL = 2

def complete(moves, board = chess.Board(), log_level = 0):
    """Completes the a chessgame given by 'moves'; some entries in 'moves' are == '?'"""        
    if moves in ([],['1/2-1/2'],['1-0'],['0-1']):
        yield board.copy()
    elif moves[0] == '?':
        leg_moves = board.legal_moves            
        for next_move in leg_moves:
            if log_level <= MAX_LOG_LEVEL:
                print('.' * (3 * log_level) +
                      str(list(leg_moves).index(next_move) + 1) +
                      '/' + str(len(leg_moves)) +
                      ': ' + board.san(next_move), file = sys.stderr)
            board.push(next_move)
            yield from complete(moves[1:], board = board, log_level = log_level + 1)
            board.pop()
    else:
        next_move = moves[0]
        if next_move in [board.san(m) for m in board.legal_moves]:
            board.push_san(next_move)
            yield from complete(moves[1:], board = board, log_level = log_level)
            board.pop()
# -----------------------------------------------------------------------------
# Create new game and merge all completions of game.moves ...
G = chess.pgn.Game()

G.headers['Event'] = game.event
G.headers['Site'] = game.site
G.headers['Date'] = game.date
G.headers['Round'] = game.round
G.headers['White'] = game.white
G.headers['Black'] = game.black
G.headers['Result'] = game.result
G.headers['Comment'] = 'chess-toolkit complete ' + pgn_filename
    
for l in [chess.pgn.Game.from_board(board) for board in complete(game.moves)]:
    g = G.root()
    while not l.is_end():
        l = l.variation(0)        
        if not g.has_variation(l.move):
            g.add_variation(l.move)
        g = g.variation(l.move)        
      
print(G, end = "\n\n")
# -----------------------------------------------------------------------------
