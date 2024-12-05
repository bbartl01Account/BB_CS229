#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 00:42:35 2024

@author: baxter
"""

import numpy as np
import matplotlib.pyplot as plt
from data_processing import createProcessedMaps, splitData
from lwr_TermProject import LocallyWeightedLinearRegression
from nn_TermProject import get_initial_params, forward_prop, train_NN

def evaluateLeastSquares(k_train, data_train, k_test, data_test):
    k_train, data_train, k_test, data_test = splitData(kArray, dataArray, False)
    Theta = k_train @ data_train.T @ np.linalg.inv(data_train @ data_train.T)
    k_pred = Theta @ data_test
    m = np.size(k_test,0)
    n = np.size(k_test,1)
    MSE = (np.linalg.norm(k_pred - k_test)**2)/((m-1)*n)
    print("Least Squares MSE")
    print(MSE)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111,projection='3d')
    ax1.scatter(k_test[0,:],k_test[1,:],k_test[2,:],"o",color='b',s=70,label="Data")
    ax1.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"*",color='r',s=70,label="Predictions")
    ax1.set_xlabel("Kp")
    ax1.set_ylabel("Ki")
    ax1.set_zlabel("Kd")
    ax1.set_title("Least Squares Comparison")
    ax1.legend(loc="upper right")
    fig1.savefig('LeastSquares.png')

def evaluateNN(k_train, data_train, k_test, data_test):
    params = get_initial_params(3, 3, 3)
    train_NN(data_train[:3,:], k_train[:3,:], params)
    A, k_pred, J_final = forward_prop(data_test[:3,:], k_test[:3,:], params, True)
    print("NN MSE")
    print(J_final)
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111,projection='3d')
    ax2.scatter(k_test[0,:],k_test[1,:],k_test[2,:],"o",color='b',s=70,label="Data")
    ax2.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"*",color='r',s=70,label="Predictions")
    ax2.set_xlabel("Kp")
    ax2.set_ylabel("Ki")
    ax2.set_zlabel("Kd")
    ax2.set_title("Neural Network Evaluation")
    ax2.legend(loc="upper right")
    fig2.savefig('NN.png')

def evaluateLWR(k_train, data_train, k_val, data_val, k_test, data_test):
    m = np.size(k_val,0)
    n = np.size(k_val,1)
    tau_vals = [i/10 for i in range(1,11)]
    minMSE = 0
    tau_best = None
    for tau in tau_vals:
        lwr = LocallyWeightedLinearRegression(tau)
        lwr.fit(data_train,k_train)
        k_pred = lwr.predict(data_val)
        MSE = (np.linalg.norm(k_pred - k_val)**2)/((m-1)*n)
        if tau_best == None or MSE < minMSE:
            tau_best = tau
            minMSE = MSE
    #print(tau_best)
    lwr = LocallyWeightedLinearRegression(tau_best)
    lwr.fit(data_train,k_train)
    k_pred = lwr.predict(data_test)
    MSE = (np.linalg.norm(k_pred - k_test)**2)/((m-1)*n)
    print("LWR MSE")
    print(MSE)
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111,projection='3d')
    ax3.scatter(k_test[0,:],k_test[1,:],k_test[2,:],"o",color='b',s=70,label="Data")
    ax3.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"*",color='r',s=70,label="Predictions")
    ax3.set_xlabel("Kp")
    ax3.set_ylabel("Ki")
    ax3.set_zlabel("Kd")
    ax3.set_title("LWR Evaluation")
    ax3.legend(loc="upper right")
    fig3.savefig('LWR.png')

def evaluateRegularization(k_train, data_train, k_val, data_val, k_test, data_test):
    m = np.size(k_val,0)
    n = np.size(k_val,1)
    lambda_vals = [0.01, 0.05, 0.1, 0.5, 1, 5]
    minMSE = 0
    lambda_best = None
    for lam in lambda_vals:
        Theta = k_train @ data_train.T @ np.linalg.inv(data_train @ data_train.T + lam*np.eye(4,4))
        k_pred = Theta @ data_val
        MSE = (np.linalg.norm(k_pred - k_val)**2)/((m-1)*n)
        if lambda_best == None or MSE < minMSE:
            lambda_best = lam
            minMSE = MSE
    #print(lambda_best)
    Theta = k_train @ data_train.T @ np.linalg.inv(data_train @ data_train.T + lambda_best*np.eye(4,4))
    k_pred = Theta @ data_test
    MSE = (np.linalg.norm(k_pred - k_test)**2)/((m-1)*n)
    print("Regularization MSE")
    print(MSE)
    fig4 = plt.figure()
    ax4 = fig4.add_subplot(111,projection='3d')
    ax4.scatter(k_test[0,:],k_test[1,:],k_test[2,:],"o",color='b',s=70,label="Data")
    ax4.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"*",color='r',s=70,label="Predictions")
    ax4.set_xlabel("Kp")
    ax4.set_ylabel("Ki")
    ax4.set_zlabel("Kd")
    ax4.set_title("Regularization Evaluation")
    ax4.legend(loc="upper right")
    fig4.savefig('Regularization.png')

if __name__ == '__main__':
    np.random.seed(101)
    kpVals = [10,5,1]
    kiVals = [1,0.5,0.1]
    kdVals = [0,0.1,0.5,1]
    kArray, dataArray = createProcessedMaps(kpVals, kiVals, kdVals)
    k_train_norm, data_train_norm, k_test_norm, data_test_norm = splitData(kArray, dataArray, False)
    k_train_hyp, data_train_hyp, k_val_hyp, data_val_hyp, k_test_hyp, data_test_hyp = splitData(kArray, dataArray, True)
    evaluateLeastSquares(k_train_norm, data_train_norm, k_test_norm, data_test_norm)
    evaluateNN(k_train_norm, data_train_norm, k_test_norm, data_test_norm)
    evaluateLWR(k_train_hyp, data_train_hyp, k_val_hyp, data_val_hyp, k_test_hyp, data_test_hyp)
    evaluateRegularization(k_train_hyp, data_train_hyp, k_val_hyp, data_val_hyp, k_test_hyp, data_test_hyp)
    plt.show()
    