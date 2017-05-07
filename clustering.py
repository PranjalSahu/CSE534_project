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

def extract_features():
    textfeatures = []
    names = [os.path.basename(x) for x in glob.glob('./dataset/feature/*')]
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
        atomicFlow.append(names[nameCounter])
        allFeatures.append(atomicFlow)
        nameCounter += 1
    all_keys  = len_hash.keys()
    mean_hash = {}
    for key in all_keys:
        mean_hash[key] = sum(len_hash[key])/len(len_hash[key])
    all_features_filtered = []
    all_features_filtered_type = []
    index = 0
    for feature in  allFeatures:
        if len(feature[2]) >= mean_hash[feature_type_array[index]]:
            all_features_filtered.append(feature)
            all_features_filtered_type.append(mean_hash[feature_type_array[index]])
        index = index+1
    return [all_features_filtered, all_features_filtered_type, feature_type_array]


def get_dtw_distance(flow1, flow2):
    x = np.array(flow1)
    y = np.array(flow2)
    distance, path = fastdtw(x, y, dist=euclidean)
    
    return distance

def create_distance_matrix(features, inweight, outweight, allweight):
    nsamples = len(features)
    
    distMat = np.zeros((nsamples, nsamples))
    
    for i in range(0,nsamples):
        print(i)
        for j in range(0,nsamples):
            
            inDist = get_dtw_distance(features[i][0], features[j][0])
            outDist = get_dtw_distance(features[i][1], features[j][1])
            allDist = get_dtw_distance(features[i][2], features[j][2])
            
            netDistance = inweight * inDist + outweight * outDist + allweight * allDist
            distMat[i][j] = netDistance
    print(distMat)
    return distMat

def get_labels():
    labels = {}
    with open('dataset/output') as f:
        content = f.read().splitlines()
    
    for entry in content:
        entry = entry.split(' ');   
        labels[int(entry[0])] = entry[1]
    
    return labels
   
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
        for idx in clusteridx:
            actualcluster = labels[idx]
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

inweight = 0; outweight = 0; allweight = 1.0
#cluster(features)
distMat = create_distance_matrix(features, inweight, outweight, allweight)
#distArray = ssd.squareform(distMat)
distArray = distMat[np.triu_indices(len(features),1)]

Z = linkage(distArray, method='average')

#create three clusters
fl = fcluster(Z,3,criterion='maxclust');

purity = get_cluster_purity(get_labels(), features, fl, 3)
             
#plot dendogram
plt.figure(figsize=(10, 10))


#0th: incoming packets; 1st: outgoing packets; 2nd: incoming + outgoing
features = extract_features()
#features = features[0:5]

inweight = 1; outweight = 0.0; allweight = 0.0
#cluster(features)
distMat = create_distance_matrix(features, inweight, outweight, allweight)
#distArray = ssd.squareform(distMat)
distArray = distMat[np.triu_indices(len(features),1)]

Z = linkage(distArray, method='average')

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