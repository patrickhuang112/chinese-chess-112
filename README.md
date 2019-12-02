# chinese-chess-112
# Created by: Patrick Huang
# Andrew ID: pbhuang
# Fall-2019, 15-112 Final Term Project

Final Term Project for: https://www.cs.cmu.edu/~112/

External Modules used: Panda3D: https://www.panda3d.org/

External Software used: Adobe After Effects, Blender 2.70, Blender YABEE Exporter

External Code used:
	-Used code from Panda3D Chessboard demo: code relating to 3D clicking and selecting (creating collision rays and traversers)
	-Used code from 112 course (roundHalfUp)

Notes:
	-When first playing the game, it will take a second or so after clicking/selecting a piece for the color to change. This is because the model needs to be loaded for the first time into the game.

	-Use the arrow keys (left, right) to rotate the board horizontally and (up, down) to rotate the board vertically
	-Used WASD keys to move the position of the camera (the movement will always be relative to how much you have rotated the board)
	-Use "j" to zoom in closer to the board and use "k" to zoom out from the board
	
	-When in the instructions screen, click left and right arrow to switch between slides. 
	-Click "esc" anytime to go back to the main menu (whether in instructions or in game)

	-Lime Green indicates what piece is currently selected
	-Dark Blue circles indicate "legal" moves for a selected piece
	-Orange circles indicate a legal move that involves taking an enemy piece
	-Pink-Purple circles indicate a king piece is in check

Game Rules:
	-Chinese Chess (xianqi) is quite like Western chess, where the objective is to put the opponent's king in checkmate or stalemate (no legal moves). 
	-Pieces:
		-King: Moves and attacks horizontally and vertically one space at a time. Cannot leave the "X" palace area of the board
		-Guards: Moves and attacks diagonally one space. Cannot leave the "X" palace area of the board
		-Ministers: Moves and attacks diagonally in a two space leap. Cannot "cross the river" to the other side of the board
		-Knights: Moves L-shape attack (two steps forward, one to left or right), just like Western chess knight. Key difference is if a piece is directly in front of the move two spaces direction, the knight cannot move in that direction.
		-Rooks: Moves and attacks horizontally and vertically unlimited number of spaces. Identical to Western chess rook
		-Cannons: Moves horizontally and vertically, just like a rook. Can only attack by "jumping" over a piece (friendly or enemy) and attacking a piece on the other side of the "jumped" piece.
		-Pawns: Initially, can only move and attack in forward direction. Once it has crossed the river, it can move and attack horizontally.
	-Special Rules:
		-Kings Facing: The two kings can never "see" each other. They cannot be in the same column without a piece in between
		-Red goes first

All code and project files on: https://github.com/patrickhuang112/chinese-chess-112
Have fun playing!	