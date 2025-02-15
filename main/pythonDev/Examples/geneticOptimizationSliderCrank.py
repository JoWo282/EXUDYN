#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This is an EXUDYN example
#
# Details:  Slider crank model with verification in MATLAB for machine dynamics course
#           optionally, the slider crank is mounted on a floating frame, leading to vibrations
#           if the system is unbalanced
#           Use this example in combination with cmd: 'python resultsMonitor.py solution/geneticSliderCrank.txt'
#
# Author:   Johannes Gerstmayr
# Date:     2019-12-07 (created)
#           2021-01-10 (adapted for genetic optimization)
#
# Copyright:This file is part of Exudyn. Exudyn is free software. You can redistribute it and/or modify it under the terms of the Exudyn license. See 'LICENSE.txt' for more details.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import exudyn as exu
from exudyn.itemInterface import *
from exudyn.utilities import *
from exudyn.processing import GeneticOptimization, ParameterVariation, PlotOptimizationResults2D

import numpy as np #for postprocessing
import os
from time import sleep

useGraphics = False
L1=0.1
L2=0.3
m1=0.4
m2=0.2
m3=0.1
s1opt = -L1*(m2+m3)/m1 #-0.075
s2opt = -m3/m2*L2      #-0.15

#this is the function which is repeatedly called from ParameterVariation
#parameterSet contains dictinary with varied parameters
def ParameterFunction(parameterSet):

    s1=L1*0.5
    s2=L2*0.5
    if False:
        s1 = s1opt
        s2 = s2opt

    if 's1' in parameterSet:
        s1 = parameterSet['s1']
    h=0.002
    if 'h' in parameterSet:
        h = parameterSet['h']
    if 's2' in parameterSet:
        s2 = parameterSet['s2']

    iCalc = 'Ref' #needed for parallel computation ==> output files are different for every computation
    if 'computationIndex' in parameterSet:
        iCalc = str(parameterSet['computationIndex'])
        #print("computation index=",iCalc, flush=True)

    SC = exu.SystemContainer()
    mbs = SC.AddSystem()
    
    testCases = 1 #floating body
    nGround = mbs.AddNode(NodePointGround(referenceCoordinates=[0,0,0])) #ground node for coordinate constraint
    mGround = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber = nGround, coordinate=0)) #Ground node ==> no action
    
    
    #++++++++++++++++++++++++++++++++
    #floating body to mount slider-crank mechanism
    constrainGroundBody = (testCases == 0) #use this flag to fix ground body
    
    #graphics for floating frame:
    gFloating = GraphicsDataOrthoCube(-0.25, -0.25, -0.1, 0.8, 0.25, -0.05, color=[0.3,0.3,0.3,1.]) 
    
    if constrainGroundBody:
        floatingRB = mbs.AddObject(ObjectGround(referencePosition=[0,0,0], visualization=VObjectGround(graphicsData=[gFloating])))    
        mFloatingN = mbs.AddMarker(MarkerBodyPosition(bodyNumber = floatingRB, localPosition=[0,0,0]))
    else:
        nFloating = mbs.AddNode(Rigid2D(referenceCoordinates=[0,0,0], initialVelocities=[0,0,0]));
        mFloatingN = mbs.AddMarker(MarkerNodePosition(nodeNumber=nFloating))
        floatingRB = mbs.AddObject(RigidBody2D(physicsMass=2, physicsInertia=1, nodeNumber=nFloating, visualization=VObjectRigidBody2D(graphicsData=[gFloating])))
        mRB0 = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber = nFloating, coordinate=0))
        mRB1 = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber = nFloating, coordinate=1))
        mRB2 = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber = nFloating, coordinate=2))

        #add spring dampers for reference frame:        
        k=5000 #stiffness of floating body
        d=k*0.01
        mbs.AddObject(CoordinateSpringDamper(markerNumbers=[mGround,mRB0], stiffness=k, damping=d))
        mbs.AddObject(CoordinateSpringDamper(markerNumbers=[mGround,mRB1], stiffness=k, damping=d))
        mbs.AddObject(CoordinateSpringDamper(markerNumbers=[mGround,mRB2], stiffness=k, damping=d))
        mbs.AddObject(CoordinateConstraint(markerNumbers=[mGround,mRB2]))
    
    
    
    #++++++++++++++++++++++++++++++++
    #nodes and bodies
    omega=2*pi/60*300 #3000 rpm
    M=0.1 #torque (default: 0.1)

    s1L=-s1
    s1R=L1-s1
    s2L=-s2
    s2R=L2-s2
    
    #lambda=L1/L2
    J1=(m1/12.)*L1**2 #inertia w.r.t. center of mass
    J2=(m2/12.)*L2**2 #inertia w.r.t. center of mass
    
    ty = 0.05    #thickness
    tz = 0.05    #thickness

    graphics1 = GraphicsDataRigidLink(p0=[s1L,0,-0.5*tz],p1=[s1R,0,-0.5*tz], 
                                      axis0=[0,0,1], axis1=[0,0,1],radius=[0.5*ty,0.5*ty],
                                      thickness=0.8*ty, width=[tz,tz], color=color4steelblue,nTiles=16)
    
    graphics2 = GraphicsDataRigidLink(p0=[s2L,0,0.5*tz],p1=[s2R,0,0.5*tz], 
                                      axis0=[0,0,1], axis1=[0,0,1],radius=[0.5*ty,0.5*ty],
                                      thickness=0.8*ty, width=[tz,tz], color=color4lightred,nTiles=16)
    
    #crank:
    nRigid1 = mbs.AddNode(Rigid2D(referenceCoordinates=[s1,0,0], 
                                  initialVelocities=[0,0,0]));
    oRigid1 = mbs.AddObject(RigidBody2D(physicsMass=m1, 
                                        physicsInertia=J1,
                                        nodeNumber=nRigid1,
                                        visualization=VObjectRigidBody2D(graphicsData= [graphics1])))
    
    #connecting rod:
    nRigid2 = mbs.AddNode(Rigid2D(referenceCoordinates=[L1+s2,0,0], 
                                  initialVelocities=[0,0,0]));
    oRigid2 = mbs.AddObject(RigidBody2D(physicsMass=m2, 
                                        physicsInertia=J2,
                                        nodeNumber=nRigid2,
                                        visualization=VObjectRigidBody2D(graphicsData= [graphics2])))
    
    
    #++++++++++++++++++++++++++++++++
    #slider:
    c=0.025 #dimension of mass
    graphics3 = GraphicsDataOrthoCube(-c,-c,-c*2,c,c,0,color4grey)
    
    #nMass = mbs.AddNode(Point2D(referenceCoordinates=[L1+L2,0]))
    #oMass = mbs.AddObject(MassPoint2D(physicsMass=m3, nodeNumber=nMass,visualization=VObjectMassPoint2D(graphicsData= [graphics3])))
    nMass = mbs.AddNode(Rigid2D(referenceCoordinates=[L1+L2,0,0]))
    oMass = mbs.AddObject(RigidBody2D(physicsMass=m3, physicsInertia=0.001*m3, nodeNumber=nMass,visualization=VObjectRigidBody2D(graphicsData= [graphics3])))
    
    #++++++++++++++++++++++++++++++++
    #markers for joints:
    mR1Left = mbs.AddMarker(MarkerBodyRigid(bodyNumber=oRigid1, localPosition=    [s1L,0.,0.])) #support point # MUST be a rigidBodyMarker, because a torque is applied
    mR1Right = mbs.AddMarker(MarkerBodyPosition(bodyNumber=oRigid1, localPosition=[s1R,0.,0.])) #end point; connection to connecting rod
    
    mR2Left = mbs.AddMarker(MarkerBodyPosition(bodyNumber=oRigid2, localPosition= [s2L,0.,0.])) #connection to crank
    mR2Right = mbs.AddMarker(MarkerBodyPosition(bodyNumber=oRigid2, localPosition=[s2R,0.,0.])) #end point; connection to slider
    
    mMass = mbs.AddMarker(MarkerBodyPosition(bodyNumber=oMass, localPosition=[ 0.,0.,0.]))
    mG0 = mFloatingN
    
    #++++++++++++++++++++++++++++++++
    #joints:
    mbs.AddObject(RevoluteJoint2D(markerNumbers=[mG0,mR1Left]))
    mbs.AddObject(RevoluteJoint2D(markerNumbers=[mR1Right,mR2Left]))
    mbs.AddObject(RevoluteJoint2D(markerNumbers=[mR2Right,mMass]))
        
    
    #prismatic joint:
    mRigidGround = mbs.AddMarker(MarkerBodyRigid(bodyNumber = floatingRB, localPosition = [L1+L2,0,0]))
    mRigidSlider = mbs.AddMarker(MarkerBodyRigid(bodyNumber = oMass, localPosition = [0,0,0]))
    
    mbs.AddObject(PrismaticJoint2D(markerNumbers=[mRigidGround,mRigidSlider], constrainRotation=True))
    
    
    #user function for load; switch off load after 1 second
    userLoadOn = True
    def userLoad(mbs, t, load):
        setLoad = 0
        if userLoadOn:
            setLoad = load
            omega = mbs.GetNodeOutput(nRigid1,variableType = exu.OutputVariableType.AngularVelocity)[2]
            if omega > 2*pi*2:
                #print("t=",t)
                userLoadOn = False
        return setLoad
    
    #loads and driving forces:
    mRigid1CoordinateTheta = mbs.AddMarker(MarkerNodeCoordinate(nodeNumber = nRigid1, coordinate=2)) #angle coordinate is constrained
    #mbs.AddLoad(LoadCoordinate(markerNumber=mRigid1CoordinateTheta, load = M, loadUserFunction=userLoad)) #torque at crank
    mbs.AddLoad(LoadCoordinate(markerNumber=mRigid1CoordinateTheta, load = M)) #torque at crank

    #write motion of support frame:    
    sensorFileName = 'solution/floatingPos'+iCalc+'.txt'
    sFloating = mbs.AddSensor(SensorNode(nodeNumber=nFloating, fileName=sensorFileName, 
                             outputVariableType=exu.OutputVariableType.Position))
    
    #++++++++++++++++++++++++++++++++
    #assemble, adjust settings and start time integration
    mbs.Assemble()
    
    simulationSettings = exu.SimulationSettings() #takes currently set values or default values
    tEnd = 3
    
    simulationSettings.timeIntegration.numberOfSteps = int(tEnd/h) 
    simulationSettings.timeIntegration.endTime = tEnd              

    #simulationSettings.timeIntegration.newton.relativeTolerance = 1e-8 #10000
    #simulationSettings.timeIntegration.verboseMode = 1 #10000
    
    simulationSettings.solutionSettings.solutionWritePeriod = 2e-3
    simulationSettings.solutionSettings.writeSolutionToFile = useGraphics

    simulationSettings.timeIntegration.newton.useModifiedNewton = True
    simulationSettings.timeIntegration.newton.relativeTolerance = 1e-8
    simulationSettings.timeIntegration.newton.absoluteTolerance = 1e-8
    
    #++++++++++++++++++++++++++++++++++++++++++
    #solve index 2 / trapezoidal rule:
    simulationSettings.timeIntegration.generalizedAlpha.useNewmark = True
    simulationSettings.timeIntegration.generalizedAlpha.useIndex2Constraints = True
    
    dSize = 0.02
    SC.visualizationSettings.nodes.defaultSize = dSize
    SC.visualizationSettings.markers.defaultSize = dSize
    SC.visualizationSettings.bodies.defaultSize = [dSize, dSize, dSize]
    SC.visualizationSettings.connectors.defaultSize = dSize
    
    #data obtained from SC.GetRenderState(); use np.round(d['modelRotation'],4)
    SC.visualizationSettings.openGL.initialModelRotation = [[ 0.87758,  0.04786, -0.47703],
                                                            [ 0.     ,  0.995  ,  0.09983],
                                                            [ 0.47943, -0.08761,  0.8732]]
    SC.visualizationSettings.openGL.initialZoom = 0.47
    SC.visualizationSettings.openGL.initialCenterPoint = [0.192, -0.0039,-0.075]
    SC.visualizationSettings.openGL.initialMaxSceneSize = 0.4
    SC.visualizationSettings.general.autoFitScene = False
    #mbs.WaitForUserToContinue()
    
    if useGraphics: 
        exu.StartRenderer()
   
    exu.SolveDynamic(mbs, simulationSettings)
        
    if useGraphics: 
        #+++++++++++++++++++++++++++++++++++++
        #animate solution
#        mbs.WaitForUserToContinue
#        fileName = 'coordinatesSolution.txt'
#        solution = LoadSolutionFile('coordinatesSolution.txt')
#        AnimateSolution(mbs, solution, 10, 0.025, True)
        #+++++++++++++++++++++++++++++++++++++

        SC.WaitForRenderEngineStopFlag()
        exu.StopRenderer() #safely close rendering window!
    
    #++++++++++++++++++++++++++++++++++++++++++
    #evaluate error:
    data = np.loadtxt(sensorFileName, comments='#', delimiter=',')

    errorNorm = max(abs(data[:,1])) + max(abs(data[:,2])) #max displacement in x and y direction

    #++++++++++++++++++++++++++++++++++++++++++
    #clean up optimization
    if True: #delete files; does not work for parallel, consecutive operation
        if iCalc != 'Ref':
            os.remove(sensorFileName) #remove files in order to clean up
            while(os.path.exists(sensorFileName)): #wait until file is really deleted -> usually some delay
                sleep(0.001) #not nice, but there is no other way than that
        
    if useGraphics:
        print("max. oszillation=", errorNorm)
        from exudyn.plot import PlotSensor
        
        PlotSensor(mbs, sensorNumbers=[sFloating,sFloating], components=[0,1])

    del mbs
    del SC
    
    return errorNorm
    #++++++++++++++++++++++++++++++++++++++++++

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

doOptimize = True
#now perform parameter variation
if __name__ == '__main__': #include this to enable parallel processing
    if doOptimize:
        import time
    
        #%%++++++++++++++++++++++++++++++++++++++++++++++++++++
        #GeneticOptimization    
        start_time = time.time()
        [pOpt, vOpt, pList, values] = GeneticOptimization(objectiveFunction = ParameterFunction, 
                                             parameters = {'s1':(-L1,L1), 's2':(-L2,L2)}, #parameters provide search range
                                             numberOfGenerations = 30,
                                             populationSize = 50,
                                             elitistRatio = 0.1,
                                             crossoverProbability = 0.1,
                                             rangeReductionFactor = 0.5,
                                             addComputationIndex=True,
                                             randomizerInitialization=0, #for reproducible results
                                             #distanceFactor = 0.1, #for this example only one significant minimum
                                             debugMode=False,
                                             useMultiProcessing=True, #may be problematic for test
                                             showProgress=True,
                                             resultsFile = 'solution/geneticSliderCrank.txt',
                                             )
        #exu.Print("--- %s seconds ---" % (time.time() - start_time))
    
        exu.Print("[pOpt, vOpt]=", [pOpt, vOpt])
        u = vOpt
        exu.Print("optimum=",u)
    
        if False:
            # from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
            import matplotlib.pyplot as plt
    
            plt.close('all')
            [figList, axList] = PlotOptimizationResults2D(pList, values, yLogScale=True)
    else:
        useGraphics = True
        parameterSet = {'s1':L1*0.5, 's2':L2*0.5, 'h':1e-5}
        #parameterSet = {'s1':-0.075, 's2':-0.15, 'h':1e-5}
        ParameterFunction(parameterSet)    





if False:
    dataIndex2 = np.loadtxt('coordinatesSolution.txt', comments='#', delimiter=',')
    #dataMatlab = np.loadtxt('slidercrankRefSolM0.1_tol1e-4.txt', comments='#', delimiter=',') #this is quite inaccurate
    dataMatlab2 = np.loadtxt('slidercrankRefSolM0.1_tol1e-6.txt', comments='#', delimiter=',')
                            
    vODE2=mbs.systemData.GetODE2Coordinates()
    nODE2=len(vODE2) #number of ODE2 coordinates

    nAngle = mbs.systemData.GetObjectLTGODE2(oRigid1)[2] #get coordinate index of angle
    plt.plot(dataIndex2[:,0], dataIndex2[:,1+nAngle], 'b-') #plot angle of crank;
    plt.plot(dataIndex2[:,0], dataIndex2[:,1+nODE2+nAngle], 'r-') #plot angular velocity of crank
    #plt.plot(dataMatlab[:,0], dataMatlab[:,2], 'g-') #plot angular velocity of crank from MATLAB
    plt.plot(dataMatlab2[:,0], dataMatlab2[:,2], 'k-') #plot angular velocity of crank from MATLAB
    
    #plt.plot(dataIndex3[:,0], dataIndex3[:,1+globalIndex], 'b-') #plot x-coordinate of slider
    
    ax=plt.gca() # get current axes
    ax.grid(True, 'major', 'both')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(10)) #use maximum of 8 ticks on y-axis
    ax.yaxis.set_major_locator(ticker.MaxNLocator(10)) #use maximum of 8 ticks on y-axis
    plt.tight_layout()
    plt.show() 
    
