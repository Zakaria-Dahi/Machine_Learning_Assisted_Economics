#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Predifined packages (e.g. call functions that are faster than user-made ones)
import numpy as np
from scipy.spatial import distance
import math
from random import random

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 

"""
    random initialisation
    repair function to ensure K clusters are actually created
    fitness function: sum of squared euclidian distances
    DPX1 crossover for integer-coded individuals.
    Synchronous replacement
"""

# function repair: ensures that each individual represents a configuration of K clusters
    
def repair(individual,val_check,test4,dim):
    pos = np.random.choice(np.arange(0,dim), replace=False, size=(np.size(test4))) # geneate random indices of positions in the chromosome where to insert the missing clusters
    for ind in range(np.size(pos)) : # browse the generated positions
        individual[pos[ind]] = test4[ind] # affect one missing cluster per one generated position
    test3 = np.isin(val_check, individual) # check if the processed chromosome is representing all the clusters
    test4 =  val_check[test3 ==  False] # retrive the clusters that are not represented by the processed chromosome
    if np.size(test4) != 0: # ensures that there is a real lack of clusters before reparing the chromosome
       individual = repair(individual,val_check,test4,dim) # call the repair function
    return individual;

# function centroids: compute the centroids of the clusters' configuration represented by a given cGA chromosome

def centroids(individual3,dim,data_clust,kk):
    feat = np.size(data_clust[0]) # extract the number of features
    centroid_mat = np.zeros(feat) # will savethe corrdinates of the K centroids
    sam1 = np.array(individual3) # convert the chromosome in numpy array: needed to call predefined funtion "where"
    for ind in range (1,(kk+1)): # browse each cluster
        sam2 = np.where(sam1 == ind) # extract the indicces of the cities that belong to the cluser "ind" being processed
        sam3 = sam2[0]
        # compute the centroid
        centroid = np.zeros(feat); # initialise the centroid's coordinate for each rocessed cluster
        for ind1 in sam3: # browse each city
            centroid = np.array(centroid) + np.array(data_clust[ind1])                     
        centroid = centroid / np.size(sam3)  #centroid computed according to equation 2 (see paper) and widely used in the literature (inclusding scikit learn official website)            
        centroid_mat = np.vstack((centroid_mat, centroid))    
    centroid_mat = np.delete(centroid_mat,0,0) # delete the first line of uneuseful zeros
    return centroid_mat;


# function ff: compute the fitness value of a given cGA chromosome

def ff(individual,dim,data_clust,kk,center):
    fit = 0; # initialise the fitness of the chromosome being processed
    sam1 = np.array(individual)
    for ind in range (1,(kk+1)): # browse each cluster
        sam2 = np.where(sam1 == ind) # find the cities that belong to the cluster "ind" being processed
        sam3 = sam2[0] 
        for ind1 in sam3:
            euc_dist = distance.euclidean(data_clust[ind1], center[(ind-1)]) # the fitness is computed according to equation 1 of the paper (also widely used even in scikit learn documentation)
            fit = fit + math.pow(euc_dist,2)
    return fit;

# Distance2 computes the sum of the distances between each cluster's centroid and the farthest point in that cluster

def distance2(best_indiv,best_indiv_rep,data_clust,k):
    met_2 = 0
    sam1 = np.array(best_indiv_rep)
    for ind in range (1,(k+1)): # browse each cluster     
        dist = np.array([])
        sam2 = np.where(sam1 == ind) # find the cities that belong to the cluster "ind" being processed
        sam3 = sam2[0] 
        for ind1 in sam3:
            dist_val = math.pow(distance.euclidean(data_clust[ind1], best_indiv[(ind-1)]),2) # the fitness is computed according to equation 1 of the paper (also widely used even in scikit learn documentation)
            dist = np.append(dist,dist_val)
        met_2 = met_2 + np.max(dist)
    return met_2
    
# Distance3 computes inertia inter class : sum of the distances between all the clusters' centroids

def distance3(best_indiv):    
    dist = 0
    numb_clust = len(best_indiv[:,0])
    for i in range(numb_clust):
        if i < numb_clust: # avoid the case of the last cluster because distance with remaining clusters has already been computed
            for j in range ((i+1),numb_clust):
                dist = dist + math.pow(distance.euclidean(best_indiv[i], best_indiv[j]),2)
    return dist            

# Distance 4 computes the sum of the distances between each cluster's centroid and the closest points from the remaining clusters

def distance4(best_indiv,best_indiv_rep,data_clust,k):
    sam1 = np.array(best_indiv_rep)
    dist = 0
    for ind1 in range(1,(k+1)):
        for ind2 in range(1,(k+1)):
            if ind1 != ind2: # avoid the case where we treat the same cluster
                dist_vect = np.array([])
                sam2 = np.where(sam1 == ind2) # find the cities that belong to the cluster "ind" being processed
                sam3 = sam2[0] 
                for ind3 in sam3:
                    dist_val = math.pow(distance.euclidean(data_clust[ind3], best_indiv[(ind1-1)]),2) # the distance is computed according to equation 1 of the paper (also widely used even in scikit learn documentation)
                    dist_vect = np.append(dist_vect,dist_val)     
                dist = dist + np.min(dist_vect)
    return dist;

# function cGA: is the main of the cGA algorithm

def cGA(pop,dim,it,pc,pm,data_clust,k,N,D):  
    """
    Variables' declaration
    """
    sample_size = len(data_clust[0])
    fitness_all = [None] * pop # create an array to save all the chromosomes fintess values
    best_fit = 100000000000000; #set big enough so that it can be enhanced later using the cGA (solving the clustering as a minimisation problem)
    best_indiv = np.full(((k+1),sample_size),None) #empty list to be filled later with the centroids of the best individual found at each cGA step
    best_indiv_rep = [None] * dim # empty list to stores the cluster configuration leading to the best individual centroids "best_indiv
    population_copy = np.full((pop,dim),None)
    fitness_all_copy = [None] * pop
    
    """
    Initialisation Phase: create the population of chromosome
    """
    k = k+1 # adjusting the values of K : number of clusters are transmitted from 0 to (K - 1) 
    population = np.random.randint(1,(k+1),size = (pop,dim)); # create a population of integers [from 1 to K] of size (pop x dim)    
    """
    Repair Phase: ensures that K clusters are really represented in each chromosome
    """
    val_check = np.arange(1,k+1) # create a list of K evenly-spaced integers:s from 1 to K clusters
    for i in range(pop): # browse all the population 
        test = np.isin(val_check, population[i]) # check if the processed chromosome is representing all the clusters
        test2 =  val_check[test ==  False] # retrive the clusters that are not represented by the processed chromosome
        if np.size(test2) != 0: # ensures that there is a real lack of clusters before reparing the chromosome
           population[i][0:dim] = repair(population[i],val_check,test2,dim) # call the repair function
    """
    Compute the fitness of each chromosome 
    """
    for i in range(pop): # browse each chromosome in the population
        centroids_co = np.full((k,sample_size),None)
        centroids_co[:][:] =   centroids(population[i],dim,data_clust,k)  #compute the centroids of the clusters represented by the processed chromosome
        fitness = ff(population[i],dim,data_clust,k,centroids_co) # compute the fitness of the processed chromosome
        fitness_all[i] = fitness
        #compute the best individual
        if best_fit >= fitness:
           best_fit = fitness
           for index in range(k):
               best_indiv[index][0:sample_size] = centroids_co[index][0:sample_size]   
           best_indiv_rep[0:dim] = population[i][0:dim]
           
    """    
    Process of the cGA
    """
    for ito in range(it): # repeat the cGA's phases "it" times
        # copy the population in an auxiliary one
        for index in range (pop):
            population_copy[index][0:dim] = population[index][0:dim]
            fitness_all_copy[index] = fitness_all[index]

        for i in range (0,N): # browse the grid node by node
            for j in range (1,(D+1)):
                processed = (i * D) + j # index of the processed node in the grid
                # extract Von Neumann Neigbourhood: left right, top, bottom
                if i !=0 and i != N-1 and j != 1 and j != D:
                    neighbourhood = [(processed-1),(processed+1),(processed-D),(processed+D)]  
               
                else :
                    if processed == 1: # first col, first row
                        neighbourhood = [D,(processed+1),(((N-1) * D) +j),(processed+D)]   
                    
                    if processed == D: # last col, first row
                        neighbourhood = [(D-1),1,(N* D),(processed+D)]
                    
                    if processed == ((N-1) * D) + 1: # first col, last row
                        neighbourhood = [(N* D),(processed+1),(processed-D),1]
                    
                    if processed == N*D: # last col, last row       
                        neighbourhood = [(processed-1),(((N-1) * D) + 1),(processed-D),D]
            
                    if ((i == 0) and (j != 1) and (j != D)): # first row
                        neighbourhood = [(processed-1),(processed+1),(((N-1) * D) + j),(processed+D)]
         
                    if ((i == N-1) and (j != 1) and (j != D)): # last row
                        neighbourhood = [(processed-1),(processed+1),(processed-D),j]
          
                    if ((j == 1) and (i != 0) and (i != N-1)): # first column
                        neighbourhood = [(processed+D-1),(processed+1),(processed-D),(processed+D)]
           
                    if ((j == D) and (i != 0) and (i != N-1)): # last column
                        neighbourhood = [(processed-1),(processed - D +1),(processed-D),(processed+D)]

                # adjust indices = python array/matrices  starts from 0
                processed = processed - 1
                neighbourhood[0] = neighbourhood[0] - 1
                neighbourhood[1] = neighbourhood[1] - 1
                neighbourhood[2] = neighbourhood[2] - 1
                neighbourhood[3] = neighbourhood[3] - 1
                # Selection via binary tournament: parent 1 = processed chromosome, parent 2 = selection via binary tournament on Von Neumann neighbourhood of parent 1
                parent1 = [None] * dim
                parent1[0:dim] = population[processed][0:dim] # choose the processed chomosome the first parent 1
                fit_neigh = [None]*4
                fit_neigh = [fitness_all[neighbourhood[0]],fitness_all[neighbourhood[1]],fitness_all[neighbourhood[2]], fitness_all[neighbourhood[3]]]
                parent2 = [None] * dim
                id_parent2 =  neighbourhood[fit_neigh.index(min(fit_neigh))]
                parent2[0:dim] = population[id_parent2][0:dim] # choose the best of News neighbourhood as parent 2         
                """
                Crossover : perform DPX1 crossover
                """
                offspring1 = np.array([None] * dim)
                offspring2 = np.array([None] * dim)
                offspring1[0:dim] = parent1[0:dim] # copy the parent 1 in the offspring 1
                offspring2[0:dim] = parent2[0:dim] # copy the parent 2 in the offspring 2
                if random() <= pc: # if condition of crossover satisfied perform the crossover
                    switch_points = np.random.choice(np.arange(0,dim), replace=False, size=(2))
                    while switch_points[0] > switch_points[1]:
                        switch_points = np.random.choice(np.arange(0,dim), replace=False, size=(2))
                    offspring1[switch_points[0]:switch_points[1]] = parent2[switch_points[0]:switch_points[1]] 
                    offspring2[switch_points[0]:switch_points[1]] = parent1[switch_points[0]:switch_points[1]]  
                # keep the offspring having the largest portion of the best parent
                # extract the best parent 
                best_par = [None]*dim
                if fitness_all[processed] <= fitness_all[id_parent2]:
                    best_par[0:dim] = parent1[0:dim]
                else:
                    best_par[0:dim] = parent2[0:dim]

                diff1 = [None] *dim
                diff2 = [None] *dim
                diff1[0:dim] = offspring1[0:dim] - best_par[0:dim]
                diff2[0:dim] = offspring2[0:dim] - best_par[0:dim]
                             
                offspring = [None] * dim
                if np.count_nonzero(diff1 == 0) > np.count_nonzero(diff2 == 0):
                    offspring[0:dim] = offspring1[0:dim]
                else:
                    offspring[0:dim] = offspring2[0:dim]

                """
                Mutation: perform a distance-based mutation
                """
                for index in range(dim):
                    if random() <= pm: # if condition of mutation satisfied perform the mutation
                        if k > 1: # avoid case of 1 cluster: normalization will result in case of undefined limit
                            # Ensures that the mutated offspring is valid
                            test = np.isin(val_check, offspring)
                            test2 =  val_check[test ==  False]
                            if np.size(test2) != 0:
                                offspring[0:dim] = repair(offspring,val_check,test2,dim) 
                            cent = np.full((k,sample_size),None)
                            cent[:][:] =   centroids(offspring,dim,data_clust,k)  # compute the centroids of the cluster configuration represented by offspring before mutation                       

                            dist_vect = np.array([]);
                            for ind in range (1,(k+1)): # browse each cluster                    
                                dist = math.pow(distance.euclidean(data_clust[index], cent[(ind-1)]),2) # compute the distance between the sample represented by the processed gene and the centroids of each cluster represented by the offspring
                                dist_vect= np.append(dist_vect, dist)
                            # normalize distances to probabilities
                            prob = 1 - (dist_vect - np.min(dist_vect))/(np.max(dist_vect) - np.min(dist_vect))
                            for ii in range (len(prob)):
                                if (random() <= prob[ii]) and ((ii+1) != offspring[index]) : # replace the current cluster by a the one chosen randomply based on its probability and if it is not the same as the current one
                                    offspring[index] = ii+1 #apply the mutation
                                    break
                """
                Repair function: test if offspring 1 and 2 are valid (all clusters are created) 
                """
                test = np.isin(val_check, offspring)
                test2 =  val_check[test ==  False]
                if np.size(test2) != 0:
                    offspring[0:dim] = repair(offspring,val_check,test2,dim)
                """
                Fitness computing of offspring
                """
                centroids_co = np.full((k,sample_size),None)
                centroids_co[:][:] =   centroids(offspring,dim,data_clust,k)  # compute the centroids of the cluster configuration represented by offspring
                fit = ff(offspring,dim,data_clust,k,centroids_co) # compute the fitness value of offspring 
                
                """
                Replacement: perform a synchronous replacement 
                """
                if fit <= fitness_all[processed]:
                   fitness_all_copy[processed] = fit
                   population_copy[processed][0:dim]  = offspring[0:dim]
                   # udpdate the global best
                   if fit <= best_fit:
                       best_fit = fit
                       for index in range(k):
                           best_indiv[index][0:sample_size] = centroids_co[index][0:sample_size]   
                       best_indiv_rep[0:dim] = offspring[0:dim]
        """
        Replace the old population with the auxilary one
        """
        for index in range (pop):
            population[index][0:dim] =  population_copy[index][0:dim]
            fitness_all[index] = fitness_all_copy[index]
        
    """
    compute two additional metric that could explain the quality of clustering (to minimize)
    # metric_1 : sum of the distances between each cluster's points and centroids (to minimize)
    # metric_2 : sum of the distances between the fartheset point in each cluster and the cluster's centroid
    # metric_3 : sum of the distances between all the clusters' centroids (to maximize)
    # metric_4 : sum of the distances between each cluster's centroid and its nearest point from other clusters (to maximize)
    """
    metric_1 = best_fit   
    metric_2 = distance2(best_indiv,best_indiv_rep,data_clust,k) 
    metric_3 = distance3(best_indiv)
    metric_4 = distance4(best_indiv,best_indiv_rep,data_clust,k) 
    # print(metric_1, metric_2,metric_3,metric_4)
    return best_indiv;
