#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This is an EXUDYN example
#
# Details:  A chain of 3D rigid bodies is simulated rigid bodies are connected via spring-dampers (no joints!)
#
# Author:   Johannes Gerstmayr
# Date:     2019-11-15
#
# Copyright:This file is part of Exudyn. Exudyn is free software. You can redistribute it and/or modify it under the terms of the Exudyn license. See 'LICENSE.txt' for more details.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import exudyn as exu
from exudyn.itemInterface import *
from exudyn.utilities import *

SC = exu.SystemContainer()
mbs = SC.AddSystem()

print('EXUDYN version='+exu.GetVersionString())

#background
#rect = [-0.1,-0.1,0.1,0.1] #xmin,ymin,xmax,ymax
#background0 = {'type':'Line', 'color':[0.1,0.1,0.8,1], 'data':[rect[0],rect[1],0, rect[2],rect[1],0, rect[2],rect[3],0, rect[0],rect[3],0, rect[0],rect[1],0]} #background
color = [0.1,0.1,0.8,1]
zz = 2*4 #max size
s = 0.1 #size of cube
sx = 3*s #x-size
cPosZ = 0.1 #offset of constraint in z-direction

#create background, in order to have according zoom all
background0 = GraphicsDataRectangle(-zz,-2*zz,zz,zz,color4white)
oGround=mbs.AddObject(ObjectGround(referencePosition= [0,0,0], 
                                   visualization=VObjectGround(graphicsData= [background0])))
mPosLast = mbs.AddMarker(MarkerBodyPosition(bodyNumber = oGround, 
                                            localPosition=[-2*sx,0,cPosZ]))

#create a chain of bodies:
for i in range(20):
    #print("Build Object", i)
    f = 0 #factor for initial velocities
    omega0 = [0,50.*f,20*f] #arbitrary initial angular velocity
    ep0 = eulerParameters0 #no rotation
    
    ep_t0 = AngularVelocity2EulerParameters_t(omega0, ep0)

    p0 = [-sx+i*2*sx,0.,0] #reference position
    v0 = [0.2*f,0.,0.] #initial translational velocity

    nRB = mbs.AddNode(NodeRigidBodyEP(referenceCoordinates=p0+ep0, 
                                      initialVelocities=v0+list(ep_t0)))
    #nRB = mbs.AddNode(NodeRigidBodyEP(referenceCoordinates=[0,0,0,1,0,0,0], initialVelocities=[0,0,0,0,0,0,0]))
    oGraphics = GraphicsDataOrthoCubeLines(-sx,-s,-s, sx,s,s, [0.8,0.1,0.1,1])
    oRB = mbs.AddObject(ObjectRigidBody(physicsMass=2, 
                                        physicsInertia=[6,1,6,0,0,0], 
                                        nodeNumber=nRB, 
                                        visualization=VObjectRigidBody(graphicsData=[oGraphics])))

    mMassRB = mbs.AddMarker(MarkerBodyMass(bodyNumber = oRB))
    mbs.AddLoad(Gravity(markerNumber = mMassRB, loadVector=[0.,-9.81,0.])) #gravity in negative z-direction

    #mCenterRB = mbs.AddMarker(MarkerBodyRigid(bodyNumber = oRB, localPosition = [0.,0.,0.]))
    #mbs.AddLoad(Torque(markerNumber = mCenterRB, loadVector=[0.,10000.,100000.])) #gravity in negative z-direction

    k = 1e7
    d=0.01*k
    mPos = mbs.AddMarker(MarkerBodyPosition(bodyNumber = oRB, localPosition = [-sx,0.,cPosZ]))
    mbs.AddObject(ObjectConnectorCartesianSpringDamper(markerNumbers = [mPosLast, mPos], 
                                                       stiffness=[k,k,k], damping=[d,d,d])) #gravity in negative z-direction
    mPosLast = mbs.AddMarker(MarkerBodyPosition(bodyNumber = oRB, localPosition = [sx,0.,cPosZ]))


mbs.Assemble()
print(mbs)

simulationSettings = exu.SimulationSettings() #takes currently set values or default values

fact = 10000
simulationSettings.timeIntegration.numberOfSteps = 1*fact
simulationSettings.timeIntegration.endTime = 0.001*fact*0.5
simulationSettings.solutionSettings.solutionWritePeriod = simulationSettings.timeIntegration.endTime/fact*10
simulationSettings.timeIntegration.verboseMode = 1

simulationSettings.timeIntegration.newton.useModifiedNewton = True
simulationSettings.timeIntegration.generalizedAlpha.useIndex2Constraints = False
simulationSettings.timeIntegration.generalizedAlpha.useNewmark = False
simulationSettings.timeIntegration.generalizedAlpha.spectralRadius = 0.6 #0.6 works well 

simulationSettings.solutionSettings.solutionInformation = "rigid body tests"
SC.visualizationSettings.nodes.defaultSize = 0.05

exu.StartRenderer()
mbs.WaitForUserToContinue()

exu.SolveDynamic(mbs, simulationSettings)

SC.WaitForRenderEngineStopFlag()
exu.StopRenderer() #safely close rendering window!
