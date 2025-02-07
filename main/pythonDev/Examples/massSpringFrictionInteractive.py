#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This is an EXUDYN example
#
# Details:  Example with 1D spring-mass-damper and friction system
#
# Author:   Johannes Gerstmayr
# Date:     2020-01-10
#
# Copyright:This file is part of Exudyn. Exudyn is free software. You can redistribute it and/or modify it under the terms of the Exudyn license. See 'LICENSE.txt' for more details.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#import sys
#sys.path.append('C:/DATA/cpp/EXUDYN_git/main/bin/WorkingRelease') #for exudyn, itemInterface and exudynUtilities

import exudyn as exu
from exudyn.utilities import *
from exudyn.itemInterface import *
from exudyn.interactive import InteractiveDialog
from exudyn.physics import StribeckFunction, RegularizedFriction

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from math import exp, sqrt
from numpy import sign


#draw friction curve vs. velocity
if True:
    n= 200
    x = np.linspace(-1,1,n)
    y = np.zeros(n)
    for i in range(n):
        y[i] = StribeckFunction(x[i], muDynamic=0.1, muStaticOffset=0.05, expVel=0.1)
    
    plt.close('all')
    plt.plot(x,y,'b-')
    
    for i in range(n):
        y[i] = RegularizedFriction(x[i], muDynamic=0.1, muStaticOffset=0.05, velStatic=0.05, velDynamic=0.8)
    
    plt.plot(x,y,'r-')


#%%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
plt.rcParams.update({'font.size': 14})

SC = exu.SystemContainer()
mbs = SC.AddSystem()

print('EXUDYN version='+exu.__version__)

caseName = "movingBand"
#dRel = 0.05 #relative damping

dRel = 0.002
tt=0.05

#parameters of mass-spring with friction
#self-excitation works with (stick-slip); must have enough initial velocity ..., if started from zero, does not work: 
#param = [1, 10, 400]
param = [4, 40, 400]   #works with dRel up to 0.016
#param = [1, 40, 400]  #works with dRel up to 0.103

#param = [0.2, 8, 400] #very slow oscillation
vBand = param[0]
fFriction = param[1] #force in Newton, only depends on direction of velocity
stiffness = param[2]

L=0.5
mass = 0.5
omega0 = sqrt(stiffness/mass)
damping = 2 * dRel * omega0 
u0 = 0 #initial displacement
v0 = 0 #initial velocity

    
f = 80
x0 = f/stiffness

#graphics:
lBand = 200*L
w = L*0.5
z=-tt
gBackground = [GraphicsDataQuad([[-lBand,-w,z],[ L,-w,z],[ L, w,z],[-lBand, w,z]], 
                              color=color4lightgrey, alternatingColor=color4grey,
                              nTiles=200, nTilesY=6)]

#node for mass point:
nMass=mbs.AddNode(Point(referenceCoordinates = [L,0,0], initialCoordinates = [u0,0,0], 
                     initialVelocities= [v0,0,0]))

#add mass points and ground object:
gCube = GraphicsDataOrthoCube(-tt, -tt, -tt, tt, tt, tt, color4steelblue)
massPoint = mbs.AddObject(MassPoint(physicsMass = mass, nodeNumber = nMass, 
                                    visualization=VObjectMassPoint(graphicsData=[gCube])))

#marker for constraint / springDamper
nGround=mbs.AddNode(NodePointGround(referenceCoordinates = [0,0,0]))
groundCoordinateMarker = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= nGround, coordinate = 0))

mbs.variables['bandVelocity'] = vBand
mbs.variables['relDamping'] = dRel
mbs.variables['dynamicFriction'] = fFriction
mbs.variables['staticFrictionOffset'] = fFriction
mbs.variables['stiffness'] = stiffness
def UFbandVelocity(mbs, t, itemIndex, lOffset):
    return mbs.variables['bandVelocity']

bandCoordinateMarker = 0
if vBand == 0:
    #ground
    objectGround = mbs.AddObject(ObjectGround(referencePosition = [0,0,0], 
                                              visualization=VObjectGround(graphicsData=gBackground)))
    bandCoordinateMarker = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= nGround, coordinate = 0))
else:
    #moving bar:
    n0=mbs.AddNode(Point(referenceCoordinates = [0,0,0], initialCoordinates = [0,0,0], 
                         initialVelocities= [vBand,0,0]))
    bandCoordinateMarker = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= n0, coordinate = 0))
    mbs.AddObject(MassPoint(physicsMass = mass, nodeNumber = n0, 
                            visualization=VObjectMassPoint(graphicsData=gBackground)))
    #mbs.AddLoad(LoadCoordinate(markerNumber=bandCoordinateMarker, load=1e5))
    mbs.AddObject(CoordinateConstraint(markerNumbers=[groundCoordinateMarker, bandCoordinateMarker], velocityLevel=True, 
                                       offsetUserFunction_t=UFbandVelocity,
                                       visualization=VCoordinateConstraint(show=False)))

nodeCoordinateMarker0  = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= nMass, coordinate = 0))
nodeCoordinateMarker1  = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= nMass, coordinate = 1))
nodeCoordinateMarker2  = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber= nMass, coordinate = 2))

#Spring-Dampers
#add static/dynamic friction with userfunction
useStaticFriction = True
if useStaticFriction:
    reg = 1e-4
    def UFspring(mbs, t, u, v, k, d, offset, frictionForce, frictionProportionalZone):
        return RegularizedFriction(vel=v, 
                                muDynamic=mbs.variables['dynamicFriction'], muStaticOffset=mbs.variables['staticFrictionOffset'], 
                                velStatic=frictionProportionalZone, velDynamic=k, muViscous=0)
    
    mbs.variables['oFriction'] = mbs.AddObject(CoordinateSpringDamper(markerNumbers = [bandCoordinateMarker, nodeCoordinateMarker0], 
                                         stiffness = 4*reg,                 #velDynamic
                                         damping = 0,                       #viscous term
                                         offset = fFriction,                #muStaticOffset
                                         dryFriction=fFriction,             #muDynamic
                                         dryFrictionProportionalZone=reg,   #velStatic
                                         springForceUserFunction = UFspring,
                                         visualization=VObjectConnectorCoordinateSpringDamper(show=False))) 
else:
    mbs.variables['oFriction'] = mbs.AddObject(CoordinateSpringDamper(markerNumbers = [bandCoordinateMarker, nodeCoordinateMarker0], 
                                         stiffness = 0, damping = 0, dryFriction=fFriction, 
                                         dryFrictionProportionalZone=1e-5, #offset must be zero, because coordinates just represent the displacements
                                         visualization=VObjectConnectorCoordinateSpringDamper(show=False))) 

mbs.variables['oSpring'] = mbs.AddObject(CoordinateSpringDamper(markerNumbers = [groundCoordinateMarker, nodeCoordinateMarker0], 
                                                                  stiffness = stiffness, damping = 0)) #damping added to user function

mbs.AddObject(CoordinateSpringDamper(markerNumbers = [groundCoordinateMarker, nodeCoordinateMarker1], stiffness = 4000, 
                                     visualization=VObjectConnectorCoordinateSpringDamper(show=False))) 
mbs.AddObject(CoordinateSpringDamper(markerNumbers = [groundCoordinateMarker, nodeCoordinateMarker2], stiffness = 4000,
                                     visualization=VObjectConnectorCoordinateSpringDamper(show=False))) 


#add loads:
mbs.AddLoad(LoadCoordinate(markerNumber = nodeCoordinateMarker0, load = f))

sensPos = mbs.AddSensor(SensorNode(nodeNumber=nMass, fileName='solution/nonlinearPos.txt',
                                   outputVariableType=exu.OutputVariableType.Displacement))
sensVel = mbs.AddSensor(SensorNode(nodeNumber=nMass, fileName='solution/nonlinearVel.txt',
                                   outputVariableType=exu.OutputVariableType.Velocity))


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
#print(mbs)
mbs.Assemble()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++

simulationSettings = exu.SimulationSettings()

simulationSettings.solutionSettings.solutionWritePeriod = 1e-1
simulationSettings.solutionSettings.solutionInformation = "Mass-spring-damper:"+caseName

simulationSettings.timeIntegration.generalizedAlpha.spectralRadius = 1 #SHOULD work with 0.9 as well
#simulationSettings.timeIntegration.simulateInRealtime = True
#simulationSettings.timeIntegration.realtimeFactor = 0.2

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
#data obtained from SC.GetRenderState(); use np.round(d['modelRotation'],4)
# SC.visualizationSettings.openGL.initialModelRotation = [[ 0.33  ,  0.0882, -0.9399],
#                                                        [ 0.0819,  0.9892,  0.1216],
#                                                        [ 0.9404, -0.1171,  0.3192]]
SC.visualizationSettings.openGL.initialZoom = 0.5#0.28
SC.visualizationSettings.openGL.initialCenterPoint = [0.297, 0.000318, 0.0]
SC.visualizationSettings.openGL.initialMaxSceneSize = 0.5
SC.visualizationSettings.general.autoFitScene = False
SC.visualizationSettings.general.textSize = 12
SC.visualizationSettings.general.showSolverInformation = 12
SC.visualizationSettings.general.graphicsUpdateInterval = 0.02
SC.visualizationSettings.window.renderWindowSize=[1200,1000]
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
exu.StartRenderer()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++



SC.visualizationSettings.general.autoFitScene = False #otherwise, renderState not accepted for zoom

#time.sleep(0.5) #allow window to adjust view

h = 2e-5      #step size of solver
deltaT = 0.01 #time period to be simulated between every update

#++++++++++++++++++++++++++++
#define items for dialog
dialogItems = [{'type':'label', 'text':'Friction oscillator', 'grid':(0,0,2), 'options':['L']}, 
               #{'type':'radio', 'textValueList':[('linear',0),('nonlinear (f=k*u+1000*k*u**3+d*v)',1)], 'value':0, 'variable':'mode', 'grid': [(2,0),(2,1)]},
               {'type':'label', 'text':'band velocity:', 'grid':(1,0)},
               {'type':'slider', 'range': (0, 20), 'value':mbs.variables['bandVelocity'], 'steps':400, 'variable':'bandVelocity', 'grid':(1,1)},
               {'type':'label', 'text':'dynamic friction force:', 'grid':(2,0)},
               {'type':'slider', 'range': (0, 100), 'value':mbs.variables['dynamicFriction'], 'steps':400, 'variable':'dynamicFriction', 'grid':(2,1)},
               {'type':'label', 'text':'static friction offset:', 'grid':(3,0)},
               {'type':'slider', 'range': (0, 100), 'value':mbs.variables['staticFrictionOffset'], 'steps':400, 'variable':'staticFrictionOffset', 'grid':(3,1)},
               {'type':'label', 'text':'stiffness:', 'grid':(4,0)},
               {'type':'slider', 'range':(0, 2000), 'value':mbs.variables['stiffness'], 'steps':400, 'variable':'stiffness', 'grid':(4,1)},
               {'type':'label', 'text':'relative damping:', 'grid':(5,0)},
               {'type':'slider', 'range':(0, 0.4), 'value':mbs.variables['relDamping'], 'steps':400, 'variable':'relDamping', 'grid':(5,1)}]

#++++++++++++++++++++++++++++++++++++++++
#specify subplots to be shown interactively
plt.close('all')

plots={'fontSize':16,'sizeInches':(12,12),'nPoints':200, 
       'subplots':(3,1), 'sensors':[[(sensPos,0),(sensPos,1),'time','mass position'], 
                                    [(sensVel,0),(sensVel,1),'time','mass velocity'], 
                                    [(sensPos,1),(sensVel,1),'position (phase space)','velocity (phase space)']
                                    ],
       'limitsX':[(),(),()], #omit if time auto-range
       #'limitsY':[(-0.05,0.05),()]}
       'limitsY':[(),(),()]}

#++++++++++++++++++++++++++++++++++++++++
#setup simulation settings and run interactive dialog:
simulationSettings = exu.SimulationSettings()
simulationSettings.timeIntegration.generalizedAlpha.spectralRadius = 1
simulationSettings.solutionSettings.writeSolutionToFile = False
simulationSettings.solutionSettings.solutionWritePeriod = 0.1 #data not used
simulationSettings.solutionSettings.sensorsWritePeriod = 0.1 #data not used
simulationSettings.solutionSettings.solutionInformation = 'Nonlinear oscillations: compare linear / nonlinear case'
simulationSettings.timeIntegration.verboseMode = 0 #turn off, because of lots of output

simulationSettings.timeIntegration.numberOfSteps = int(deltaT/h)
simulationSettings.timeIntegration.endTime = deltaT

#this is an exemplariy simulation function, which adjusts some values for simulation
def SimulationUF(mbs, dialog):
    mbs.SetObjectParameter(mbs.variables['oFriction'],'dryFriction',mbs.variables['dynamicFriction'])
    mbs.SetObjectParameter(mbs.variables['oSpring'],'stiffness',mbs.variables['stiffness'])
    mbs.SetObjectParameter(mbs.variables['oSpring'],'damping',2*mbs.variables['relDamping']*omega0)


dialog = InteractiveDialog(mbs=mbs, simulationSettings=simulationSettings,
                           simulationFunction=SimulationUF, 
                           title='Interactive window',
                           dialogItems=dialogItems, period=deltaT, realtimeFactor=10,
                           plots=plots, fontSize=12)

# #stop solver and close render window
exu.StopRenderer() #safely close rendering window!


