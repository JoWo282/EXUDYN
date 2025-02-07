#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This is an EXUDYN example
#
# Details:  A chain of 3D rigid bodies connected with revolute and prismatic joints
#
# Author:   Johannes Gerstmayr
# Date:     2021-07-01
#
# Copyright:This file is part of Exudyn. Exudyn is free software. You can redistribute it and/or modify it under the terms of the Exudyn license. See 'LICENSE.txt' for more details.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
sys.path.append('../TestModels')            #for modelUnitTest as this example may be used also as a unit test

import exudyn as exu
from exudyn.itemInterface import *
from exudyn.utilities import *

from modelUnitTests import ExudynTestStructure, exudynTestGlobals

from math import sin, cos, pi
import numpy as np

SC = exu.SystemContainer()
mbs = SC.AddSystem()


#background
color = [0.1,0.1,0.8,1]
L = 0.4 #length of bodies
d = 0.1 #diameter of bodies

#create background, in order to have according zoom all
zz=2*L
#background0 = GraphicsDataRectangle(-zz,-zz,zz,zz,color4white)
oGround=mbs.AddObject(ObjectGround(referencePosition= [0,0,0])) #,visualization=VObjectGround(graphicsData= [background0])))
mPosLast = mbs.AddMarker(MarkerBodyRigid(bodyNumber = oGround, localPosition=[0,0,0]))
A0 = RotationMatrixX(0) 
Alast = A0 #previous marker

A0 = RotationMatrixX(0)
A1 = RotationMatrixY(0.5*pi)
A2 = RotationMatrixZ(0.5*pi)
A3 = RotationMatrixX(-0.5*pi)
A4 = RotationMatrixZ(0.5*pi)

Alist=[A0,A1,A2,A3,A4]

p0 = [0.,0.,0] #reference position
vLoc = np.array([L,0,0]) #last to next joint
#g = [0,0,-9.81]
g = [0,-9.81,0]

#create a chain of bodies:
for i in range(5):
    #print("Build Object", i)
    inertia = InertiaCuboid(density=1000, sideLengths=[L,d,d])
    #p0 += Alist[i] @ (0.5*vLoc)
    p0 += (0.5*vLoc)

    ep0 = eulerParameters0 #no rotation
    graphicsBody = GraphicsDataOrthoCubePoint([0,0,0], [L,d,d], color4steelblue)
    [nRB, oRB] = AddRigidBody(mbs, inertia, nodeType=exu.NodeType.RotationEulerParameters,
                              position=p0,
                              rotationMatrix=A0,
                              gravity=g,
                              graphicsDataList=[graphicsBody])

    mPos0 = mbs.AddMarker(MarkerBodyRigid(bodyNumber = oRB, localPosition = [-0.5*L,0,0]))
    mPos1 = mbs.AddMarker(MarkerBodyRigid(bodyNumber = oRB, localPosition = [ 0.5*L,0,0]))
    useGenericJoint = False #for comparison
    if True:
        if i != 2:
            if not useGenericJoint:
                mbs.AddObject(ObjectJointRevoluteZ(markerNumbers = [mPosLast, mPos0], 
                                                  rotationMarker0=Alist[i],
                                                  rotationMarker1=Alist[i],
                                                  visualization=VObjectJointRevoluteZ(axisRadius=0.5*d, axisLength=1.2*d)
                                                  )) 
            else: #compare to GenericJoint
                mbs.AddObject(ObjectJointGeneric(markerNumbers = [mPosLast, mPos0], 
                                                 constrainedAxes=[1,1,1,1,1,0],
                                                 rotationMarker0=Alist[i],
                                                 rotationMarker1=Alist[i],
                                                 visualization=VGenericJoint(axesRadius=0.5*d, axesLength=1.2*d)
                                                 )) 
        else:
            if not useGenericJoint:
                mbs.AddObject(ObjectJointPrismaticX(markerNumbers = [mPosLast, mPos0], 
                                                  rotationMarker0=Alist[i],
                                                  rotationMarker1=Alist[i],
                                                  visualization=VObjectJointPrismaticX(axisRadius=0.5*d, axisLength=1.2*d)
                                                  )) 
            else: #compare to GenericJoint
                mbs.AddObject(ObjectJointGeneric(markerNumbers = [mPosLast, mPos0], 
                                                 constrainedAxes=[0,1,1,1,1,1],
                                                 rotationMarker0=Alist[i],
                                                 rotationMarker1=Alist[i],
                                                 visualization=VGenericJoint(axesRadius=0.5*d, axesLength=1.2*d)
                                                 )) 
            #add spring, to limit motion in prismatic joint:
            k=500
            damp=k*0.02
            mbs.AddObject(CartesianSpringDamper(markerNumbers = [mPosLast, mPos0], 
                                       stiffness = [k]*3, damping = [damp]*3,
                                       visualization=VCartesianSpringDamper(show=False, drawSize=0.5*d)))
        
    mPosLast = mPos1
    
    # p0 += Alist[i] @ (0.5*vLoc)
    p0 += (0.5*vLoc)
    Alast = Alist[i]

mbs.AddLoad(LoadForceVector(markerNumber=mPosLast, loadVector=[0,0,20]))

mbs.Assemble()

simulationSettings = exu.SimulationSettings() #takes currently set values or default values

tEnd = 0.25
h=0.001  #use small step size to detext contact switching

simulationSettings.timeIntegration.numberOfSteps = int(tEnd/h)
simulationSettings.timeIntegration.endTime = tEnd
simulationSettings.solutionSettings.solutionWritePeriod = 0.001
simulationSettings.solutionSettings.sensorsWritePeriod = 0.01
#simulationSettings.timeIntegration.simulateInRealtime = True
#simulationSettings.timeIntegration.realtimeFactor = 0.1
simulationSettings.timeIntegration.verboseMode = 1

simulationSettings.timeIntegration.generalizedAlpha.spectralRadius = 0.8
simulationSettings.timeIntegration.generalizedAlpha.computeInitialAccelerations=True
simulationSettings.timeIntegration.newton.useModifiedNewton = True
#simulationSettings.timeIntegration.newton.modifiedNewtonJacUpdatePerStep = True 

SC.visualizationSettings.nodes.show = True
SC.visualizationSettings.nodes.drawNodesAsPoint  = False
SC.visualizationSettings.nodes.showBasis = True
SC.visualizationSettings.nodes.basisSize = 0.015
SC.visualizationSettings.connectors.showJointAxes = True
 
SC.visualizationSettings.general.autoFitScene = False #use loaded render state
#exudynTestGlobals.useGraphics = False
if exudynTestGlobals.useGraphics:
    simulationSettings.displayComputationTime = True
    simulationSettings.displayStatistics = True
    exu.StartRenderer()
    if 'renderState' in exu.sys:
        SC.SetRenderState(exu.sys[ 'renderState' ])
    #mbs.WaitForUserToContinue()
else:
    simulationSettings.solutionSettings.writeSolutionToFile = False

#exu.SolveDynamic(mbs, simulationSettings, solverType=exu.DynamicSolverType.TrapezoidalIndex2)
exu.SolveDynamic(mbs, simulationSettings, showHints=True)

if False: #use this to reload the solution and use SolutionViewer
    sol = LoadSolutionFile('coordinatesSolution.txt')
    from exudyn.interactive import SolutionViewer
    SolutionViewer(mbs, sol)


u0 = mbs.GetNodeOutput(nRB, exu.OutputVariableType.Displacement)
rot0 = mbs.GetNodeOutput(nRB, exu.OutputVariableType.Rotation)
exu.Print('u0=',u0,', rot0=', rot0)

result = (abs(u0)+abs(rot0)).sum()
exu.Print('solution of revoluteJointprismaticJointTest=',result)

exudynTestGlobals.testError = result - (1.2538806799246283) #2020-07-01: 1.2538806799246283
exudynTestGlobals.testResult = result



#%%+++++++++++++++++++++++++++++
if exudynTestGlobals.useGraphics:
    SC.WaitForRenderEngineStopFlag()
    exu.StopRenderer() #safely close rendering window!


