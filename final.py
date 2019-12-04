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
from panda3d.core import LPoint3, LVector3, BitMask32, DirectionalLight, Mat4
from panda3d.core import KeyboardButton
from direct.interval.IntervalGlobal import *

# Game Notes: Black has 0 row, Red has 9th row.

# Thanks to:
    # Professor Kosbie for suggesting 3D Chinese Chess for my TP idea
    # Elan for suggesting the idea of moving the camera after each move
    # Michelle for undying support <3


# From https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    # You do not need to understand how this function works.
    import decimal
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#Board Class attributes
class Board(object):
    def __init__(self):
        self.x, self.y, self.z = 0,0,0
        self.cols, self.rows = 9, 10
        self.width, self.height = 146, 164
        self.radiusX, self.radiusY = self.width / 2, self.height / 2
        self.cellWidth = self.width / (self.cols - 1)
        self.cellHeight = self.height / (self.rows - 1)
        self.pieces = [[None] * self.cols for row in range(self.rows)]
    def __repr__(self):
        for row in range(len(self.pieces)):
            print(self.pieces[row], end = ' ')
            print() 
    
    def printBoard(self):
        self.__repr__()

#Piece Class
class Piece(object):
    r = 20
    def __init__(self, x, y, color, model):
        self.x = x
        self.y = y
        self.color = color
        self.moveCount = 0
        self.model = model

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

#King Class (Black: 將, Red: 師)
class King(Piece):

    def __repr__(self):
        return 'King'

    # Horizontal and Vertical directions
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result
    
    # Must remain inside palace and no friendly piece blocking
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):        
        legalMoves = []
        if( (self.isInPalace(row + drow, col + dcol)) and
            ((board.pieces[row+drow][col+dcol] == None) or 
             (board.pieces[row+drow][col+dcol].color != self.color))):        
                legalMoves.append((row + drow, col + dcol))
        return legalMoves

#Guard Class (Black: 士, Red: 仕)
class Guard(Piece):

    def __repr__(self):
        return 'Guard'

    # Diagonal directions
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, +1]:
            for dcol in [-1, +1]:
                result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    # Must be within palace and no friendly piece blocking
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):        
        legalMoves = []
        if( (self.isInPalace(row + drow, col + dcol)) and
            ((board.pieces[row+drow][col+dcol] == None) or 
             (board.pieces[row+drow][col+dcol].color != self.color))):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
        return legalMoves

#Minister Class (Black: 象, Red: 相)
class Minister(Piece):
    
    def __repr__(self):
        return 'Minister'

    # Diagonal Directions
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, +1]:
            for dcol in [-1, +1]:
                result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    # Must move two at a time, must not cross river, no friendly piece in space
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

#Rook Class (Red/Black: 車)
class Rook(Piece):
    
    def __repr__(self):
        return 'Rook'
    
    # Horizontal and Vertical directions
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result
  
    # Takes and moves to any point on same horizontal or vertical line
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        finishedAttacking = False
        while(  (0 <= row + drow < board.rows) and 
                (0 <= col + dcol < board.cols) and 
                (not finishedAttacking)):
            if(board.pieces[row+drow][col+dcol] == None):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
            elif(board.pieces[row+drow][col+dcol].color != self.color):
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
                finishedAttacking = True
            else: break
        return legalMoves

#knight Class (Red/Black: 馬)
class Knight(Piece):

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
    
    # L-shape (two forward, then one to side)                   
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-2, -1, +1, +2]:
            for dcol in [-2, -1, +1, +2]:
                if(abs(abs(drow) - abs(dcol)) == 1):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    # Must not have piece one move in front of two move direction
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

#Cannon Class (Black: 炮, Red: 砲)
class Cannon(Piece):
    
    def __repr__(self):
        return 'Cannon'

    # Horizontal and Vertical directions
    def getLegalMoves(self, board, row, col):
        result = []
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                if(((drow != 0) and (dcol == 0 )) or 
                   ((dcol != 0) and (drow == 0))):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result

    # Movement: Identical to Rook
    # Attack: Must find friendly or enemy piece in front of facing direction to 
    #         jump over, then find enemy piece behind "jumped" piece.
    def getLegalMovesFromPoint(self, board, row, col, drow, dcol):
        legalMoves = []
        attacking = False
        finishedAttacking = False
        while((0 <= row + drow < board.rows) and (0 <= col + dcol < board.cols)):
            if((not attacking) and (board.pieces[row+drow][col+dcol] != None)):
                attacking = True
                row += drow
                col += dcol
            elif(attacking and (not finishedAttacking)):
                if( (board.pieces[row+drow][col+dcol] != None) and 
                    (board.pieces[row+drow][col+dcol].color != self.color)):
                    legalMoves.append((row + drow, col + dcol))
                    break
                row += drow
                col += dcol   
            elif(board.pieces[row+drow][col+dcol] == None):        
                legalMoves.append((row + drow, col + dcol))
                row += drow
                col += dcol
            else: break
        return legalMoves

#Pawn Class (Black: 卒, Red: 兵)
class Pawn(Piece):
    def __init__(self, x, y, color, model):
        super().__init__(x, y, color, model)
        self.hasCrossedRiver = False
    
    # If pawn has taken two moves, it has crossed the river
    def updateCrossedRiver(self):
        self.hasCrossedRiver = True if(self.moveCount >= 2) else False
    
    def __repr__(self):
        return 'Pawn'
    
    # Not crossed river: Forward direction
    # Crossed river: Forward and horizontal directions
    def getLegalMoves(self, board, row, col):
        self.updateCrossedRiver()    
        result = []
        horizontalMoves = [-1, 0, +1] if (self.hasCrossedRiver) else [0]
        verticalMoves = [-1, 0] if (self.color == 'Red') else [+1, 0]

        for drow in verticalMoves:
            for dcol in horizontalMoves:
                if(((drow != 0) and (dcol == 0 )) or 
                    (dcol != 0) and (drow == 0)):
                    result.extend(self.getLegalMovesFromPoint(board,row,col,drow,dcol))
        return result
    
    # Must not be friendly piece in way
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

# Wrapper Function that contains 3D helper function, 3D Game class, Model class, Controller class
def runGame(): 

    # From Panda3D Chessboard demo
    # https://github.com/kralf/panda3d/blob/master/python/bin/samples/chessboard.py
    def PointAtZ(z, point, vec):
        return point + vec * ((z - point.getZ()) / vec.getZ())
    
    #3D Main App Class
    class ChineseChess112(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            
            #Initialize Game and World for first time.
            Controller.createLighting(self)
            Controller.initGame(self)
            Controller.createCollisionChecker(self)
            Controller.setMenuCamera(self)

            # Check for mouse and keys events
            self.accept('mouse1', self.keyHandler, ['mouse1'])
            self.accept('arrow_left', self.keyHandler, ['arrow_left'])
            self.accept('arrow_right', self.keyHandler, ['arrow_right'])
            self.taskMgr.add(self.checkKeys, "CheckKeysTask")
    
        #Event handlers for in-game keys, menu
        def checkKeys (self, task):
            arrow_left = KeyboardButton.left()
            arrow_right = KeyboardButton.right()
            arrow_up = KeyboardButton.up()
            arrow_down = KeyboardButton.down()
            space = KeyboardButton.space()
            escape = KeyboardButton.escape()
            g = KeyboardButton.ascii_key('g')
            j = KeyboardButton.ascii_key('j')
            k = KeyboardButton.ascii_key('k')
            w = KeyboardButton.ascii_key('w')
            a = KeyboardButton.ascii_key('a')
            s = KeyboardButton.ascii_key('s')
            d = KeyboardButton.ascii_key('d')

            isDown = base.mouseWatcherNode.is_button_down

            # Space: Go to game (based on current player)
            if((isDown(space)) and ((not Model.playingGame) or (Model.inInstructions))):
                Model.playingGame = True
                if(Model.currentPlayer == 'Red'):
                    Controller.toDefaultRed(self)
                else:
                    Controller.toDefaultBlack(self)

            # g: Go to instructions 
            elif(isDown(g)):
                Model.inInstructions = True
                Controller.toInstructionsCamera(self)

            # Esc: Go to menu
            elif(isDown(escape)):
                Model.playingGame = False
                Model.inInstructions = False
                Model.slideIndex = 0
                Controller.toMenuCamera(self)
                # If game over (checkmate), remove check and checkmate models
                if(Model.gameOver):
                    Model.gameOver = False
                    Model.kingInCheck.removeNode()
                    Model.kingCheckmated.removeNode()
                    Controller.initGame(self)
            
            # In game keys
            elif(Model.playingGame):
                # Left arrow: Rotate camera to the left
                if(isDown(arrow_left)):
                    (h,p,r) = self.dummy.getHpr()
                    moveDummyHpr = LerpHprInterval(self.dummy, 0.25, LVector3(h-5, p, r))
                    moveDummyHpr.start()

                # Right arrow: Rotate camera to the right
                elif(isDown(arrow_right)):
                    (h,p,r) = self.dummy.getHpr()
                    moveDummyHpr = LerpHprInterval(self.dummy, 0.25, LVector3(h+5, p, r))
                    moveDummyHpr.start()

                # Down arrow: Tilt camera backwards (stops at certain angle)
                elif(isDown(arrow_up)):
                    (h,p,r) = self.dummy.getHpr()
                    if(p - 5 > -75):
                        moveDummyHpr = LerpHprInterval(self.dummy, 0.25, LVector3(h, p-5, r))
                        moveDummyHpr.start()

                # Up arrow: Tilt camera forwards (stops at certain angle)
                elif(isDown(arrow_down)):
                    (h,p,r) = self.dummy.getHpr()
                    if(p + 5 < 75):
                        moveDummyHpr = LerpHprInterval(self.dummy, 0.25, LVector3(h, p+5, r))
                        moveDummyHpr.start()

                # W: move camera forward (will be relative to current camera rotation)
                if(isDown(w)):
                    (x,y,z) = self.dummy.getPos()
                    h = self.dummy.getH()
                    hpi = (h*math.pi) / 180
                    moveCam = LerpPosInterval(self.dummy, 0.25, LPoint3(x-10*math.sin(hpi), y+10*math.cos(hpi), z))
                    moveCam.start()
                
                # S: move camera backward (will be relative to current camera rotation)
                elif(isDown(s)):
                    (x,y,z) = self.dummy.getPos()
                    h = self.dummy.getH()
                    hpi = (h*math.pi) / 180
                    moveCam = LerpPosInterval(self.dummy, 0.25, LPoint3(x+10*math.sin(hpi), y-10*math.cos(hpi), z))
                    moveCam.start()
                
                # A: move camera to the left (will be relative to current camera rotation)
                elif(isDown(a)):
                    (x,y,z) = self.dummy.getPos()
                    h = self.dummy.getH()
                    hpi = (h*math.pi) / 180
                    moveCam = LerpPosInterval(self.dummy, 0.25, LPoint3(x-10*math.cos(hpi), y-10*math.sin(hpi), z))
                    moveCam.start()
                
                # d: move camera to the right (will be relative to current camera rotation)
                elif(isDown(d)):
                    (x,y,z) = self.dummy.getPos()
                    h = self.dummy.getH()
                    hpi = (h*math.pi) / 180
                    moveCam = LerpPosInterval(self.dummy, 0.25, LPoint3(x+10*math.cos(hpi), y+10*math.sin(hpi), z))
                    moveCam.start()
                
                # j: Zoom camera in (will stop at certain zoom level)
                elif(isDown(j)):
                    (x,y,z) = self.camera.getPos()
                    if(0.8 * z > 100):
                        movePos = LerpPosInterval(self.camera, 0.25, LPoint3(0.8*x, 0.8*y, 0.8*z))
                        movePos.start()
                
                # k: Zoom camera out (will stop at certain zoom level)
                elif(isDown(k)):
                    (x,y,z) = self.camera.getPos()
                    if(1.25 * z < 700):
                        movePos = LerpPosInterval(self.camera, 0.25, LPoint3(1.25*x, 1.25*y, 1.25*z))
                        movePos.start()
            return Task.cont

        # Event function for a mouse click
        def mousePressed(self):
            if self.mouseWatcherNode.hasMouse():
                # Collision detection logic form Panda3D chessboard demo
                # https://github.com/kralf/panda3d/blob/master/python/bin/samples/chessboard.py
                mpos = self.mouseWatcherNode.getMouse()
                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
                nearPoint = render.getRelativePoint(camera, self.pickerRay.getOrigin())
                nearVec = render.getRelativeVector(camera, self.pickerRay.getDirection())
                
                # Get click position in 3D world and perform game logic
                self.empty.setPos(PointAtZ(.5, nearPoint, nearVec))
                (x,y,z) = self.empty.getPos()
                Controller.selectAndMove(x, y, self)
        
        #Event handler for mouse click and arrow keys in instruction screen
        def keyHandler(self,key):
            # Arrow keys in Instructions
            if(Model.inInstructions):
                # Move to previous instruction slide
                if(key == 'arrow_left'):
                    if(Model.slideIndex != 0):
                        (x,y,z) = self.dummy.getPos()
                        moveDummyPos = LerpPosInterval(self.dummy, 1.0, LPoint3(x, y+360, z), blendType = 'easeInOut')
                        moveDummyPos.start()
                        Model.slideIndex -= 1

                # Move to next instruction slide
                elif(key == 'arrow_right'):
                    if(Model.slideIndex != 4): 
                        (x,y,z) = self.dummy.getPos()
                        moveDummyPos = LerpPosInterval(self.dummy, 1.0, LPoint3(x, y-360, z), blendType = 'easeInOut')
                        moveDummyPos.start()
                        Model.slideIndex += 1
            # Mouse click
            elif(key == 'mouse1'):
                self.mousePressed()
    
    # Game data and 3D world important variables
    class Model(object):    
        
        # Create Board
        gameBoard = Board()
        middleRow = gameBoard.rows // 2 - 1
        middleCol = gameBoard.cols // 2

        # Create empty dictionary of game pieces, lists of pieces, instructions
        pieces = dict()
        pieces['Red'], pieces['Black'], tempMoves, instructions = [], [], [], []
        
        # Board and game specific variables
        slideIndex, width, height = 0, 500, 600
        selectedPosition = (-1,-1)
        currentPlayer = 'Red'
        
        # Initially unused models
        selectedPiece, selectedModel = None, None
        kingCheckmated, kingInCheck = None, None

        # Used Models
        boardLines, boardBody, boardBase, river = None, None, None, None
        showBase, menu, palaceRed, palaceBlack = None, None, None, None
        
        # App states
        gameOver, playingGame, inInstructions = False, False, False

    #Methods for game and 3D manipulation and logic
    class Controller(object):
        
        @staticmethod
        def initGame(showBase):

            showBase.disableMouse()
            Controller.clearBoardAndPieces()
            Controller.initUnusedModels(showBase)
            Controller.createMenu(showBase)
            Controller.createInstructions(showBase)
            Controller.createPieces(showBase)
            Controller.createBoard(showBase)
            Controller.putPiecesInBoard(Model.gameBoard)
            Controller.updatePieces(showBase)
            
            print('Game Initiated!')
        
        # Initializes unused models at the start of the game 
        #    (reduces lag in-game but increases start up time)
        @staticmethod
        def initUnusedModels(showBase):
            Model.rCheckmate = showBase.loader.loadModel('models/redkingcheckmated')
            Model.bCheckmate = showBase.loader.loadModel('models/blackkingcheckmated')
            Model.redKingCheckModel = showBase.loader.loadModel('models/redkingincheck')
            Model.blackKingCheckModel = showBase.loader.loadModel('models/blackkingincheck')
            Model.rPawnSel = showBase.loader.loadModel('models/redpawnselect')
            Model.bPawnSel = showBase.loader.loadModel('models/blackpawnselect')
            Model.knightSel = showBase.loader.loadModel('models/knightselect')
            Model.rookSel = showBase.loader.loadModel('models/rookselect')
            Model.rCannonSel = showBase.loader.loadModel('models/redcannonselect')
            Model.bCannonSel = showBase.loader.loadModel('models/blackcannonselect')
            Model.rMinisterSel = showBase.loader.loadModel('models/redministerselect')
            Model.bMinisterSel = showBase.loader.loadModel('models/blackministerselect')
            Model.rGuardSel = showBase.loader.loadModel('models/redguardselect')
            Model.bGuardSel = showBase.loader.loadModel('models/blackguardselect')
            Model.rKingSel = showBase.loader.loadModel('models/redkingselect')
            Model.bKingSel = showBase.loader.loadModel('models/blackkingselect')

        # Initilize lighting in 3D world
        @staticmethod
        def createLighting(showBase):
            showBase.dlight = DirectionalLight('DLight')
            showBase.dlnp = render.attachNewNode(showBase.dlight)
            showBase.dlnp.setHpr(0, 90, 0)
            render.setLight(showBase.dlnp)

        # Initializes first camera position
        @staticmethod
        def setMenuCamera(showBase):       
            showBase.dummy = render.attachNewNode('dummyNode')
            showBase.camera.reparentTo(showBase.dummy)
            showBase.camera.setPos(0, 0, 250)
            showBase.camera.setHpr(0, -90, 0)
            showBase.dummy.setHpr(-90, -180, 0)

        # From Panda3D Chessboard demo
        # https://github.com/kralf/panda3d/blob/master/python/bin/samples/chessboard.py
        # Checks for a collision between 'null' model shot from camera and objects
        # in the 3D world
        @staticmethod
        def createCollisionChecker(showBase):
            #Create null object that inhabits click position
            showBase.empty = showBase.loader.loadModel("models/redcannon")
            showBase.empty.setPos(0, 0 ,5)
            showBase.empty.setScale(10, -10, 10)
            #Object that detects collisions
            showBase.picker = CollisionTraverser()  
            #Holds all objects that are collided
            showBase.pq = CollisionHandlerQueue()  
            # Make a collision node for our picker ray (will be the thing colliding)
            showBase.pickerNode = CollisionNode('mouseRay')
            # Attach that node to the camera since the ray will need to be positioned
            # relative to it
            showBase.pickerNP = camera.attachNewNode(showBase.pickerNode)
            # Everything to be picked will use bit 1. This way if we were doing other
            # collision we could separate it
            showBase.pickerNode.setFromCollideMask(BitMask32.bit(1))
            showBase.pickerRay = CollisionRay()  # Make our ray
            # Add it to the collision node
            showBase.pickerNode.addSolid(showBase.pickerRay)
            # Register the ray as something that can cause collisions
            showBase.picker.addCollider(showBase.pickerNP, showBase.pq)
        
        # Interval (animation) to move to default black player position in-game
        @staticmethod
        def toDefaultBlack(showBase):  
            moveLightHpr = LerpHprInterval(showBase.dlnp, 3.0, LPoint3(0, -90, 0), blendType = 'easeInOut') 
            moveCamPos = LerpPosInterval(showBase.camera, 3.0, LPoint3(0, 0, 400), blendType = 'easeInOut')
            moveDummyPos = LerpPosInterval(showBase.dummy, 3.0, LPoint3(0, 0, 0), blendType = 'easeInOut')
            moveDummyHpr = LerpHprInterval(showBase.dummy, 3.0, LVector3(180, 30, 0), blendType = 'easeInOut')
            movePar = Parallel(moveDummyHpr, moveDummyPos, moveCamPos, moveLightHpr)
            movePar.start()

        # Interval (animation) to move to default red player position in-game
        @staticmethod
        def toDefaultRed(showBase):    
            moveLightHpr = LerpHprInterval(showBase.dlnp, 3.0, LPoint3(0, -90, 0), blendType = 'easeInOut')
            moveCamPos = LerpPosInterval(showBase.camera, 3.0, LPoint3(0, 0, 400), blendType = 'easeInOut')
            moveDummyPos = LerpPosInterval(showBase.dummy, 3.0, LPoint3(0, 0, 0), blendType = 'easeInOut')
            moveDummyHpr = LerpHprInterval(showBase.dummy, 3.0, LVector3(0, 30, 0), blendType = 'easeInOut')
            movePar = Parallel(moveDummyHpr, moveDummyPos, moveCamPos, moveLightHpr)
            movePar.start()

        # Interval (animation) to move to main menu
        @staticmethod
        def toMenuCamera(showBase):       
            moveLightHpr = LerpHprInterval(showBase.dlnp, 3.0, LPoint3(0, 90, 0), blendType = 'easeInOut')
            moveCamPos = LerpPosInterval(showBase.camera, 3.0, LPoint3(0, 0, 250), blendType = 'easeInOut')
            moveDummyPos = LerpPosInterval(showBase.dummy, 3.0, LPoint3(0, 0, 0), blendType = 'easeInOut')
            moveDummyHpr = LerpHprInterval(showBase.dummy, 3.0, LVector3(-90, -180, 0), blendType = 'easeInOut')
            movePar = Parallel(moveDummyHpr, moveDummyPos, moveCamPos, moveLightHpr)
            movePar.start()
    
        # Interval (animation) to move to instructions
        @staticmethod
        def toInstructionsCamera(showBase):
            moveLightHpr = LerpHprInterval(showBase.dlnp, 3.0, LPoint3(0, 90, 0), blendType = 'easeInOut')
            moveCamPos = LerpPosInterval(showBase.camera, 3.0, LPoint3(0, 0, 250), blendType = 'easeInOut')
            moveDummyHpr = LerpHprInterval(showBase.dummy, 3.0, LVector3(-90, -180, 0), blendType = 'easeInOut')
            moveDummyPos = LerpPosInterval(showBase.dummy, 3.0, LPoint3(325, 0, 310), blendType = 'easeInOut')
            movePar = Parallel(moveDummyPos, moveDummyHpr, moveCamPos, moveLightHpr)
            movePar.start()
        
        # Create Instructions models in scene
        @staticmethod
        def createInstructions(showBase):
            instruct1 = showBase.loader.loadModel("models/instruct1")
            instruct2 = showBase.loader.loadModel("models/instruct2")
            instruct3 = showBase.loader.loadModel("models/instruct3")
            instruct4 = showBase.loader.loadModel("models/instruct4")
            instruct5 = showBase.loader.loadModel("models/instruct5")
            Model.instructions.extend([instruct1, instruct2, instruct3, instruct4, instruct5])
            for slide in Model.instructions:
                slide.reparentTo(showBase.render)
                slide.setScale(100, 100, 100)

        # Create menu object in scene
        @staticmethod
        def createMenu(showBase):
            Model.menu = showBase.loader.loadModel("models/menu")
            Model.menu.reparentTo(showBase.render)
            Model.menu.setScale(100, 100, 100)
        
        # Create board in scene
        @staticmethod
        def createBoard(showBase):
            Model.boardLines = showBase.loader.loadModel("models/boardLines")
            Model.boardBody = showBase.loader.loadModel("models/boardBody")
            Model.boardBase = showBase.loader.loadModel("models/boardBase")
            Model.palaceRed = showBase.loader.loadModel("models/redpalace")
            Model.palaceBlack = showBase.loader.loadModel("models/blackpalace")
            Model.river = showBase.loader.loadModel("models/river")
            Model.palaceRed.reparentTo(showBase.render)
            Model.palaceBlack.reparentTo(showBase.render)
            Model.boardLines.reparentTo(showBase.render)
            Model.boardBody.reparentTo(showBase.render)
            Model.boardBase.reparentTo(showBase.render)
            Model.river.reparentTo(showBase.render)
            Model.palaceRed.setScale(100, 100, 100)
            Model.palaceBlack.setScale(100, 100, 100)
            Model.boardLines.setScale(100, 100, 100)
            Model.boardBody.setScale(100, 100, 100)
            Model.boardBase.setScale(100, 100, 100)
            Model.river.setScale(100, 100, 100)

        # Creates all piece models (not game objects) in scene
        @staticmethod
        def updatePieces(showBase):
            for color in Model.pieces:
                for piece in Model.pieces[color]:
                    piece.model.reparentTo(showBase.render)
                    piece.model.setScale(9, -9, 9)
                    if(piece.color == 'Black'):
                        piece.model.setHpr(-180, 0, 0)
                    piece.model.setPos(piece.x, piece.y, 5)

        # Removes all piece models, restarts board and game logic
        @staticmethod
        def clearBoardAndPieces():
            # Visually clear models
            for piece in Model.pieces['Red']:
                piece.model.removeNode()
                
            for piece in Model.pieces['Black']:
                piece.model.removeNode()

            # Reset game values
            Model.gameBoard = Board()
            Model.middleRow = Model.gameBoard.rows // 2 - 1
            Model.middleCol = Model.gameBoard.cols // 2 
            
            Model.pieces = dict()
            Model.pieces['Red'], Model.pieces['Black'] = [], []
            Model.tempMoves, Model.instructions = [], []

            Model.selectedPiece, Model.selectedModel = None, None
            Model.kingCheckmated, Model.kingInCheck = None, None
            
            Model.slideIndex = 0
            Model.selectedPosition = (-1,-1)
            Model.currentPlayer = 'Red'

            Model.gameOver, Model.playingGame, Model.inInstructions = False, False, False
        
        # Create pawn game objects
        @staticmethod
        def createPawns(board, showBase):
            numPawns = 5
            for i in range(numPawns):
                bx, by = Controller.getIntersectionCoords(board, 3, 2*i)
                rx, ry = Controller.getIntersectionCoords(board, 6, 2*i)
                pawnModelBlack = showBase.loader.loadModel('models/blackpawn')
                pawnModelRed = showBase.loader.loadModel('models/redpawn')
                Model.pieces['Black'].append(Pawn(bx, by, 'Black', pawnModelBlack))
                Model.pieces['Red'].append(Pawn(rx, ry, 'Red', pawnModelRed))
    
        # Create 'doubled' game objects (any piece with two initially)
        @staticmethod
        def createDoubles(board, pieceType, showBase):
            numPieces = 2
            for i in range(numPieces):
                if(pieceType == 'Rook'): 
                    rookModelBlack = showBase.loader.loadModel("models/blackrook")
                    rookModelRed = showBase.loader.loadModel("models/redrook")
                    (spacing, initialCol) = (8, 0)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Rook(bx, by, 'Black', rookModelBlack))
                    Model.pieces['Red'].append(Rook(rx, ry, 'Red', rookModelRed))
                elif(pieceType == 'Knight'):
                    knightModelBlack = showBase.loader.loadModel("models/blackknight")
                    knightModelRed = showBase.loader.loadModel("models/redknight")
                    (spacing, initialCol) = (6, 1)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Knight(bx, by, 'Black', knightModelBlack))
                    Model.pieces['Red'].append(Knight(rx, ry, 'Red', knightModelRed))
                elif(pieceType == 'Cannon'):
                    cannonModelBlack = showBase.loader.loadModel("models/blackcannon")
                    cannonModelRed = showBase.loader.loadModel("models/redcannon")
                    (spacing, initialCol) = (6, 1)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Cannon(bx, by, 'Black', cannonModelBlack))
                    Model.pieces['Red'].append(Cannon(rx, ry, 'Red', cannonModelRed))
                elif(pieceType == 'Minister'): 
                    ministerModelBlack = showBase.loader.loadModel("models/blackminister")
                    ministerModelRed = showBase.loader.loadModel("models/redminister")
                    (spacing, initialCol) = (4, 2)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Minister(bx, by, 'Black', ministerModelBlack))
                    Model.pieces['Red'].append(Minister(rx, ry, 'Red', ministerModelRed))
                elif(pieceType == 'Guard'): 
                    guardModelBlack = showBase.loader.loadModel("models/blackguard")
                    guardModelRed = showBase.loader.loadModel("models/redguard")
                    (spacing, initialCol) = (2, 3)
                    (bx,by,rx,ry) = Controller.getBxByRxRyHelper(board, pieceType, spacing, 
                                                            initialCol, i)
                    Model.pieces['Black'].append(Guard(bx, by, 'Black', guardModelBlack))
                    Model.pieces['Red'].append(Guard(rx, ry, 'Red', guardModelRed))

        # Helper method for creating doubles game objects
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

        # Create king game objects
        @staticmethod
        def createKings(board, showBase):
            kingModelBlack = showBase.loader.loadModel("models/blackking")
            kingModelRed = showBase.loader.loadModel("models/redking")
            bx, by = Controller.getIntersectionCoords(board, 0, Model.middleCol)
            rx, ry = Controller.getIntersectionCoords(board, Model.gameBoard.rows-1, Model.middleCol)
            Model.pieces['Black'].append(King(bx, by, 'Black', kingModelBlack))
            Model.pieces['Red'].append(King(rx, ry, 'Red', kingModelRed))

        # Create all piece game objects (not models)
        @staticmethod
        def createPieces(showBase):
            Controller.createPawns(Model.gameBoard, showBase)
            Controller.createDoubles(Model.gameBoard, 'Rook' , showBase)
            Controller.createDoubles(Model.gameBoard, 'Cannon' , showBase)
            Controller.createDoubles(Model.gameBoard, 'Knight' , showBase)
            Controller.createDoubles(Model.gameBoard, 'Minister' , showBase)
            Controller.createDoubles(Model.gameBoard, 'Guard' , showBase)
            Controller.createKings(Model.gameBoard, showBase)
        
        # Returns (x,y) position of (row,col) on board
        @staticmethod
        def getIntersectionCoords(board, row, col):
            x = -Model.gameBoard.radiusX + col*(board.cellWidth)
            y = Model.gameBoard.radiusY - row*(board.cellHeight)
            return (x, y)
        
        # Returns whether click is near legal game board
        @staticmethod
        def isNearBoard(x, y):
            return ((-Model.gameBoard.radiusX - Piece.r <= x <= Model.gameBoard.radiusX + Piece.r) and
                    (-Model.gameBoard.radiusY - Piece.r <= y <= Model.gameBoard.radiusY + Piece.r))

        # Returns (row,col) or (x,y) position on board
        @staticmethod
        def getIntersection(board, x, y):
            row = roundHalfUp((Model.gameBoard.radiusY - y) / board.cellHeight)
            col = roundHalfUp((Model.gameBoard.radiusX + x) / board.cellWidth)
            return (row,col)

        # Initially put all piece models into scene
        @staticmethod
        def putPiecesInBoard(board):
            for color in Model.pieces:
                for piece in Model.pieces[color]:
                    (row,col) = Controller.getIntersection(board, piece.x, piece.y)
                    board.pieces[row][col] = piece

        # Select a piece from a given (row,col)
        @staticmethod
        def selectPiece(board, row, col):
            if(board.pieces[row][col] != None):
                Model.selectedPosition = (row, col)
                return board.pieces[row][col]
        
        # Remove and return a piece in (row,col)
        @staticmethod
        def removeReplacedPiece(board, row, col):
            color = Model.gameBoard.pieces[row][col].color
            index = Model.pieces[color].index(Model.gameBoard.pieces[row][col])
            removedPiece = Model.pieces[color].pop(index)
            (x,y,z) = removedPiece.model.getPos()
            removedPiece.model.setPos(x,y,z-10)
            return removedPiece

        # Revert a piece replacement (if a move turns out to be illegal)
        @staticmethod
        def revertReplacedPiece(board, row, col, removedPiece):
            if(removedPiece.color == 'Red'):
                Model.pieces['Red'].append(removedPiece)
            else:
                Model.pieces['Black'].append(removedPiece)
            (x,y,z) = removedPiece.model.getPos()
            removedPiece.model.setPos(x,y,z+10)

        # Place a piece from (oldRow,oldCol) onto (row,col)
        @staticmethod
        def placePiece(board, oldRow, oldCol, row, col):
            
            # Update piece coords
            (newX, newY) = Controller.getIntersectionCoords(Model.gameBoard, row, col)
            (Model.selectedPiece.x, Model.selectedPiece.y) = (newX, newY)
            
            # Check if another piece is on (row,col), if so, remove
            if(Model.gameBoard.pieces[row][col] != None):
                removedPiece = Controller.removeReplacedPiece(board, row, col)
                removedPiece.model.removeNode()
            
            # Update gameboard with move
            Model.gameBoard.pieces[oldRow][oldCol] = None
            Model.gameBoard.pieces[row][col] = Model.selectedPiece

        # Switch the current player and move camera 
        @staticmethod
        def switchPlayer(showBase):
            if(Model.currentPlayer == 'Red'):
                Model.currentPlayer = 'Black'  
                Controller.toDefaultBlack(showBase)
            else:
                Model.currentPlayer = 'Red'    
                Controller.toDefaultRed(showBase)

        # Find the (row,col) of each king on the board    
        @staticmethod
        def findKings(board):
            for row in range(len(board.pieces)):
                for col in range(len(board.pieces[0])):
                    if(isinstance(board.pieces[row][col], King)):
                        piece = board.pieces[row][col]
                        if(piece.color == 'Red'):
                            (redKingRow, redKingCol) = (row, col)
                        else:
                            (blackKingRow, blackKingCol) = (row, col)
            
            return (redKingRow, redKingCol, blackKingRow, blackKingCol)

        # Check if two kings are facing each other on the board
        @staticmethod
        def kingsFacing(board):
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
        
        # Check if player has any "legal" moves
        # If not: checkmate/stalemate and enter gameover state
        @staticmethod
        def checkGameOver(board, showBase):  
            final = []
            color = 'Red' if(Model.currentPlayer == 'Red') else 'Black'

            # Get every possible legal move for a player
            for piece in Model.pieces[color]:
                (row, col) = Controller.getIntersection(board, piece.x, piece.y)
                legalMoves = piece.getLegalMoves(board, row, col)
                refinedMoves = Controller.refineLegalMoves(board, row, col, piece, legalMoves)
                final.extend(refinedMoves)

            # If there are none, show checkmate models and enter gameover state 
            if(len(final) == 0):
                (rkRow, rkCol, bkRow, bkCol) = Controller.findKings(board)
                if(Model.currentPlayer == 'Red'):
                    kingPiece = board.pieces[rkRow][rkCol]
                    Model.kingCheckmated = Model.rCheckmate
                    Model.kingCheckmated.reparentTo(showBase.render)
                    Model.kingCheckmated.setScale(9, -9, 9)
                    (x,y) = (kingPiece.x, kingPiece.y)
                    Model.kingCheckmated.setPos(x, y, 7)
                else:
                    kingPiece = board.pieces[bkRow][bkCol]
                    Model.kingCheckmated = Model.bCheckmate
                    Model.kingCheckmated.reparentTo(showBase.render)
                    Model.kingCheckmated.setScale(9, -9, 9)
                    (x,y) = (kingPiece.x, kingPiece.y)
                    Model.kingCheckmated.setPos(x, y, 7)
                    Model.kingCheckmated.setHpr(180, 0, 0)

                Model.gameOver = True

        # Takes a piece legal moves from position and refines them according to
        # game constraints (kings facing, putting own king in check)
        @staticmethod
        def refineLegalMoves(board, row, col, piece, moves):
            changedMoves = copy.deepcopy(moves)
            # Try each legal move and see if it fits with constraints
            for (newRow, newCol) in moves:
                removedPiece = None
                board.pieces[row][col] = None
                if(board.pieces[newRow][newCol] != None):
                    removedPiece = board.pieces[newRow][newCol]
                board.pieces[newRow][newCol] = piece
                
                # Find the kings
                if(piece.color == 'Red'):
                    (kingRow, kingCol, notNeeded1, notNeeded2) = Controller.findKings(board)
                else:
                    (notNeeded1, notNeeded2, kingRow, kingCol) = Controller.findKings(board)
 
                # Check if valid move (kings facing and check) 
                # If not, move will be removed from initial deepcopy
                if(Controller.kingsFacing(Model.gameBoard)):
                    changedMoves.remove((newRow, newCol))
                elif(Controller.isInCheck(board, kingRow, kingCol, piece.color)):
                    changedMoves.remove((newRow, newCol))

                # Revert temp changes 
                if(removedPiece != None):
                    board.pieces[newRow][newCol] = removedPiece
                else: 
                    board.pieces[newRow][newCol] = None
                board.pieces[row][col] = piece
            
            # Return deepcopy with illegal moves removed
            return changedMoves

        # Checks whether a certain king in (kingRow,kingCol) is in check
        @staticmethod
        def isInCheck(board, kingRow, kingCol, color):
            if color == 'Red':
                for piece in Model.pieces['Black']:
                    (row, col) = Controller.getIntersection(board, piece.x, piece.y)
                    if((kingRow, kingCol) in piece.getLegalMoves(board, row, col)):
                        return True
                return False
            else:
                for piece in Model.pieces['Red']:
                    (row, col) = Controller.getIntersection(board, piece.x, piece.y)
                    if((kingRow, kingCol) in piece.getLegalMoves(board, row, col)):
                        return True
                return False
        
        # Highlights all the refined legal moves for a piece
        @staticmethod
        def highlightLegalMoves(board, moves, showBase):
            for (row, col) in moves:
                (x, y) = Controller.getIntersectionCoords(board, row, col)
                if(board.pieces[row][col] != None): 
                    temp = showBase.loader.loadModel('models/takeable')
                else: temp = showBase.loader.loadModel('models/possiblemove')
                Model.tempMoves.append(temp)
                temp.reparentTo(showBase.render)
                temp.setScale(9, -9, 9)
                temp.setPos(x, y, 6)
        
        # Removes highlighted legal moves when piece deselected or moved
        @staticmethod
        def removeHighlightedMoves():
            for piece in Model.tempMoves:
                piece.removeNode()

        # If king is in check, place incheck model
        @staticmethod
        def updateInCheckModels(board, showBase):
            (rkRow, rkCol, bkRow, bkCol) = Controller.findKings(board)
            if(Controller.isInCheck(board, rkRow, rkCol, 'Red')):
                kingPiece = board.pieces[rkRow][rkCol]
                Model.redKingCheckModel = showBase.loader.loadModel('models/redkingincheck')
                Model.kingInCheck = Model.redKingCheckModel
                Model.kingInCheck.reparentTo(showBase.render)
                Model.kingInCheck.setScale(9, -9, 9)
                (x,y) = (kingPiece.x, kingPiece.y)
                Model.kingInCheck.setPos(x, y, 6)
            elif(Controller.isInCheck(board, bkRow, bkCol, 'Black')):
                kingPiece = board.pieces[bkRow][bkCol]
                Model.blackKingCheckModel = showBase.loader.loadModel('models/blackkingincheck')
                Model.kingInCheck = Model.blackKingCheckModel
                Model.kingInCheck.reparentTo(showBase.render)
                Model.kingInCheck.setScale(9, -9, 9)
                (x,y) = (kingPiece.x, kingPiece.y)
                Model.kingInCheck.setPos(x, y, 6)
                Model.kingInCheck.setHpr(180, 0, 0)  

        # If king is no longer in check, remove incheck model 
        @staticmethod
        def removeInCheckModels():
            if(Model.kingInCheck != None): Model.kingInCheck.removeNode()

        # Add a "selected" green model for current selected piece 
        @staticmethod
        def selectPieceModel(showBase):
            if(isinstance(Model.selectedPiece, Pawn)):    
                if(Model.selectedPiece.color == 'Red'):
                    Model.rPawnSel = showBase.loader.loadModel('models/redpawnselect')
                    Model.selectedModel = Model.rPawnSel
                else:
                    Model.bPawnSel = showBase.loader.loadModel('models/blackpawnselect') 
                    Model.selectedModel = Model.bPawnSel
            elif(isinstance(Model.selectedPiece, Rook)):
                Model.rookSel = showBase.loader.loadModel('models/rookselect')
                Model.selectedModel = Model.rookSel
            elif(isinstance(Model.selectedPiece, Knight)):
                Model.knightSel = showBase.loader.loadModel('models/knightselect')
                Model.selectedModel = Model.knightSel
            elif(isinstance(Model.selectedPiece, Minister)):
                if(Model.selectedPiece.color == 'Red'):
                    Model.rMinisterSel = showBase.loader.loadModel('models/redministerselect')
                    Model.selectedModel = Model.rMinisterSel
                else:
                    Model.bMinisterSel = showBase.loader.loadModel('models/blackministerselect') 
                    Model.selectedModel = Model.bMinisterSel
            elif(isinstance(Model.selectedPiece, Guard)):
                if(Model.selectedPiece.color == 'Red'):
                    Model.rGuardSel = showBase.loader.loadModel('models/redguardselect')
                    Model.selectedModel = Model.rGuardSel
                else: 
                    Model.bGuardSel = showBase.loader.loadModel('models/blackguardselect')
                    Model.selectedModel = Model.bGuardSel
            elif(isinstance(Model.selectedPiece, Cannon)):
                if(Model.selectedPiece.color == 'Red'):
                    Model.rCannonSel = showBase.loader.loadModel('models/redcannonselect')
                    Model.selectedModel = Model.rCannonSel
                else: 
                    Model.bCannonSel = showBase.loader.loadModel('models/blackcannonselect')
                    Model.selectedModel = Model.bCannonSel
            elif(isinstance(Model.selectedPiece, King)): 
                if(Model.selectedPiece.color == 'Red'):
                    Model.rKingSel = showBase.loader.loadModel('models/redkingselect')
                    Model.selectedModel = Model.rKingSel
                else: 
                    Model.bKingSel = showBase.loader.loadModel('models/blackkingselect') 
                    Model.selectedModel = Model.bKingSel
            
            Model.selectedModel.reparentTo(showBase.render)
            Model.selectedModel.setScale(9, -9, 9)
            if(Model.selectedPiece.color == 'Black'):
                Model.selectedModel.setHpr(180, 0, 0)    
            Model.selectedModel.setPos(Model.selectedPiece.x, Model.selectedPiece.y, 6)
            
        # Remove special "selected" piece model
        @staticmethod
        def deselectPieceModel(showBase):
            Model.selectedModel.removeNode()
            Model.selectedModel = None

        # Main game logic from mouseclick
        @staticmethod
        def selectAndMove(x,y, showBase):
            #If user clicked in board
            if(Controller.isNearBoard(x, y)):
                (row,col) = Controller.getIntersection(Model.gameBoard, x, y)
                (oldRow, oldCol) = Model.selectedPosition
                # Select a piece if none selected
                if((Model.selectedPiece == None) and 
                   (Model.gameBoard.pieces[row][col] != None)):
                    if(Model.currentPlayer == Model.gameBoard.pieces[row][col].color):
                        Model.selectedPiece = Controller.selectPiece(Model.gameBoard, row, col)
                        Controller.selectPieceModel(showBase)
                        legalMoves = Model.selectedPiece.getLegalMoves(Model.gameBoard, row, col)
                        refinedMoves = Controller.refineLegalMoves(Model.gameBoard, row, col, Model.selectedPiece, legalMoves)
                        Controller.highlightLegalMoves(Model.gameBoard, refinedMoves, showBase)
                
                #Piece is selected already
                elif(Model.selectedPiece != None):
                    legalMoves = Model.selectedPiece.getLegalMoves(Model.gameBoard, oldRow, oldCol)
                    refinedMoves = Controller.refineLegalMoves(Model.gameBoard, oldRow, oldCol, Model.selectedPiece, legalMoves)
                    # User click on selected piece, deselects it
                    if(Model.selectedPiece == Model.gameBoard.pieces[row][col]):
                        Controller.deselectPieceModel(showBase)
                        Controller.removeHighlightedMoves()
                        Model.selectedPiece = None
                        Model.selectedPosition = (-1,-1)

                    # User clicks on valid move area, selected piece moves there
                    elif((Model.selectedPiece != Model.gameBoard.pieces[row][col]) and 
                        ((row, col) in refinedMoves)):
                        Controller.placePiece(Model.gameBoard, oldRow, oldCol, row, col)
                        Controller.deselectPieceModel(showBase)
                        Controller.removeHighlightedMoves()
                        Model.selectedPiece.moveCount += 1
                        Model.selectedPiece = None
                        Model.selectedPosition = (-1,-1)
                        Controller.switchPlayer(showBase)
            
            # After each click, update piece models and check if gameover
            Controller.updatePieces(showBase)
            Controller.removeInCheckModels()
            Controller.updateInCheckModels(Model.gameBoard, showBase)
            Controller.checkGameOver(Model.gameBoard, showBase)

    game = ChineseChess112()
    game.run()
    
def testGame():
    print('Testing Game...')
    runGame()

testGame()
