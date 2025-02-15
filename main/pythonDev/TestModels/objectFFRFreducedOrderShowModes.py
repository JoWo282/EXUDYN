#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This is an EXUDYN example
#
# Details:  Test for ObjectFFRFreducedOrder with python user function for reduced order equations of motion
#
# Author:   Johannes Gerstmayr 
# Date:     2020-05-13
#
# Copyright:This file is part of Exudyn. Exudyn is free software. You can redistribute it and/or modify it under the terms of the Exudyn license. See 'LICENSE.txt' for more details.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++import sys

import exudyn as exu
from exudyn.itemInterface import *
from exudyn.utilities import *
from exudyn.FEM import *
from exudyn.graphicsDataUtilities import *
from exudyn.interactive import AnimateModes

SC = exu.SystemContainer()
mbs = SC.AddSystem()

import numpy as np





#%%+++++++++++++++++++++++++++++++++++++++++++++++++++++
#Use FEMinterface to import FEM model and create FFRFreducedOrder object
fem = FEMinterface()
inputFileName = 'testData/rotorDiscTest' #runTestSuite.py is at another directory
#if exudynTestGlobals.useGraphics:
#    inputFileName = 'testData/rotorDiscTest'        #if executed in current directory

nodes=fem.ImportFromAbaqusInputFile(inputFileName+'.inp', typeName='Instance', name='rotor-1')

fem.ReadMassMatrixFromAbaqus(inputFileName+'MASS1.mtx')
fem.ReadStiffnessMatrixFromAbaqus(inputFileName+'STIF1.mtx')
fem.ScaleStiffnessMatrix(1e-2) #for larger deformations, stiffness is reduced to 1%

#nodeNumberUnbalance = 9  #on disc, max y-value
nodeNumberUnbalance = fem.GetNodeAtPoint(point=[0. , 0.19598444, 0.15])
#exu.Print("nodeNumberUnbalance =",nodeNumberUnbalance)
unbalance = 0.1
fem.AddNodeMass(nodeNumberUnbalance, unbalance)
#print(fem.GetMassMatrix()[8*3:11*3,:])

nModes = 8
fem.ComputeEigenmodes(nModes, excludeRigidBodyModes = 6, useSparseSolver = True)
#print("eigen freq.=", fem.GetEigenFrequenciesHz())

cms = ObjectFFRFreducedOrderInterface(fem)

objFFRF = cms.AddObjectFFRFreducedOrderWithUserFunctions(exu, mbs, positionRef=[0,0,0], eulerParametersRef=eulerParameters0, 
                                              initialVelocity=[0,0,0], initialAngularVelocity=[0,0,50*2*pi],
                                              color=[0.1,0.9,0.1,1.])

mbs.Assemble()

    
#%%+++++++++++++++++++++++++++++++++++++++
#some settings, advantages for showing modes:

SC.visualizationSettings.nodes.show = False
SC.visualizationSettings.bodies.deformationScaleFactor = 1 #use this factor to scale the deformation of modes

SC.visualizationSettings.openGL.showFaceEdges = True
SC.visualizationSettings.openGL.multiSampling=4
SC.visualizationSettings.window.renderWindowSize = [1600,1080]
# SC.visualizationSettings.contour.outputVariable = exu.OutputVariableType.DisplacementLocal
# SC.visualizationSettings.contour.outputVariableComponent = 0 #component


#%%+++++++++++++++++++++++++++++++++++++++
#animate modes of ObjectFFRFreducedOrder (only needs generic node containing modal coordinates)
SC.visualizationSettings.general.autoFitScene = False #otherwise, model may be difficult to be moved

nodeNumber = objFFRF['nGenericODE2'] #this is the node with the generalized coordinates
AnimateModes(SC, mbs, nodeNumber)
    


