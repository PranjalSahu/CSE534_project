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
from scipy.cluster.hierarchy import fcluster    
from matplotlib import pyplot as plt

def DTWDistance(s, t):
    n = len(s)
    m = len(t)
    dtw = np.zeros((n, m))
    for i in range(0, len(s)):
        dtw[i, 0] = 1000000
    for i in range(0, len(t)):
        dtw[0, i] = 1000000
    dtw[0, 0] = 0
    for i in range(1, n):
        for j in range(1, m):
            cost = abs(s[i] - t[j])
            dtw[i, j] = cost + min( dtw[i-1, j], dtw[i  , j-1], dtw[i-1, j-1])
            
    flow_length_distance =  abs(len(s) - len(t))
    return dtw[n-1, m-1] * 0.001 + flow_length_distance

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

def create_distance_matrix(features, outweight, inweight, allweight):
    nsamples = len(features)
    
    distMat = np.zeros((nsamples, nsamples))
    
    for i in range(0,nsamples):
        print(i)
        for j in range(0,nsamples):
            
            outDist = get_dtw_distance(features[i][0], features[j][0])
            inDist = get_dtw_distance(features[i][1], features[j][1])
            allDist = get_dtw_distance(features[i][2], features[j][2])
#            outDist = DTWDistance(features[i][0], features[j][0])
#            inDist = DTWDistance(features[i][1], features[j][1])
#            allDist = DTWDistance(features[i][2], features[j][2])
            
            netDistance = inweight * inDist + outweight * outDist + allweight * allDist
            distMat[i][j] = netDistance
    print(distMat)
    return distMat

   
def get_cluster_purity(features, fl, numclusters):    
    #1: post_on_wall 2:send_message 3:open_user_profile
    cluster1total = 0; cluster2total = 0; cluster3total = 0
    clusterlengths = []; maxvotes = []
    purity = []
    clusteridxs = []
    for itr in range(1,numclusters + 1):
        clusteridx = np.where(fl == itr)[0].tolist()
        clusteridxs.append(clusteridx)
    
    cluster_centers = []
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
        
        majority_label = ''
        if majorityClusters == cluster1total:
            majority_label = 'post_on_wall'
        elif majorityClusters == cluster2total:
            majority_label = 'send_message'
        elif majorityClusters == cluster3total:
            majority_label = 'open_user_profile'    
        
        outmean = 0; inmean = 0; allmean = 0
        for idx in clusteridx:
            label = features[idx][3]
            if label == majority_label:
                outmean += len(features[idx][0])
                inmean += len(features[idx][1])
                allmean += len(features[idx][2])
        
        outmean = (float)(outmean)/(float)(majorityClusters)
        inmean = (float)(inmean)/(float)(majorityClusters)
        allmean = (float)(allmean)/(float)(majorityClusters)
        
        center = [outmean, inmean, allmean]
        cluster_centers.append([center, majority_label])
        
    return purity, cluster_centers
 
def get_classified_flows(features, cluster_centers, inweight, outweight, allweight):
        
    classified_flows = []
    for feature in features:        
        feature_characteristic = outweight * len(feature[0]) + inweight * len(feature[1]) + allweight * len(feature[2])
        assignedCluster = ''
        assignedCluster_characteristic = 0
        feature_distance = 100000000
        for cluster in cluster_centers:
            cluster_type = cluster[1]
            cluster_characteristic = outweight * cluster[0][0] + inweight * cluster[0][1] + allweight * cluster[0][2]
            if feature_distance > abs(cluster_characteristic - feature_characteristic):
                feature_distance = abs(cluster_characteristic - feature_characteristic)
                assignedCluster = cluster_type
                assignedCluster_characteristic = cluster_characteristic
        
        feature_actualtype = feature[3]
        feature_assignedtype = assignedCluster
        feature_id = feature[4]
        
        feature_details = [feature_actualtype, feature_assignedtype, feature_id, feature_characteristic, assignedCluster_characteristic]
        classified_flows.append(feature_details)
    
    return classified_flows
        
#0th: incoming packets; 1st: outgoing packets; 2nd: incoming + outgoing
features = extract_features("./dataset/train/feature/*")

inweight = 0; outweight = 0; allweight = 1
distMat = create_distance_matrix(features, outweight, inweight, allweight)
distArray = distMat[np.triu_indices(len(features),1)]

Z = linkage(distArray, method='average')

#create three clusters
fl = fcluster(Z,3,criterion='maxclust');

purity,cluster_centers = get_cluster_purity(features, fl, 3)
             
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



#classfication of test data
test_features = extract_features("./dataset/feature/*")
classified_flows = get_classified_flows(test_features, cluster_centers, inweight, outweight, allweight)

positive_count = 0
for clflow in classified_flows:
    if clflow[0] == clflow[1]:
        positive_count += 1

flow_accuracy = float(positive_count)/float(len(classified_flows))

actions = {}

for clflow in classified_flows:
    flowid = clflow[2]
    if flowid in actions:
        actions[flowid].append(clflow)
    else:
        actions[flowid] = []
        actions[flowid].append(clflow)
 
positive_action_count = 0
for key in actions.keys():
    flows = actions[key]
    
    actual_label = flows[0][0]
    
    correctlabelcount = 0
    for flow in flows:
        curr_label = flow[1]
        if curr_label == actual_label:
            correctlabelcount += 1
    
    if correctlabelcount >= (float)(len(flows))/2.0:
        positive_action_count += 1

action_accuracy = float(positive_action_count)/float(len(actions))
        
print 'flow accuracy = ', flow_accuracy
print 'event accuracy = ', action_accuracy
    
