#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 12:37:04 2024

@author: baxter
"""

import util
import numpy as np
import collections

SETPOINT = 30
IDX_TO_SECONDS = 1/1000
END_TIME_FRACTION = 0.2
TRAIN_TEST_FRACTION = 0.75
TRAIN_VAL_TEST_FRACTION = 2/3

def computeRiseTime(speeds):
    rise_time = 0
    while int(speeds[rise_time]) != SETPOINT:
        rise_time += 1;
    return rise_time*IDX_TO_SECONDS

def computeSS_Error(speeds):
    idxStart = int((1-END_TIME_FRACTION)*len(speeds))
    error_t = speeds[idxStart:] - SETPOINT
    return np.dot(error_t,error_t)/len(error_t)

def computeStability(speeds):
    speedCounter = collections.Counter(speeds)
    commonSpeed, numOccurrences = speedCounter.most_common(1)[0]
    idxStart = np.min(np.where(speeds == commonSpeed))
    speedsSS = speeds[idxStart:]
    notCount = np.count_nonzero(speedsSS != commonSpeed)
    return numOccurrences/notCount

def createProcessedMaps(kpVals, kiVals, kdVals):
    kArray = np.ones((4,np.size(kpVals)*np.size(kiVals)*np.size(kdVals)))
    dataArray = np.ones((4,np.size(kpVals)*np.size(kiVals)*np.size(kdVals)))
    idxK = 0
    for p in kpVals:
        for i in kiVals:
            for d in kdVals:
                filename = "./"+str(p)+"_"+str(i)+"_"+str(d)+".csv"
                kArray[:,idxK] = np.array([p,i,d,1])
                time, speed = util.load_dataset(filename, add_intercept=False)
                dataArray[0,idxK] = computeRiseTime(speed)
                dataArray[1,idxK] = computeSS_Error(speed)
                dataArray[2,idxK] = computeStability(speed)
                idxK += 1
    return kArray, dataArray

def splitData(kArray, dataArray, addVal):
    numData = np.size(kArray,1)
    idxData = [i for i in range(numData)]
    np.random.shuffle(idxData)
    if addVal:
        trainSize = int(TRAIN_VAL_TEST_FRACTION*numData)
        otherSize = int(0.5*(numData-trainSize))
        k_train = np.zeros((4,trainSize))
        data_train = np.zeros((4,trainSize))
        k_val = np.zeros((4,otherSize))
        data_val = np.zeros((4,otherSize))
        k_test = np.zeros((4,otherSize))
        data_test = np.zeros((4,otherSize))
        for idx in range(numData):
            if idx < trainSize:
                k_train[:,idx] = kArray[:,idxData[idx]]
                data_train[:,idx] = dataArray[:,idxData[idx]]
            elif idx < trainSize + otherSize:
                k_val[:,idx - trainSize] = kArray[:,idxData[idx]]
                data_val[:,idx - trainSize] = dataArray[:,idxData[idx]]
            else:
                k_test[:,idx - (trainSize + otherSize)] = kArray[:,idxData[idx]]
                data_test[:,idx - (trainSize + otherSize)] = dataArray[:,idxData[idx]]
        return k_train, data_train, k_val, data_val, k_test, data_test
    else:
        trainSize = int(TRAIN_TEST_FRACTION*numData)
        k_train = np.zeros((4,trainSize))
        data_train = np.zeros((4,trainSize))
        k_test = np.zeros((4,numData-trainSize))
        data_test = np.zeros((4,numData-trainSize))
        for idx in range(numData):
            if idx < trainSize:
                k_train[:,idx] = kArray[:,idxData[idx]]
                data_train[:,idx] = dataArray[:,idxData[idx]]
            else:
                k_test[:,idx - trainSize] = kArray[:,idxData[idx]]
                data_test[:,idx - trainSize] = dataArray[:,idxData[idx]]
        return k_train, data_train, k_test, data_test

if __name__ == '__main__':
    np.random.seed(229)
    kpVals = [10,5,1]
    kiVals = [1,0.5,0.1]
    kdVals = [0,0.1,0.5,1]
    kArray, dataArray = createProcessedMaps(kpVals, kiVals, kdVals)
    print(kArray)
    print(dataArray)
    print("Train and Test")
    k_train, data_train, k_test, data_test = splitData(kArray, dataArray, False)
    print("K Train")
    print(k_train)
    print("Data Train")
    print(data_train)
    print("K Test")
    print(k_test)
    print("Data Test")
    print(data_test)
    print("Train, Val, and Test")
    k_train, data_train, k_val, data_val, k_test, data_test = splitData(kArray, dataArray, True)
    print("K Train")
    print(k_train)
    print("Data Train")
    print(data_train)
    print("K Val")
    print(k_val)
    print("Data Test")
    print(data_val)
    print("K Test")
    print(k_test)
    print("Data Test")
    print(data_test)