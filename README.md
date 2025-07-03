# Chess Game

A simple chess game implemented in Python, using Pygame for the UI and the python-chess library for move logic and validation.

All piece assets are from Lichess cburnett set: https://github.com/lichess-org/lila/tree/master/public/piece/cburnett.

## Features

✅ Full chess rules (check, checkmate, draw)  
✅ Move history log  
✅ Flip board perspective  
✅ Undo moves  
✅ Automatic PGN export of finished games

## Controls

| Key | Action
| Mouse Click        | First click selects a piece; second click moves it to the chosen square |
| ← Left Arrow       | Undo the last move |
| ↑ / ↓ Arrows       | Navigate through the move log |
| F                  | Flip the board's point of view |
| R                  | Restart with a new game |

## Notes

- When a game ends (checkmate or draw), the game is saved in PGN format in a folder named "games". If the folder does not exist, it will be created automatically.

## Requirements

- Pygame: (https://www.pygame.org/) Used version: 2.6.1
- Python-chess (https://python-chess.readthedocs.io/) Used version: 1.11.2

Install dependencies:
pip install pygame chess
