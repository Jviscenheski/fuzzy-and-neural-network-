import vrep
import sys
import numpy as np
import math
import time
import skfuzzy as fuzz
import skfuzzy.control as ctrl

import pdb

PI = math.pi

vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

if clientID != -1:
  print('Connected to remote API server')
else:
  sys.exit('Could not connect')

returnCode, KJuniorHandle      = vrep.simxGetObjectHandle(clientID, 'KJunior',            vrep.simx_opmode_oneshot_wait)
returnCode, KJuniorLeftHandle  = vrep.simxGetObjectHandle(clientID, 'KJunior_motorLeft',  vrep.simx_opmode_oneshot_wait)
returnCode, KJuniorRightHandle = vrep.simxGetObjectHandle(clientID, 'KJunior_motorRight', vrep.simx_opmode_oneshot_wait)

returnCode, LaptopHandle        = vrep.simxGetObjectHandle(clientID, 'laptop',              vrep.simx_opmode_oneshot_wait)

centerLeftSensor = ctrl.Antecedent(np.arange(0, 2000, 1),   'centerLeftSensor')
centerRightSensor = ctrl.Antecedent(np.arange(0, 2000, 1),   'centerRightSensor')
leftSensor   = ctrl.Antecedent(np.arange(0, 2000, 1),   'leftSensor')
rightSensor  = ctrl.Antecedent(np.arange(0, 2000, 1),   'rightSensor')
orientation  = ctrl.Antecedent(np.arange(-181, 181, 0.1), 'orientation')
leftWheelVel     = ctrl.Consequent(np.arange(-5, 5, 0.1),     'leftWheelVel')
rightWheelVel     = ctrl.Consequent(np.arange(-5, 5, 0.1),     'rightWheelVel')

centerLeftSensor['no-signal']   = fuzz.trapmf(centerLeftSensor.universe, [0, 0, 1, 1])
centerLeftSensor['far']         = fuzz.trapmf(centerLeftSensor.universe, [1, 2, 900, 1000])
centerLeftSensor['near']        = fuzz.trapmf(centerLeftSensor.universe, [900, 1000, 2000, 2000])

centerRightSensor['no-signal']   = fuzz.trapmf(centerRightSensor.universe, [0, 0, 1, 1])
centerRightSensor['far']         = fuzz.trapmf(centerRightSensor.universe, [1, 2, 900, 1000])
centerRightSensor['near']        = fuzz.trapmf(centerRightSensor.universe, [900, 1000, 2000, 2000])

leftSensor['no-signal']   = fuzz.trapmf(leftSensor.universe, [0, 0, 1, 1])
leftSensor['far']         = fuzz.trapmf(leftSensor.universe, [1, 2, 900, 1000])
leftSensor['near']        = fuzz.trapmf(leftSensor.universe, [900, 1000, 2000, 2000])

rightSensor['no-signal']   = fuzz.trapmf(rightSensor.universe, [0, 0, 1, 1])
rightSensor['far']         = fuzz.trapmf(rightSensor.universe, [1, 2, 900, 1000])
rightSensor['near']        = fuzz.trapmf(rightSensor.universe, [900, 1000, 2000, 2000])

orientation['left']       = fuzz.trimf( orientation.universe, [-181, -40, 0])
orientation['center']     = fuzz.trapmf(orientation.universe, [-60, -20, 20, 60])
orientation['right']      = fuzz.trimf( orientation.universe, [0, 40, 181])

leftWheelVel['fastReverse']   = fuzz.trapmf(leftWheelVel.universe, [-5,     -5, -3.5,   -1])
leftWheelVel['slowReverse']   = fuzz.trapmf(leftWheelVel.universe, [-4,   -1.5,    0,    0])
leftWheelVel['stopped']       = fuzz.trapmf(leftWheelVel.universe, [-0.2, -0.1,  0.1,  0.2])
leftWheelVel['slowForward']   = fuzz.trapmf(leftWheelVel.universe, [ 0,      0,  1.5,    4])
leftWheelVel['fastForward']   = fuzz.trapmf(leftWheelVel.universe, [ 1,    3.5,    5,    5])

rightWheelVel['fastReverse']   = fuzz.trapmf(rightWheelVel.universe, [-5,     -5, -3.5,   -1])
rightWheelVel['slowReverse']   = fuzz.trapmf(rightWheelVel.universe, [-4,   -1.5,    0,    0])
rightWheelVel['stopped']       = fuzz.trapmf(rightWheelVel.universe, [-0.2, -0.1,  0.1,  0.2])
rightWheelVel['slowForward']   = fuzz.trapmf(rightWheelVel.universe, [ 0,      0,  1.5,    4])
rightWheelVel['fastForward']   = fuzz.trapmf(rightWheelVel.universe, [ 1,    3.5,    5,    5])

wheelRules = [
  ctrl.Rule(orientation['left'] & leftSensor['no-signal'] & centerLeftSensor['no-signal'] & centerRightSensor['no-signal'] & rightSensor['no-signal'], [ leftWheelVel['fastForward'], rightWheelVel['stopped']]),
  ctrl.Rule(orientation['right'] & leftSensor['no-signal'] & centerLeftSensor['no-signal'] & centerRightSensor['no-signal'] & rightSensor['no-signal'], [ leftWheelVel['stopped'], rightWheelVel['fastForward']]),
  ctrl.Rule(orientation['center'] & leftSensor['no-signal'] & centerLeftSensor['no-signal'] & centerRightSensor['no-signal'] & rightSensor['no-signal'], [ leftWheelVel['fastForward'], rightWheelVel['fastForward']]),

  ctrl.Rule(~leftSensor['no-signal'], leftWheelVel['fastForward']),
  ctrl.Rule(~leftSensor['no-signal'], rightWheelVel['slowForward']),
  ctrl.Rule(~centerLeftSensor['no-signal'], leftWheelVel['fastForward']),
  ctrl.Rule(~centerLeftSensor['no-signal'], rightWheelVel['stopped']),

  ctrl.Rule(~rightSensor['no-signal'], rightWheelVel['fastForward']),
  ctrl.Rule(~rightSensor['no-signal'], leftWheelVel['slowForward']),
  ctrl.Rule(~centerRightSensor['no-signal'], rightWheelVel['fastForward']),
  ctrl.Rule(~centerRightSensor['no-signal'], leftWheelVel['stopped']),

  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['no-signal'], leftWheelVel['fastForward']),
  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['no-signal'], rightWheelVel['slowForward']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['no-signal'], rightWheelVel['fastForward']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['no-signal'], leftWheelVel['slowForward']),

  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['far'], leftWheelVel['fastForward']),
  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['far'], rightWheelVel['slowReverse']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['far'], rightWheelVel['fastForward']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['far'], leftWheelVel['slowReverse']),

  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['near'], leftWheelVel['fastForward']),
  ctrl.Rule(~leftSensor['no-signal'] & centerLeftSensor['near'], rightWheelVel['fastReverse']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['near'], rightWheelVel['fastForward']),
  ctrl.Rule(~rightSensor['no-signal'] & centerRightSensor['near'], leftWheelVel['fastReverse']),

  ctrl.Rule(~centerLeftSensor['no-signal'] & ~centerRightSensor['no-signal'] & ~rightSensor['no-signal'], leftWheelVel['slowReverse']),
  ctrl.Rule(~centerLeftSensor['no-signal'] & ~centerRightSensor['no-signal'] & ~rightSensor['no-signal'], rightWheelVel['fastForward']),

  ctrl.Rule(~centerRightSensor['no-signal'] & ~centerLeftSensor['no-signal'] & ~leftSensor['no-signal'], leftWheelVel['fastForward']),
  ctrl.Rule(~centerRightSensor['no-signal'] & ~centerLeftSensor['no-signal'] & ~leftSensor['no-signal'], rightWheelVel['slowReverse'])

]

wheelControl = ctrl.ControlSystem(wheelRules)
wheelFuzzy   = ctrl.ControlSystemSimulation(wheelControl)

KJuniorProxSensors    = []
KJuniorProxSensorsVal = []

for i in [1, 2, 4, 5]:
  errorCode, proxSensor = vrep.simxGetObjectHandle(clientID, 'KJunior_proxSensor' + str(i), vrep.simx_opmode_oneshot_wait)
  KJuniorProxSensors.append(proxSensor)
  errorCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, proxSensor, vrep.simx_opmode_streaming)
  distance = round(2000 - np.linalg.norm(detectedPoint) * 20000, 2)
  if distance <= 0 or distance == 2000:
    distance = 0
  KJuniorProxSensorsVal.append(distance)

# Current KJunior and Objective position
errorCode, KJuniorCurrentPosition = vrep.simxGetObjectPosition(clientID, KJuniorHandle, -1, vrep.simx_opmode_streaming)
errorCode, LaptopPosition = vrep.simxGetObjectPosition(clientID, LaptopHandle, -1, vrep.simx_opmode_streaming)

# Orientation related to Origin
errorCode, _KJuniorOrientation = vrep.simxGetObjectOrientation(clientID, KJuniorHandle, -1, vrep.simx_opmode_streaming)
KJuniorOrientationOrigin = [math.degrees(_KJuniorOrientation[0]), math.degrees(_KJuniorOrientation[1]), math.degrees(_KJuniorOrientation[2])]

# Orientation related to Objective
KJuniorOrientationObjective = math.degrees(
  math.atan2(KJuniorCurrentPosition[1] - LaptopPosition[1], KJuniorCurrentPosition[0] - LaptopPosition[0])
)

reachedDestination = False

while not reachedDestination:
  # Current KJunior and Objective position
  errorCode, KJuniorCurrentPosition = vrep.simxGetObjectPosition(clientID, KJuniorHandle, -1, vrep.simx_opmode_buffer)
  errorCode, LaptopPosition = vrep.simxGetObjectPosition(clientID, LaptopHandle, -1, vrep.simx_opmode_buffer)

  # Orientation related to X axis
  errorCode, _KJuniorOrientation = vrep.simxGetObjectOrientation(clientID, KJuniorHandle, -1, vrep.simx_opmode_buffer)
  KJuniorOrientationOrigin = [math.degrees(_KJuniorOrientation[0]), math.degrees(_KJuniorOrientation[1]), math.degrees(_KJuniorOrientation[2])]
  KJuniorOrientationRelativeToX = 0
  if KJuniorOrientationOrigin[2] >= 0:
    KJuniorOrientationRelativeToX = KJuniorOrientationOrigin[1] * -1
  else:
    if KJuniorOrientationOrigin[1] < 0:
      KJuniorOrientationRelativeToX = 180 - abs(KJuniorOrientationOrigin[1])
    else:
      KJuniorOrientationRelativeToX = (180 - KJuniorOrientationOrigin[1]) * -1

  # Orientation related to Objective
  KJuniorOrientationObjective = math.degrees(
    math.atan2(LaptopPosition[1] - KJuniorCurrentPosition[1], LaptopPosition[0] - KJuniorCurrentPosition[0])
  ) * -1

  # Orientation relative to my view and objective
  KJuniorOrientation = KJuniorOrientationRelativeToX - KJuniorOrientationObjective

  # Read sensors
  KJuniorProxSensorsVal = []
  for i in [1, 2, 4, 5]:
    distance = 0
    errorCode, proxSensor = vrep.simxGetObjectHandle(clientID, 'KJunior_proxSensor' + str(i), vrep.simx_opmode_oneshot_wait)
    errorCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, proxSensor, vrep.simx_opmode_buffer)
    # Normalize distance
    distance = round(2000 - np.linalg.norm(detectedPoint) * 20000, 2)
    # print(proxSensor, 'read', detectedPoint, 'with distance of', distance, 'detectionState', detectionState, 'errorCode', errorCode)
    if detectedObjectHandle == LaptopHandle:
      print('Reached destination!!!!!!!')
      reachedDestination = True
    if distance <= 0 or distance == 2000 or not detectionState:
      distance = 0
    KJuniorProxSensorsVal.append(distance)

  # FUZZY

  try:
    wheelFuzzy.input['leftSensor']   = KJuniorProxSensorsVal[0]
    wheelFuzzy.input['centerLeftSensor'] = KJuniorProxSensorsVal[1]
    wheelFuzzy.input['centerRightSensor'] = KJuniorProxSensorsVal[2]
    wheelFuzzy.input['rightSensor']  = KJuniorProxSensorsVal[3]
    wheelFuzzy.input['orientation']  = KJuniorOrientation
  except:
    print('ERROR IN INPUTS!!!!!!!!!!!!!!')
    print('ERROR IN INPUTS!!!!!!!!!!!!!!')
    print('ERROR IN INPUTS!!!!!!!!!!!!!!')
    print('ERROR IN INPUTS!!!!!!!!!!!!!!')
    print('ERROR IN INPUTS!!!!!!!!!!!!!!')
    pdb.set_trace()

  try:
    wheelFuzzy.compute()
  except:
    print('ERROR IN COMPUTATION!!!!!!!!!!!!!!')
    print('ERROR IN COMPUTATION!!!!!!!!!!!!!!')
    print('ERROR IN COMPUTATION!!!!!!!!!!!!!!')
    print('ERROR IN COMPUTATION!!!!!!!!!!!!!!')
    print('ERROR IN COMPUTATION!!!!!!!!!!!!!!')
    pdb.set_trace()

  leftVel  = wheelFuzzy.output['leftWheelVel']
  rightVel = wheelFuzzy.output['rightWheelVel']

  # print('--------------------------------------', KJuniorProxSensorsVal)
  # print('++++++++++++++++++++++++++++++++++++++', leftVel, rightVel)

  errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorLeftHandle,  leftVel , vrep.simx_opmode_streaming)
  errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorRightHandle, rightVel, vrep.simx_opmode_streaming)

  time.sleep(0.5)

errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorLeftHandle,  0, vrep.simx_opmode_streaming)
errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorRightHandle, 0, vrep.simx_opmode_streaming)
errorCode = vrep.simxStopSimulation(clientID, vrep.simx_opmode_oneshot)
