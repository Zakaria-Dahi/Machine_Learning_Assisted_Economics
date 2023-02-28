# -*- coding: utf-8 -*-
"""
Created on ---------------------

"""


# Used to connect and query the database
import sqlite3
# libs for array use, plots, etc.
import numpy as np
# lib containing the predefined K-MEANS in python
from sklearn.cluster import KMeans
# lib used to generate the possible permutation of N digits
from itertools import permutations 
# lib to compute some statistics
# import statistics as st
# the DcGA producing initial centroids
from cGA import cGA 
# lib used to write on excel files
from xlwt import Workbook 

# Given a vector reduces it, accumulating each n values in one (mean value)
def reduce_vector(v: list, n: int) -> list:
    v2 = []
    for i in range(0, len(v), n):
        mean = 0
        for j in range(i, i+n):
            mean += v[j]
        v2.append(mean/n)
    return v2


# Return an array in which each position indicates the elements in cluster i
def get_sets(cluster, num):
    s = []
    for idx in range(num):
        s.append(
            set(
                [i for i, e in enumerate(cluster) if e == idx]
            )
        )
    return s


# distance between two clusters with an specific order
def distance_with_order(s1, s2, perm_comb):
    dist = 0
    for i in range(len(perm_comb)):
        dist += len(s1[i].union(s2[perm_comb[i]])) - len(s1[i].intersection(s2[perm_comb[i]]))
    return dist


# distance between two clustersing (it test all possible combinations)
def distance_clusters(cluster1, cluster2, cluster_num):
    index_cluster_all = list(range(0, cluster_num))  # create an array with the indexes of clusters
    perm = permutations(index_cluster_all)  # stores the permutations
    d = None
    set_c1 = get_sets(cluster1, cluster_num)
    set_c2 = get_sets(cluster2, cluster_num)
    for perm_comb in perm:  # browse the permutations
        n_d = distance_with_order(set_c1, set_c2, perm_comb)
        if not d or n_d < d:
            d = n_d

    return d


def clustering_step_2(cluster_num, verb,pop,it,pc,pm,NN,D):
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE SECOND STEP OF CLUSTERING HAS STARTED")  
    print("***********************************************************************************************")  
    # connect to the database
    conn = sqlite3.connect('db-reduced.db')
    c = conn.cursor()
    # extract the series of info
    series = c.execute('SELECT DISTINCT serie_name FROM data')
    data_ser = series.fetchall()
    # extract the locations
    locations = c.execute('SELECT DISTINCT location_name FROM data')
    data_loc = locations.fetchall()
    # define the number of months considered in each clustering
    months_considered = [1, 2, 3, 4, 6, 12]  # 1 is for a clustering considering all the months (not mean of 12 months)
    months_histogram = [0, 0, 0, 0, 0]
    # display some information about the final data displayed
    if verb == 1:
        print("***********************************************************************************************")
        print("IMPORTANT:")
        print("  - The data displayed at the end of step II is a 1x33 array.")
        print("- Each value in the array corresponds to the ideal number of months to consider for the clustering of "
              "each series of information.")
        print("  - The index of the value corresponds to the index of the serie of information to be used with.")
        print("  - If a given value is Y months, then 15 x Y features will be considered in the clustering.")  
        print("- Technically speaking, 15 x 1 features will be considered since we will take the mean of Y months in "
              "each of the 15 years.")
        print("***********************************************************************************************")  

    # ============================================== PERFORM CLUSTERING ACCORDING TO 6 CONFIGURATIONS ==================
    i = 0  # index to count down the series having been processed ("i" will be only used for displaying information)
    wb = Workbook() # open a new workbood
    sh = wb.add_sheet('data') # add a new sheet
    for tuple1 in data_ser:  # browse series
        i = i + 1  # increment the index of the serie each time one is browsed
        cluster_labels = np.zeros(52)  # will store the number of the cluster to whome each city belongs
        if verb == 1:
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("Information n° %i being processed: " % i, tuple1[0])
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        for ind in months_considered:  # browse the number of months considered:2, 3, 4, 6 and 12
            data_x_months = np.zeros(15*12//ind)  # stores the data of 15 years x 12/ind values (The mean of ind months)
            for tuple2 in data_loc:  # browse locations
                # print(tuple2[0])  # uncomment to know which city you are browsing
                # ====== RETRIEVE THE RECORDS OF THE GIVEN SERIE FOR THE PROCESSED CITY  ===============================
                records = c.execute('SELECT * FROM data WHERE serie_name = ? AND location_name =  ? ',
                                    (tuple1[0][:], tuple2[0][:]))
                data_rec = records.fetchall()
                data_mat = []  # the matrix contains the records of a city for a given series, year and period
                for tuple3 in data_rec:
                    # print(tuple3) # uncomment to know the tuple of info being displayed
                    data_mat = np.append(data_mat, tuple3[5])  # append the records
                # ===== build-up the matrix of records that will undergo clustering, lines: cities, columns:
                data_mat = reduce_vector(data_mat, ind)
                # records of the cities =========
                data_x_months = np.vstack((data_x_months, data_mat))
            # ====================== PERFORM THE K-MEANS CLUSTERING ========================
            data_x_months = np.delete(data_x_months, 0, 0)  # delete the first row of unuseful zeros (see above)
            # print(len(data_all_months[0])) # uncomment to check the number of records
            # print(len(data_all_months))  # uncomment to check the number of cities
            # ====================== compute initial centroids using GA ========================       
            dim = len(data_x_months[:,0]) # extract the number of cities = size of te GA's individual
            # compute the initial centroids via DcGA
            centro = cluster_num - 1;
            centroids = cGA(pop,dim,it,pc,pm,data_x_months,centro,NN,D)
            # ============= PERFORM K-MEANS CLUSTERING USING K CENTROIDS FOUND IN STEP I ===========================
            # perform the K-means clustering: info about parameters can be found in
            # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
            clust = KMeans(n_clusters=cluster_num, init=centroids, n_init=10, max_iter=300, tol=0.0001, verbose=0,
                           random_state=None, copy_x=True, algorithm='auto').fit(data_x_months)
            # print(clust.labels_) # uncomment to observe the labels of the clusters to which belong each city
            # print(clust.inertia_) # uncomment to observe the value of dispertion: sum of squared distances
            cluster_labels = np.vstack((cluster_labels, clust.labels_))  # append the result of the clustering

        cluster_labels = np.delete(cluster_labels, 0, 0)  # delete the unuseful set of zeros at the begining
        # print(len(cluster_labels)) # uncomment to know the number of feature configurations considered
        # print(len(cluster_labels[0])) # uncomment to know the number of cities considered
        # print(cluster_labels) # uncomment to print the result of clustering in each of the 6 feature configurations
        
        # ======== COMPUTE DISTANCE BETWEEN CLUSTERING USING 15x12 FEATURES CONFIGURATIONS AND 15 x 1 FEATURES =========
        distance_clustering = []  # will contain the distances between the clustering
        # compute the distance between the clustering
        index_feat = 0
        for ind_config in range(1, len(months_considered)):
            distance = distance_clusters(cluster_labels[0][:], cluster_labels[ind_config][:], cluster_num)
            # display the distance between the clustering
            if verb == 1:
                print(f"The distance between a clustering with 180 features and the one with " 
                      f"{12//months_considered[ind_config] * 15} features considering {months_considered[ind_config]}"
                      f" months) is: {distance}")
            # append the distance between the clustering of 180 features and the processed clustering
            distance_clustering.append(distance)
            sh.write((i-1),index_feat,distance) # write down the distance in excel file
            index_feat = index_feat + 1            
        min_dist = min(distance_clustering)
        for j in range(len(distance_clustering)):
            if distance_clustering[j] == min_dist:
                months_histogram[j] += 1

    if verb == 1:
        for i, e in enumerate(months_histogram):
            print(f"{months_considered[i+1]} months: {e}")
    features_number = months_considered[
        len(months_histogram) - months_histogram[::-1].index(max(months_histogram))
    ]
    sh.write(40,0,features_number) #" write down the ideal number of features to be considered
    wb.save('step2_data.xls')  # save the wokbook     
    if verb == 1:
        print("***********************************************************************************************")
        print("Ideal # of months to to be used for the clustering:", features_number)  
        print("***********************************************************************************************")
    
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE SECOND STEP OF CLUSTERING HAS FINISHED")  
    print("***********************************************************************************************")
    return features_number
