#################################################
# final.py
#
# Your name: Patrick Huang
# Your andrew id: pbhuang
#################################################

import math, copy, random

from cmu_112_graphics import *
from tkinter import *


# Game Notes: BLACK IS THE TOP HALF, RED IS THE BOTTOM HALF (FOR 2D)

# Bugs/Fixes:
    # Change all of the getLegalMoves in pieces to eliminate rows/cols
        # Basically implement piece.row and piece.col


# Checklist
    # Flip board
    # In Check (into game loop)
    # Checkmate / EndGame (into game loop)


# From https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    # You do not need to understand how this function works.
    import decimal
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


class Board(object):
    def __init__(self):
        self.x, self.y, self.z = 0,0,0
        self.cols, self.rows = 9, 10
        self.width, self.height = 400, 500
        self.cellWidth = self.width / (self.cols - 1)
        self.cellHeight = self.height / (self.rows - 1)
        self.boardPieces = [[None] * self.cols for row in range(self.rows)]
    def __repr__(self):
        for row in range(len(self.boardPieces)):
            print(self.boardPieces[row], end = ' ')
            print() 
    
    def printBoard(self):
        self.__repr__()


class Piece(object):
    r = 20
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.r = 20
        self.moveCount = 0
    def draw(self, canvas):
        canvas.create_oval(self.x + self.r, self.y + self.r, self.x - self.r,
                           self.y - self.r, width = 1, fill = self.color)

    def isInPalace(self, row, col):
        if (self.color == 'Red'):
            return ((3 <= col <= 5) and (7 <= row <= 9))
        elif (self.color == 'Black'):
            return ((3 <= col <= 5) and (0 <= row <= 2))
    
    def __hash__(self, other):
        return ((isinstance(other, self)) and 
               (self.x == other.x) and
               (self.y == other.y) and 
               (self.color == other.color))

    def getLegalMoves(self, board, row, col):
        raise NotImplementedError

    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        raise NotImplementedError 

class King(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '將', fill = 'white')
    def __repr__(self):
        return 'King'

    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result
    
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):        
        legalMoves = []
        if( (self.isInPalace(row + drow, col + dcol)) and
            ((board.boardPieces[row+drow][col+dcol] == None) or 
             (board.boardPieces[row+drow][col+dcol].color != self.color))):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
        return legalMoves


class Guard(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '士', fill = 'white')
    def __repr__(self):
        return 'Guard'
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, +1]:
            for dcol in [-1, +1]:
                result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):        
        legalMoves = []
        if( (self.isInPalace(row + drow, col + dcol)) and
            ((board.boardPieces[row+drow][col+dcol] == None) or 
             (board.boardPieces[row+drow][col+dcol].color != self.color))):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
        return legalMoves


class Minister(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '象', fill = 'white')
    def __repr__(self):
        return 'Minister'

    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, +1]:
            for dcol in [-1, +1]:
                result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        if( (0 <= row+2*drow < board.rows) and 
            (0 <= col+2*dcol < board.cols) and 
            ((board.boardPieces[row + 2*drow][col + 2*dcol] == None) or 
             (board.boardPieces[row + 2*drow][col + 2*dcol].color != self.color))):        
            legalMoves.append((row + 2*drow, col + 2*dcol))
            row += 2*drow
            col += 2*dcol
        return legalMoves
        
        
class Rook(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '車', fill = 'white')
    def __repr__(self):
        return 'Rook'

    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        while(  (0 <= row + drow < board.rows) and 
                (0 <= col + dcol < board.cols)):
            if( (board.boardPieces[row+drow][col+dcol] == None) or 
                (board.boardPieces[row+drow][col+dcol].color != self.color)):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
            else: break
        return legalMoves

class Knight(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '馬', fill = 'white')
    def __repr__(self):
        return 'Knight'

    def pieceIsInWay(self, board, row, col, drow, dcol):
        if(abs(drow) == 2):
            drow = -1 if (drow < 0) else +1
            dcol = 0
        elif(abs(dcol) == 2):
            dcol =  -1 if (dcol < 0) else +1
            drow = 0
        print('drow', drow, dcol)
        return (board.boardPieces[row + drow][col + dcol] != None)
                       
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-2, -1, +1, +2]:
            for dcol in [-2, -1, +1, +2]:
                if(abs(abs(drow) - abs(dcol)) == 1):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        if( (0 <= row+drow < board.rows) and 
            (0 <= col+dcol < board.cols) and 
            (not self.pieceIsInWay(board, row, col, drow, dcol)) and
            ((board.boardPieces[row + drow][col + dcol] == None) or 
             (board.boardPieces[row + drow][col + dcol].color != self.color))):        
            legalMoves.append((row + drow, col + dcol))
            row += drow
            col += dcol
        return legalMoves

class Cannon(Piece):
    def move(self):
        pass
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '炮', fill = 'white')
    def __repr__(self):
        return 'Cannon'

    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        attacking = False
        while((0 <= row + drow < board.rows) and (0 <= col + dcol < board.cols)):
            if((not attacking) and (board.boardPieces[row+drow][col+dcol] != None)):
                attacking = True
                row += drow
                col += dcol
            elif(attacking):
                if( (board.boardPieces[row+drow][col+dcol] != None) and 
                    (board.boardPieces[row+drow][col+dcol].color != self.color)):
                    legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol   
            elif(board.boardPieces[row+drow][col+dcol] == None):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
            else: break
        return legalMoves


class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.hasCrossedRiver = False
    
    def checkCrossedRiver(self):
        self.hasCrossedRiver = True if(self.moveCount >= 2) else False
        
        
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_text(self.x, self.y, text = '兵', fill = 'white')
    def __repr__(self):
        return 'Pawn'
    
    def getLegalMoves(self, board, row, col):
        self.checkCrossedRiver()
        
        result = []
        horizontalMoves = [-1, 0, +1] if (self.hasCrossedRiver) else [0]
        verticalMoves = [-1, 0] if (self.color == 'Red') else [+1, 0]

        for drow in verticalMoves:
            for dcol in horizontalMoves:
                if(((drow != 0) and (dcol == 0 )) or 
                    (dcol != 0) and (drow == 0)):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result
    
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):        
        legalMoves = []
        if(  (board.boardPieces[row+drow][col+dcol] == None) or 
             (board.boardPieces[row+drow][col+dcol].color != self.color)):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
        return legalMoves


def runGame():
    class MyModalApp(ModalApp):
        def appStarted(app):
            app.gameMode = GameMode()
            app.setActiveMode(app.gameMode)
            Controller.initGame()
        

    class GameMode(Mode):
        def appStarted(mode):
            pass
            
        # Two Options
            # Selecting a piece
            # Moving a piece
                # Replacing a piece
                # Simply moving it
        
        def mousePressed(mode, event):
            
            if(Controller.isNearPiece(event.x, event.y)):
                (row,col) = Controller.getIntersection(Model.gameBoard, event.x, event.y)
                (oldRow, oldCol) = Model.selectedPosition
        
                if((Model.selectedPiece == None) and (Model.gameBoard.boardPieces[row][col] != None)):
                    Model.selectedPiece = Controller.selectPiece(Model.gameBoard, row, col)
                    legalMoves = Model.selectedPiece.getLegalMoves(Model.gameBoard, row, col)
        
                elif(Model.selectedPiece != None):
                    if(Model.selectedPiece == Model.gameBoard.boardPieces[row][col]):
                        Model.selectedPiece = None
                        Model.selectedPosition = (-1,-1)
            
                    elif((Model.selectedPiece != Model.gameBoard.boardPieces[row][col]) and 
                        ((row, col) in Model.selectedPiece.getLegalMoves(Model.gameBoard, oldRow, oldCol))):
                        
                        Controller.placePiece(Model.gameBoard, oldRow, oldCol, row, col)
                        Model.selectedPiece.moveCount += 1
                        Model.selectedPiece = None
                        Model.selectedPosition = (-1,-1)

        def keyPressed(mode, event):
            if(event.key == 'k'):
                Model.gameBoard.printBoard()
            elif(event.key == 'f'):
                Controller.flipBoard(Model.gameBoard)

        def redrawAll(mode, canvas):
            View.drawBoard(canvas, Model.gameBoard)
            View.drawPieces(canvas)
    
    
    class View(object):
        
        @staticmethod
        def drawBoardGrid(canvas, board):
            #Subtract one because we are using lines, not spaces as rows/cols
            for row in range(board.rows - 1):
                for col in range(board.cols - 1):
                    (x0,y0,x1,y1) = Controller.getCellDimensions(board, row, col)
                    canvas.create_rectangle(x0,y0,x1,y1,fill = 'white', 
                                            width = '1')
        @staticmethod
        def drawBoardMiddle(canvas, board):
            # 0 represents the leftmost column
            (x0,y0,x1,y1) = Controller.getCellDimensions(board, Model.middleRow, 0)
            # Reassign x-coords so middle streches across entire board
            x0, x1 = Model.margin, Model.width - Model.margin
            canvas.create_rectangle(x0, y0, x1, y1, fill = 'white', width = '1')
        @staticmethod
        def drawIndivPalace(canvas, x0, y0, x1, y1):
            canvas.create_line(x0, y0, x1, y1)
            canvas.create_line(x0, y1, x1, y0)
        
        @staticmethod
        # Replace magic numbers
        def drawBoardPalace(canvas, board):
            leftPalaceColumn = 3
            topBottomPalaceRow = board.rows - 3
            (x0,y0,x1,y1) = Controller.getCellDimensions(board, 0, leftPalaceColumn)
            x1 += board.cellWidth
            y1 += board.cellHeight
            View.drawIndivPalace(canvas, x0, y0, x1, y1)

            (x0,y0,x1,y1) = Controller.getCellDimensions(board, topBottomPalaceRow, leftPalaceColumn)
            x1 += board.cellWidth
            y1 += board.cellHeight
            View.drawIndivPalace(canvas, x0, y0, x1, y1)

        @staticmethod
        def drawBoard(canvas, board):
            View.drawBoardGrid(canvas, board)
            View.drawBoardMiddle(canvas, board)
            View.drawBoardPalace(canvas, board)

        @staticmethod
        def drawPieces(canvas):
            for key in Model.pieces:
                for piece in Model.pieces[key]:
                    piece.draw(canvas)

    class Model(object):    
        gameBoard = Board()
        margin = 50
        middleRow = gameBoard.rows // 2 - 1
        middleCol = gameBoard.cols // 2 
        pieces = dict()
        pieces['Red'] = []
        pieces['Black'] = []
        width = 500
        height = 600
        selectedPiece = None
        selectedPosition = (-1,-1)

    class Controller(object):

        @staticmethod
        def initGame():
            Controller.createPieces()
            Controller.putPiecesInBoard(Model.gameBoard)
            Model.gameBoard.printBoard()

        @staticmethod
        def createPawns(board):
            numPawns = 5
            for i in range(numPawns):
                bx, by = Controller.getIntersectionCoords(board, 3, 2*i)
                rx, ry = Controller.getIntersectionCoords(board, 6, 2*i)
                Model.pieces['Black'].append(Pawn(bx, by, 'Black'))
                Model.pieces['Red'].append(Pawn(rx, ry, 'Red'))
        
        @staticmethod
        def createDoubles(board, pieceType):
            numPieces = 2
            for i in range(numPieces):
                if(pieceType == 'Rook'): 
                    (spacing, initialCol) = (8, 0)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Rook(bx, by, 'Black'))
                    Model.pieces['Red'].append(Rook(rx, ry, 'Red'))
                elif(pieceType == 'Knight'):
                    (spacing, initialCol) = (6, 1)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Knight(bx, by, 'Black'))
                    Model.pieces['Red'].append(Knight(rx, ry, 'Red'))
                elif(pieceType == 'Cannon'):
                    (spacing, initialCol) = (6, 1)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Cannon(bx, by, 'Black'))
                    Model.pieces['Red'].append(Cannon(rx, ry, 'Red'))
                elif(pieceType == 'Minister'): 
                    (spacing, initialCol) = (4, 2)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Minister(bx, by, 'Black'))
                    Model.pieces['Red'].append(Minister(rx, ry, 'Red'))
                elif(pieceType == 'Guard'): 
                    (spacing, initialCol) = (2, 3)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Guard(bx, by, 'Black'))
                    Model.pieces['Red'].append(Guard(rx, ry, 'Red'))

        @staticmethod        
        def getBxByRxRyHelper(board, pieceType, spacing, initialCol, i):
            if(pieceType == 'Cannon'):
                bx,by = Controller.getIntersectionCoords(board, 2, initialCol + i*spacing)
                rx,ry = Controller.getIntersectionCoords(board, Model.gameBoard.rows-3,
                        initialCol + i*spacing)
            else:
                bx,by = Controller.getIntersectionCoords(board, 0, initialCol + i*spacing)
                rx,ry = Controller.getIntersectionCoords(board, Model.gameBoard.rows-1,
                        initialCol + i*spacing)
            return (bx,by,rx,ry)

        @staticmethod
        def createKings(board):
            bx, by = Controller.getIntersectionCoords(board, 0, Model.middleCol)
            rx, ry = Controller.getIntersectionCoords(board, Model.gameBoard.rows-1, Model.middleCol)
            Model.pieces['Black'].append(King(bx, by, 'Black'))
            Model.pieces['Red'].append(King(rx, ry, 'Red'))

        @staticmethod
        def createPieces():
            Controller.createPawns(Model.gameBoard)
            Controller.createDoubles(Model.gameBoard, 'Rook')
            Controller.createDoubles(Model.gameBoard, 'Cannon')
            Controller.createDoubles(Model.gameBoard, 'Knight')
            Controller.createDoubles(Model.gameBoard, 'Minister')
            Controller.createDoubles(Model.gameBoard, 'Guard')
            Controller.createKings(Model.gameBoard)
 
        @staticmethod
        def getCellDimensions(board, row, col):
            
            x0 = Model.margin + col*(board.cellWidth)
            y0 = Model.margin + row*(board.cellHeight)
            x1 = Model.margin + (col+1)*(board.cellWidth)
            y1 = Model.margin + (row+1)*(board.cellHeight)

            return (x0,y0,x1,y1)
        
        @staticmethod
        def getIntersectionCoords(board, row, col):
            x = Model.margin + col*(board.cellWidth)
            y = Model.margin + row*(board.cellHeight)
            return (x, y)
        
        @staticmethod
        def isNearPiece(x, y):
            return ((Model.margin - Piece.r <= x <= Model.width - Model.margin + Piece.r) and
                    (Model.margin - Piece.r <= y <= Model.height - Model.margin + Piece.r))

        @staticmethod
        def getIntersection(board, x, y):
            row = roundHalfUp((y - Model.margin) / board.cellHeight)
            col = roundHalfUp((x - Model.margin) / board.cellWidth)
            return (row,col)

        @staticmethod
        def putPiecesInBoard(board):
            for color in Model.pieces:
                for piece in Model.pieces[color]:
                    (row,col) = Controller.getIntersection(board, piece.x, piece.y)
                    board.boardPieces[row][col] = piece
        @staticmethod
        def selectPiece(board, row, col):
            if(board.boardPieces[row][col] != None):
                Model.selectedPosition = (row, col)
                return board.boardPieces[row][col]
        
        @staticmethod
        def replacePiece(board, row, col):
            color = Model.gameBoard.boardPieces[row][col].color
            index = Model.pieces[color].index(Model.gameBoard.boardPieces[row][col])
            removedPiece = Model.pieces[color].pop(index)
            print('Removed Piece: ', removedPiece)

        @staticmethod
        def placePiece(board, oldRow, oldCol, row, col):
            (newX, newY) = Controller.getIntersectionCoords(Model.gameBoard, row, col)
             
            if(Model.gameBoard.boardPieces[row][col] != None):
                Controller.replacePiece(board, row, col)

            (Model.selectedPiece.x, Model.selectedPiece.y) = (newX, newY)
            Model.gameBoard.boardPieces[oldRow][oldCol] = None
            Model.gameBoard.boardPieces[row][col] = Model.selectedPiece        
            

        @staticmethod 
        def flipBoard(board):
            newBoard = board
            rows = len(board.boardPieces)
            cols = len(board.boardPieces[0])
            pivotCol = cols // 2
            pivotRow = (rows - 1) / 2

            print(pivotCol, pivotRow)

            for row in range(len(board.boardPieces)):
                for col in range(len(board.boardPieces[0])):
                    flipRowIndex = int(pivotRow - (row - pivotRow))
                    flipColIndex = int(pivotCol - (col - pivotCol))
                    newBoard.boardPieces[row][col] = board.boardPieces[flipRowIndex][flipColIndex]
                    (newX, newY) = Controller.getIntersectionCoords(newBoard, row, col)
                    if(newBoard.boardPieces[row][col] != None):
                        newBoard.boardPieces[row][col].x = newX
                        newBoard.boardPieces[row][col].y = newY
                
            board = newBoard

        @staticmethod
        def updatePieceCoords(piece, row, col):
            (x,y) = Controller.getIntersectionCoords(row, col)
            (piece.x, piece.y) = (x,y)

        @staticmethod
        def isInCheck(board, kingPiece):
            (kingRow, kingCol) = Controller.getIntersection(Model.gameBoard, kingPiece.x, kingPiece.y)
            if kingPiece.color == 'Red':
                for piece in Model.pieces['Black']:
                    (row, col) = Controller.getIntersection(Model.gameBoard, piece.x, piece.y)
                    if((kingRow, kingCol) in piece.getLegalMoves(Model.gameBoard, row, col)):
                        return True
                return False
            else:
                for piece in Model.pieces['Red']:
                    (row, col) = Controller.getIntersection(Model.gameBoard, piece.x, piece.y)
                    if((kingRow, kingCol) in piece.getLegalMoves(Model.gameBoard, row, col)):
                        return True
                return False

        '''
        @staticmethod
        def getLocation(row, col, board):
            if(not isInBoard(app, x, y)):
                return(-1, -1)
            
            
            return row, col        
        
        
        @staticmethod
        def getBounds(obj):
            x0 = obj.x - obj.width / 2 
            y0 = obj.y - obj.height / 2
            x1 = obj.x + obj.width / 2
            y1 = obj.y + obj.height / 2
            return (x0, y0, x1, y1)

        @staticmethod
        def selectObstacle(x, y):
            for obj in mode.obstacles:
                (x0, y0, x1, y1) = mode.getBounds(obj)
                if((x0 <= x <= x1) and (y0 <= y <= y1)):
                    obj.isDragged = True
                    mode.selectedObstacle = obj
                    mode.obstacleSelected = True
        '''
    app = MyModalApp(width=500, height=600)

def testGame():
    print('Testing Game...')
    runGame()

testGame()