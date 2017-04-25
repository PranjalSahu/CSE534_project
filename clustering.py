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
from matplotlib import pyplot as plt

def extract_features():
    textfeatures = [];
    names = [os.path.basename(x) for x in glob.glob('./dataset/feature/*')]
    files = glob.glob("./dataset/feature/*")
    nameCounter = 0
    # iterate over the list getting each file 
    for fle in files:
       # open the file and then call .read() to get the text
       with open(fle) as f:
          text = f.read()
          textfeatures.append(text)
          
    allFeatures = []
    for feat in textfeatures:
        eachThreeSet = feat.split('\n')
        
        atomicFlow = []
        for threeSet in eachThreeSet:
            inoutall = threeSet.split(',')
            vals = [int(x) for x in inoutall]
            atomicFlow.append(vals)
        atomicFlow.append(names[nameCounter])
        allFeatures.append(atomicFlow)
        nameCounter += 1
            
    return allFeatures


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
    
    
#def distance_function(flow1, flow2):
#    inDist = get_dtw_distance(flow1[0], flow2[0])
#    outDist = get_dtw_distance(flow1[1], flow2[1])
#    allDist = get_dtw_distance(flow1[2], flow2[2])
#    netDistance = inweight * inDist + outweight * outDist + allweight * allDist
#    return netDistance

#def cluster(features):
    
#    flowvals = 
#    fclust1 = fclusterdata(features, 1.0, metric=distance_function)
    

            
    
        

#0th: incoming packets; 1st: outgoing packets; 2nd: incoming + outgoing
features = extract_features()
#features = features[0:5]

inweight = 0; outweight = 0.0; allweight = 1.0
#cluster(features)
distMat = create_distance_matrix(features, inweight, outweight, allweight)
#distArray = ssd.squareform(distMat)
distArray = distMat[np.triu_indices(len(features),1)]

Z = linkage(distArray, method='average')

#plot dendogram
plt.figure(figsize=(75, 25))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
)
plt.show()


