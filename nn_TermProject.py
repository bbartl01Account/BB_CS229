#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 12:27:04 2024

@author: baxter
"""

import numpy as np
import matplotlib.pyplot as plt
from data_processing import createProcessedMaps, splitData

def sigmoid(x):
    """
    Compute the sigmoid function for the input here.

    Args:
        x: A numpy float array

    Returns:
        A numpy float array containing the sigmoid results
    """
    return 1/(1+np.exp(-x))

def get_initial_params(input_size, num_hidden, num_output):
    """
    Compute the initial parameters for the neural network.

    This function should return a dictionary mapping parameter names to numpy arrays containing
    the initial values for those parameters.

    There should be four parameters for this model:
    W1 is the weight matrix for the hidden layer of size num_hidden x input_size
    b1 is the bias vector for the hidden layer of size num_hidden
    W2 is the weight matrix for the output layers of size num_output x num_hidden
    b2 is the bias vector for the output layer of size num_output

    As specified in the PDF, weight matrices should be initialized with a random normal distribution
    centered on zero and with scale 1.
    Bias vectors should be initialized with zero.
    
    Args:
        input_size: The size of the input data
        num_hidden: The number of hidden states
        num_output: The number of output classes
    
    Returns:
        A dict mapping parameter names to numpy arrays
    """

    # *** START CODE HERE ***
    W1 = np.random.normal(loc = 0, scale = 1, size = (num_hidden,input_size))
    b1 = np.zeros((num_hidden,1))
    W2 = np.random.normal(loc = 0, scale = 1, size = (num_output,num_hidden))
    b2 = np.zeros((num_output,1))
    # *** END CODE HERE ***
    return {"W1":W1, "b1":b1, "W2":W2, "b2":b2}

def forward_prop(data,k_vals,params,returnPred):
    middleReturn = None
    A = sigmoid((params["W1"] @ data) + params["b1"])
    k_pred = (params["W2"] @ A) + params["b2"]
    E = k_vals - k_pred
    if returnPred:
        middleReturn = k_pred
    else:
        middleReturn = E
    (m,n) = E.shape
    J = (np.linalg.norm(E)**2)/(m*n)
    return A, middleReturn, J

def backward_prop(data,k_vals,params):
    A, E, J = forward_prop(data, k_vals, params, False)
    (m,n) = E.shape
    dJ_dW2 = (-2/(m*n))*np.einsum('ik,jk->ij',E,A)
    dJ_db2 = (-2/(m*n))*np.sum(E,axis=1).reshape(m,1)
    dN_dA = -2*params["W2"].T @ E
    dN_dz = dN_dA * A * (1 - A)
    dJ_dW1 = np.einsum('ik,jk->ij',dN_dz,data)/(m*n)
    dJ_db1 = np.sum(dN_dz,axis=1).reshape(m,1)/(m*n)
    return {"W1":dJ_dW1, "b1":dJ_db1, "W2":dJ_dW2, "b2":dJ_db2}

def train_NN(data,k_vals,params):
    alpha = 1
    loop_count = 0
    A, E, J = forward_prop(data, k_vals, params, False)
    J_prev = None
    while True:
        J_prev = J
        loop_count += 1
        gradients = backward_prop(data, k_vals, params)
        params["W1"] -= alpha*gradients["W1"]
        params["W2"] -= alpha*gradients["W2"]
        params["b1"] -= alpha*gradients["b1"]
        params["b2"] -= alpha*gradients["b2"]
        A, E, J = forward_prop(data, k_vals, params, False)
        if loop_count == 10000 or np.abs(J - J_prev) < 0.001:
            # print(loop_count)
            # print(np.abs(J - J_prev))
            # print(J)
            return

if __name__ == '__main__':
    np.random.seed(229)
    kpVals = [10,5,1]
    kiVals = [1,0.5,0.1]
    kdVals = [0,0.1,0.5,1]
    kArray, dataArray = createProcessedMaps(kpVals, kiVals, kdVals)
    k_train, data_train, k_test, data_test = splitData(kArray, dataArray, False)
    params = get_initial_params(3, 3, 3)
    train_NN(data_train[:3,:], k_train[:3,:], params)
    A, k_pred, J_final = forward_prop(data_test[:3,:], k_test[:3,:], params, True)
    print(J_final)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111,projection='3d')
    ax1.scatter(k_test[0,:],k_test[1,:],k_test[2,:],"o",color='b',label="Data")
    ax1.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"*",color='r',label="Predictions")
    ax1.set_xlabel("Kp")
    ax1.set_ylabel("Ki")
    ax1.set_zlabel("Kd")
    ax1.set_title("Neural Network Evaluation")
    ax1.legend(loc="upper right")
    
    # fig2 = plt.figure()
    # ax2 = fig2.add_subplot(111,projection='3d')
    # ax2.scatter(k_pred[0,:],k_pred[1,:],k_pred[2,:],"o",color='k',label="Data")
    # ax2.legend(loc="upper right")
    
    plt.show()
    
    