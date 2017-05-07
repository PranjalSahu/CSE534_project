# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 02:31:02 2017
@author: Sushant
"""
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import glob
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fclusterdata
from scipy.cluster.hierarchy import fcluster    
from matplotlib import pyplot as plt
import os

def DTWDistance(s, t):
    n = len(s)
    m = len(t)
    dtw = numpy.zeros(n, m)
    for i in range(0, len(s)):
        dtw[i, 0] = 1000000
    for i in range(0, len(t)):
        dtw[0, i] = 1000000
    dtw[0, 0] = 0
    for i in range(1, n):
        for j in range(1, m):
            cost = abs(s[i] - t[j])
            dtw[i, j] = cost + minimum( dtw[i-1, j], dtw[i  , j-1], dtw[i-1, j-1])
   return dtw[n-1, m-1]

def extract_features():
    textfeatures = []
#    names = [os.path.basename(x) for x in glob.glob('./dataset/feature/*')]
    files = glob.glob("./dataset/feature/*")
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
        if len(feature[2]) >= mean_hash[feature_type_array[index]] and len(feature[2]) <= max_hash[feature_type_array[index]]:
            all_features_filtered.append(feature)
            all_features_filtered_type.append(mean_hash[feature_type_array[index]])
        index = index+1
    return all_features_filtered



def get_dtw_distance(flow1, flow2):
    x = np.array(flow1)
    y = np.array(flow2)
    distance, path = fastdtw(x, y, dist=euclidean)
    
    flow_length_distance =  abs(len(x) - len(y))
    return flow_length_distance + distance * 0.001

def create_distance_matrix(features, outweight, inweight, allweight):
    nsamples = len(features)
    
    distMat = np.zeros((nsamples, nsamples))
    
    for i in range(0,nsamples):
        print(i)
        for j in range(0,nsamples):
            
            outDist = get_dtw_distance(features[i][0], features[j][0])
            inDist = get_dtw_distance(features[i][1], features[j][1])
            allDist = get_dtw_distance(features[i][2], features[j][2])
            
            netDistance = inweight * inDist + outweight * outDist + allweight * allDist
            distMat[i][j] = netDistance
    print(distMat)
    return distMat

   
def get_cluster_purity(labels, features, fl, numclusters):    
    #1: post_on_wall 2:send_message 3:open_user_profile
    cluster1total = 0; cluster2total = 0; cluster3total = 0
    clusterlengths = []; maxvotes = []
    purity = []
    clusteridxs = []
    for itr in range(1,numclusters + 1):
        clusteridx = np.where(fl == itr)[0].tolist()
        clusteridxs.append(clusteridx)
    
    for clusteridx in clusteridxs:
        cluster1total = 0; cluster2total = 0; cluster3total = 0
        print '---------------------------------------'
        for idx in clusteridx:
            actualcluster = features[idx][3]
            print actualcluster
            if actualcluster == 'post_on_wall':
                cluster1total += 1
            elif actualcluster == 'send_message':
                cluster2total += 1
            elif actualcluster == 'open_user_profile':
                cluster3total += 1
        majorityClusters = max(cluster1total, cluster2total, cluster3total)
        currpurity = (float)(majorityClusters)/(float)(len(clusteridx))
        clusterlengths.append(len(clusteridx))
        maxvotes.append(majorityClusters)
        purity.append(currpurity)

    return purity
    
#0th: incoming packets; 1st: outgoing packets; 2nd: incoming + outgoing
features = extract_features()
#features = features[0:5]

inweight = 0.5; outweight = 0.3; allweight = 0.5
#cluster(features)
distMat = create_distance_matrix(features, outweight, inweight, allweight)
#distArray = ssd.squareform(distMat)
distArray = distMat[np.triu_indices(len(features),1)]

Z = linkage(distArray, method='average')

#create three clusters
fl = fcluster(Z,3,criterion='maxclust');

purity = get_cluster_purity(features, fl, 3)
             
#plot dendogram
plt.figure(figsize=(10, 10))

#plot dendogram
plt.figure(figsize=(10, 10))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
)
plt.show()