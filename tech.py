from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode, Mat4
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from direct.actor.Actor import Actor
import sys

import math
from direct.task.Task import Task
import sys

def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())
 
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
    

        
        self.scene = self.loader.loadModel("models/environment")
        
        # Any model must be parented to the self.render 'tree' to render
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.1, 0.1, 0.1)
        self.scene.setPos(-8, 42, 0)

        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)




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
            self.pandaActor.setPos(PointAtZ(.5, nearPoint, nearVec))
    

    def keyHandler(self,key):
        if(key == "arrow_left"):
            x,y,z = self.pandaActor.getPos()
            x -= 2
            self.pandaActor.setPos(x, y, z)
        elif(key == "arrow_right"):
            x,y,z = self.pandaActor.getPos()
            x += 2
            self.pandaActor.setPos(x, y, z)
        elif(key == "arrow_up"):
            x,y,z = self.pandaActor.getPos()
            y += 2
            self.pandaActor.setPos(x, y, z)
        elif(key == "arrow_down"):
            x,y,z = self.pandaActor.getPos()
            y -= 2
            self.pandaActor.setPos(x, y, z)
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