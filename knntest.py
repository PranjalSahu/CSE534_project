# -*- coding: utf-8 -*-
"""
Created on Tue May 09 17:07:08 2017

@author: Sushant
"""

import numpy as np
from fastdtw import fastdtw
import glob
from matplotlib import pyplot as plt
import operator


def extract_features(path):
    textfeatures = []
    files = glob.glob(path)
    nameCounter = 0
    for fle in files:
       with open(fle) as f:
          text = f.read()
          textfeatures.append(text)
    allFeatures = []
    len_hash    = {}
    feature_type_array = []
    for feat in textfeatures:
        eachThreeSet = feat.split('\n')[0:3]
        feature_type = feat.split('\n')[3]
        feature_id = feat.split('\n')[4]
        if feature_type not in len_hash:
            len_hash[feature_type] = []
        feature_type_array.append(feature_type)
        atomicFlow = []
        for threeSet in eachThreeSet:
            inoutall = threeSet.split(',')
            vals = [int(x) for x in inoutall]
            atomicFlow.append(vals)
        len_hash[feature_type].append(len(atomicFlow[2]))
#        atomicFlow.append(names[nameCounter])
        atomicFlow.append(feature_type)
        atomicFlow.append(feature_id)
        allFeatures.append(atomicFlow)
        nameCounter += 1
    all_keys  = len_hash.keys()
    mean_hash = {}
    max_hash  = {}
    for key in all_keys:
        mean_hash[key] = sum(len_hash[key])/len(len_hash[key])
        len_hash[key].sort()
        max_hash[key]  = len_hash[key][(len(len_hash[key])*9)/10]
    all_features_filtered = []
    all_features_filtered_type = []
    index = 0
    for feature in  allFeatures:
        if len(feature[2]) >=  mean_hash[feature_type_array[index]] and len(feature[2]) <= max_hash[feature_type_array[index]]:
            all_features_filtered.append(feature)
            all_features_filtered_type.append(mean_hash[feature_type_array[index]])
        index = index+1
    return all_features_filtered


def get_dtw_distance(flow1, flow2):
    x = np.array(flow1)
    y = np.array(flow2)
    distance, path = fastdtw(x, y, dist=None)
    
    flow_length_distance =  abs(len(x) - len(y))
    return flow_length_distance + 0.001 * distance

def getDistance(x, y):
    
    in_weight = 0; out_weight = 0; all_weight = 1
    
    inDTWdistance = get_dtw_distance(x[1],y[1])
    outDTWdistance = get_dtw_distance(x[0],y[0])
    allDTWdistance = get_dtw_distance(x[2],y[2])
    
    distance = inDTWdistance * in_weight + outDTWdistance * out_weight + allDTWdistance * all_weight
    
    return distance
                                    

def getNeighbors(trainingSet, testInstance, k):
	distances = []
	for x in range(len(trainingSet)):
		dist = getDistance(testInstance, trainingSet[x])
		distances.append((trainingSet[x], dist))
	distances.sort(key=operator.itemgetter(1))
	neighbors = []
	for x in range(k):
		neighbors.append(distances[x][0])
	return neighbors

def getResponse(neighbors):
	classVotes = {}
	for x in range(len(neighbors)):
		response = neighbors[x][3]
		if response in classVotes:
			classVotes[response] += 1
		else:
			classVotes[response] = 1
	sortedVotes = sorted(classVotes.iteritems(), key=operator.itemgetter(1), reverse=True)
	return sortedVotes[0][0]

#0th: incoming packets; 1st: outgoing packets; 2nd: incoming + outgoing
features = extract_features("./dataset/train/feature/*")
test_features = extract_features("./dataset/feature/*")

predictions=[]
k = 5
correct_count = 0
for x in range(len(test_features)):
    neighbors = getNeighbors(features, test_features[x], k)
    result = getResponse(neighbors)
    print 'output = ', result, ' actual = ', test_features[x][3]
    if result == test_features[x][3]:
        correct_count += 1

flow_accuracy = float(correct_count )/ float(len(test_features))

print "flow accuracy = ", flow_accuracy
        
    
    


