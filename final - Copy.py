#################################################
# final.py
#
# Your name: Patrick Huang
# Your andrew id: pbhuang
#################################################

import math, copy, random
from direct.task.Task import Task
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode, Mat4
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.actor.Actor import Actor


# From https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
from cmu_112_graphics import *
from tkinter import *


# Game Notes: BLACK IS THE TOP HALF, RED IS THE BOTTOM HALF (FOR 2D)

# Elan: suggested camera rotation for each term over.

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
        self.pieces = [[None] * self.cols for row in range(self.rows)]
    def __repr__(self):
        for row in range(len(self.pieces)):
            print(self.pieces[row], end = ' ')
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
    
    def __eq__(self, other):
        return ((isinstance(other, type(self))) and 
               (self.x == other.x) and
               (self.y == other.y) and 
               (self.color == other.color))
               
    def getHashables(self):
        return (self.x, self.y, self.color)
    
    def __hash__(self):
        return hash(self.getHashables())
    
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
            ((board.pieces[row+drow][col+dcol] == None) or 
             (board.pieces[row+drow][col+dcol].color != self.color))):        
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
            ((board.pieces[row+drow][col+dcol] == None) or 
             (board.pieces[row+drow][col+dcol].color != self.color))):        
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
        rowLimit = 5
        if(self.color == 'Red'):
            # If piece is red, must stay within rows 5 to 9
            if( (rowLimit <= row+2*drow < board.rows) and 
                (0 <= col+2*dcol < board.cols) and 
                ((board.pieces[row + 2*drow][col + 2*dcol] == None) or 
                (board.pieces[row + 2*drow][col + 2*dcol].color != self.color))):        
                legalMoves.append((row + 2*drow, col + 2*dcol))
                row += 2*drow
                col += 2*dcol
            return legalMoves
        else:
            # If piece is black, must stay within rows 0 to 4
            if( (0 <= row+2*drow < rowLimit) and 
                (0 <= col+2*dcol < board.cols) and 
                ((board.pieces[row + 2*drow][col + 2*dcol] == None) or 
                (board.pieces[row + 2*drow][col + 2*dcol].color != self.color))):        
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
            if( (board.pieces[row+drow][col+dcol] == None) or 
                (board.pieces[row+drow][col+dcol].color != self.color)):        
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
        return (board.pieces[row + drow][col + dcol] != None)
                       
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
            ((board.pieces[row + drow][col + dcol] == None) or 
             (board.pieces[row + drow][col + dcol].color != self.color))):        
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
            if((not attacking) and (board.pieces[row+drow][col+dcol] != None)):
                attacking = True
                row += drow
                col += dcol
            elif(attacking):
                if( (board.pieces[row+drow][col+dcol] != None) and 
                    (board.pieces[row+drow][col+dcol].color != self.color)):
                    legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol   
            elif(board.pieces[row+drow][col+dcol] == None):        
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
        if( (0 <= row+drow < board.rows) and 
            (0 <= col+dcol < board.cols) and  
    
            ((board.pieces[row+drow][col+dcol] == None) or 
             (board.pieces[row+drow][col+dcol].color != self.color))):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
        return legalMoves

# From Panda3D Chessboard demo
def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())
 

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)



        self.dlight = DirectionalLight('my dlight')
        self.dlnp = render.attachNewNode(self.dlight)
        self.dlnp.setHpr(0, -90, 0)

        render.setLight(self.dlnp)

        self.boardLines = self.loader.loadModel("models/boardLines")
        self.boardBody = self.loader.loadModel("models/boardBody")
        self.boardBase = self.loader.loadModel("models/boardBase")
        self.king = self.loader.loadModel("models/cannon")
        self.scene = self.loader.loadModel("models/environment")
        
        # Any model must be parented to the self.render 'tree' to render
        # Reparent the model to render.
        self.boardLines.reparentTo(self.render)
        self.boardBody.reparentTo(self.render)
        self.boardBase.reparentTo(self.render)
        self.king.reparentTo(self.render)
        # self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        # self.test.setScale(1, 1, 1)
        
        self.scene.setScale(0.1, 0.1, 0.1)
        self.scene.setPos(-8, 42, 0)

        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        
        self.boardLines.setScale(100, 100, 100)
        self.boardBody.setScale(100, 100, 100)
        self.boardBase.setScale(100, 100, 100)
        self.king.setPos(0, 0 ,5)
        self.king.setScale(10, -10, 10)
    
        self.pandaActor.setScale(0.05, 0.05, 0.05)
        # self.pandaActor.reparentTo(self.render)




        self.picker = CollisionTraverser()  
        self.pq = CollisionHandlerQueue()  
        
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)

        # Add the spinCameraTask procedure to the task manager.
        # This is called every few seconds
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")




        # self.acceptOnce('a', self.spinCamera)
        self.accept('mouse1',self.keyHandler, ['mouse1'])
        self.accept('arrow_left', self.keyHandler, ['arrow_left'])
        self.accept('arrow_right', self.keyHandler, ['arrow_right'])
        self.accept('arrow_up', self.keyHandler, ['arrow_up'])
        self.accept('arrow_down', self.keyHandler, ['arrow_down'])
        self.accept('k', self.keyHandler, ['k'])
        self.accept('j', self.keyHandler, ['j'])
        
    
    # From Panda3D chessboard demo
    def getPosition(self, mousepos):
        self.pickerRay.setFromLens(base.camNode, mousepos.getX(),mousepos.getY()) 
        self.picker.traverse(render) 
        if self.queue.getNumEntries() > 0: 
            self.queue.sortEntries() 
            self.position = self.queue.getEntry(0).getSurfacePoint(self.environ) 
            return None
    
      # get the mouse position
    
    def mousePressed(self):
        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.mouseWatcherNode.getMouse()

            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            # If we are dragging something, set the position of the object
            # to be at the appropriate point over the plane of the board
            # Gets the point described by pickerRay.getOrigin(), which is relative to
            # camera, instead of to render
            nearPoint = render.getRelativePoint(camera, self.pickerRay.getOrigin())
            # Same thing with the direction of the ray
            nearVec = render.getRelativeVector(camera, self.pickerRay.getDirection())
            self.king.setPos(PointAtZ(.5, nearPoint, nearVec))
            (x,y,z) = self.king.getPos()
            print(x, y, z)
            self.king.setPos(x, y, z + 3)
    

    def keyHandler(self,key):
        if(key == "arrow_left"):
            pass
        elif(key == "arrow_right"):
            pass
        elif(key == "arrow_up"):
            pass
        elif(key == "arrow_down"):
            pass
        elif(key == "k"):
            self.disableMouse()
        elif(key == 'j'):
            mat=Mat4(camera.getMat())
            mat.invertInPlace()
            base.mouseInterfaceNode.setMat(mat)
            base.enableMouse()
        elif(key == 'mouse1'):
            self.mousePressed()
        
        '''
        elif(key == 'mouse1'):
            if base.mouseWatcherNode.hasMouse():
                mpos = base.mouseWatcherNode.getMouse()  # get the mouse position
                self.pandaActor.setPos(mpos.getX(), mpos.getY(), 2)
                print(mpos)
        '''

    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        self.camera.setPos(20 * math.sin(angleRadians), -20.0 * math.cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont


app = MyApp()

#Must be last line
app.run()










# ModalApp class from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
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
            
            #Only if click in board
            if(Controller.isNearBoard(event.x, event.y)):
                (row,col) = Controller.getIntersection(Model.gameBoard, event.x, 
                                                        event.y)
                (oldRow, oldCol) = Model.selectedPosition
                
                # Select a piece if none selected
                if((Model.selectedPiece == None) and 
                   (Model.gameBoard.pieces[row][col] != None)):
                    if(Model.currentPlayer == Model.gameBoard.pieces[row][col].color):
                        Model.selectedPiece = Controller.selectPiece(Model.gameBoard, row, col)
                        legalMoves = Model.selectedPiece.getLegalMoves(Model.gameBoard, row, col)
                        refinedMoves = Controller.refineLegalMoves(Model.gameBoard, row, col, Model.selectedPiece, legalMoves)
                        print('Selected piece: ', Model.selectedPiece)
                        print('Legal Moves: ', refinedMoves)
                
                #Piece is selected already
                elif(Model.selectedPiece != None):
                    legalMoves = Model.selectedPiece.getLegalMoves(Model.gameBoard, oldRow, oldCol)
                    refinedMoves = Controller.refineLegalMoves(Model.gameBoard, oldRow, oldCol, Model.selectedPiece, legalMoves)
                    
                    # User click on selected piece, deselects it
                    if(Model.selectedPiece == Model.gameBoard.pieces[row][col]):
                        Model.selectedPiece = None
                        Model.selectedPosition = (-1,-1)
                        print('Deselected Piece!')

                    # User clicks on valid move area
                    elif((Model.selectedPiece != Model.gameBoard.pieces[row][col]) and 
                        ((row, col) in refinedMoves)):
                        success = Controller.placePiece(Model.gameBoard, oldRow, oldCol, row, col)
                        if(success):    
                            Model.selectedPiece.moveCount += 1
                            Model.selectedPiece = None
                            Model.selectedPosition = (-1,-1)
                            Controller.switchPlayer()
                            print('Moved piece!')
            
            #Check if GameOver (checkmate)
            Controller.checkGameOver(Model.gameBoard)

        def keyPressed(mode, event):
            if(event.key == 'k'):
                Model.gameBoard.printBoard()
            
            # elif(event.key == 'f'):
            #    Controller.flipBoard(Model.gameBoard)

        def redrawAll(mode, canvas):
            View.drawBoard(canvas, Model.gameBoard)
            View.drawPieces(canvas)
    
    
    class View(object):
        
        #Draws vertical and horizontal board lines
        @staticmethod
        def drawBoardGrid(canvas, board):
            #Subtract one because we are using lines, not spaces as rows/cols
            for row in range(board.rows - 1):
                for col in range(board.cols - 1):
                    (x0,y0,x1,y1) = Controller.getCellDimensions(board, row, col)
                    canvas.create_rectangle(x0,y0,x1,y1,fill = 'white', 
                                            width = '1')
        
        # Draws middle 'river'
        @staticmethod
        def drawBoardMiddle(canvas, board):
            # 0 represents the leftmost column
            (x0,y0,x1,y1) = Controller.getCellDimensions(board, Model.middleRow, 0)
            # Reassign x-coords so middle streches across entire board
            x0, x1 = Model.margin, Model.width - Model.margin
            canvas.create_rectangle(x0, y0, x1, y1, fill = 'white', width = '1')
        
        # Draws individual palace
        @staticmethod
        def drawIndivPalace(canvas, x0, y0, x1, y1):
            canvas.create_line(x0, y0, x1, y1)
            canvas.create_line(x0, y1, x1, y0)
        
        @staticmethod
        # Draws red and black palaces
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

        # Draws entire board
        @staticmethod
        def drawBoard(canvas, board):
            View.drawBoardGrid(canvas, board)
            View.drawBoardMiddle(canvas, board)
            View.drawBoardPalace(canvas, board)

        # Draws all pieces on board
        @staticmethod
        def drawPieces(canvas):
            for key in Model.pieces:
                for piece in Model.pieces[key]:
                    piece.draw(canvas)

    # Contains all game data and important variables
    class Model(object):    
        gameBoard = Board()
        margin = 50
        middleRow = gameBoard.rows // 2 - 1
        middleCol = gameBoard.cols // 2 
        pieces = dict()
        pieces['Red'] = []
        pieces['Black'] = []
        width, height = 500, 600
        selectedPiece = None
        selectedPosition = (-1,-1)
        currentPlayer = 'Red'

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
        def isNearBoard(x, y):
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
                    board.pieces[row][col] = piece
        @staticmethod
        def selectPiece(board, row, col):
            if(board.pieces[row][col] != None):
                Model.selectedPosition = (row, col)
                return board.pieces[row][col]
        
        @staticmethod
        def removeReplacedPiece(board, row, col):
            color = Model.gameBoard.pieces[row][col].color
            index = Model.pieces[color].index(Model.gameBoard.pieces[row][col])
            removedPiece = Model.pieces[color].pop(index)
            print('Removed Piece: ', removedPiece)
            return removedPiece

        @staticmethod
        def revertReplacedPiece(board, row, col, removedPiece):
            if(removedPiece.color == 'Red'):
                Model.pieces['Red'].append(removedPiece)
            else:
                Model.pieces['Black'].append(removedPiece)

        @staticmethod
        def placePiece(board, oldRow, oldCol, row, col):
            (newX, newY) = Controller.getIntersectionCoords(Model.gameBoard, row, col)
            (oldX, oldY) = (Model.selectedPiece.x, Model.selectedPiece.y)
            removedPiece = None

            if(Model.gameBoard.pieces[row][col] != None):
                removedPiece = Controller.removeReplacedPiece(board, row, col)

            (Model.selectedPiece.x, Model.selectedPiece.y) = (newX, newY)
            
            Model.gameBoard.pieces[oldRow][oldCol] = None
            Model.gameBoard.pieces[row][col] = Model.selectedPiece

            if(Controller.kingsFacing(Model.gameBoard)):
                Model.gameBoard.pieces[oldRow][oldCol] = Model.selectedPiece
                (Model.selectedPiece.x, Model.selectedPiece.y) = (oldX, oldY)
                if(removedPiece != None):
                    Controller.revertReplacedPiece(Model.gameBoard, row, col, removedPiece)
                return False
            return True


        @staticmethod
        def switchPlayer():
            Model.currentPlayer = 'Black' if(Model.currentPlayer == 'Red') else 'Red'            

        @staticmethod
        def findKings(board):
            foundRedKing = False
            foundBlackKing = False
            for row in range(len(board.pieces)):
                for col in range(len(board.pieces[0])):
                    if(isinstance(board.pieces[row][col], King)):
                        piece = board.pieces[row][col]
                        if(piece.color == 'Red'):
                            (redKingRow, redKingCol) = (row, col)
                            foundRedKing = True
                        else:
                            (blackKingRow, blackKingCol) = (row, col)
                            foundBlackKing = True
            if(foundRedKing and foundBlackKing):
                return (redKingRow, redKingCol, blackKingRow, blackKingCol)
            return None

        @staticmethod
        def kingsFacing(board):
            if(len(Controller.findKings(board)) == 4):
                (rkRow, rkCol, bkRow, bkCol) = Controller.findKings(board)
                if(rkCol != bkCol):
                    return False
                else:
                    checkIndex = bkRow + 1
                    while(checkIndex < rkRow):
                        
                        if(board.pieces[checkIndex][bkCol] != None):
                            return False
                        checkIndex += 1

                    return True
            else:
                pass
                # Game Over state
        
        @staticmethod
        def checkGameOver(board):
            final = []
            color = 'Red' if(Model.currentPlayer == 'Red') else 'Black'
            for piece in Model.pieces[color]:
                (row, col) = Controller.getIntersection(board, piece.x, piece.y)
                legalMoves = piece.getLegalMoves(board, row, col)
                refinedMoves = Controller.refineLegalMoves(board, row, col, piece, legalMoves)
                final.extend(refinedMoves)
                
            if(len(final) == 0):
                print('GameOver CHECKMATE!')
                pass
                    

        @staticmethod
        def refineLegalMoves(board, row, col, piece, moves):
            changedMoves = copy.deepcopy(moves)
            for (newRow, newCol) in moves:
                #Temp changes
                removedPiece = None
                board.pieces[row][col] = None
                if(board.pieces[newRow][newCol] != None):
                    removedPiece = board.pieces[newRow][newCol]
                board.pieces[newRow][newCol] = piece

                # Check if valid
                if(Controller.kingsFacing(Model.gameBoard)):
                    changedMoves.remove((newRow, newCol))
            
                # Revert temp changes
                if(removedPiece != None):
                    board.pieces[newRow][newCol] = removedPiece
                else: 

                    board.pieces[newRow][newCol] = None
                board.pieces[row][col] = piece
            return changedMoves
                    

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
        def flipBoard(board):
            newBoard = copy.deepcopy(board)
            rows = len(board.pieces)
            cols = len(board.pieces[0])
            pivotCol = cols // 2
            pivotRow = (rows - 1) / 2

            print(pivotCol, pivotRow)

            for row in range(len(board.pieces)):
                for col in range(len(board.pieces[0])):
                    flipRowIndex = int(pivotRow - (row - pivotRow))
                    flipColIndex = int(pivotCol - (col - pivotCol))
                    newBoard.pieces[row][col] = board.pieces[flipRowIndex][flipColIndex]
                    (newX, newY) = Controller.getIntersectionCoords(newBoard, row, col)
                    if(newBoard.pieces[row][col] != None):
                        newBoard.pieces[row][col].x = newX
                        newBoard.pieces[row][col].y = newY
                
            board = newBoard

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
    # runGame()

testGame()