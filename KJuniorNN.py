# -*- coding: utf-8 -*-
# Controle do KJunior por redes neurais.

import vrep
import sys
import numpy as np
import math
import time
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import redeNeural


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

wheelClf, xscaler = redeNeural.redeNeural()
KJuniorProxSensors    = []
KJuniorProxSensorsVal = []

centerLeftSensor = ctrl.Antecedent(np.arange(0, 2000, 1),   'centerLeftSensor')
centerRightSensor = ctrl.Antecedent(np.arange(0, 2000, 1),   'centerRightSensor')
leftSensor   = ctrl.Antecedent(np.arange(0, 2000, 1),   'leftSensor')
rightSensor  = ctrl.Antecedent(np.arange(0, 2000, 1),   'rightSensor')
orientation  = ctrl.Antecedent(np.arange(-181, 181, 0.1), 'orientation')
leftWheelVel     = ctrl.Consequent(np.arange(-5, 5, 0.1),     'leftWheelVel')
rightWheelVel     = ctrl.Consequent(np.arange(-5, 5, 0.1),     'rightWheelVel')

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
    if detectedObjectHandle == LaptopHandle and distance > 1300:
      print('Reached destination!!!!!!!')
      reachedDestination = True
    if distance <= 0 or distance == 2000 or not detectionState:
      distance = 0
    KJuniorProxSensorsVal.append(distance)

  X = [KJuniorOrientation] + KJuniorProxSensorsVal
  X = xscaler.transform([X])[0]
  print(X)
  leftVel, rightVel = wheelClf.predict([X])[0]
  print(leftVel, rightVel)

  # print('--------------------------------------', KJuniorProxSensorsVal)
  # print('++++++++++++++++++++++++++++++++++++++', leftVel, rightVel)

  errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorLeftHandle,  leftVel , vrep.simx_opmode_streaming)
  errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorRightHandle, rightVel, vrep.simx_opmode_streaming)

  time.sleep(0.05)

errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorLeftHandle,  0, vrep.simx_opmode_streaming)
errorCode = vrep.simxSetJointTargetVelocity(clientID, KJuniorRightHandle, 0, vrep.simx_opmode_streaming)
errorCode = vrep.simxStopSimulation(clientID, vrep.simx_opmode_oneshot)
