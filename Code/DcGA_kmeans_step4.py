# -*- coding: utf-8 -*-
"""
Created on ----------------------

"""

# Used to connect and query the database
import sqlite3
# libs for array use
import numpy as np
# lib containing the predefined K-MEANS in python
from sklearn.cluster import KMeans
# lib used to write on excel files
from xlwt import Workbook 
# the DcGA producing initial centroids
from cGA import cGA 


# Given a vector reduces it, accumulating each "n" values in one (mean value)
def reduce_vector(v: list, n: int) -> list:
    v2 = []
    for i in range(0, len(v), n):
        mean = 0
        for j in range(i, i + n):
            mean += v[j]
        v2.append(mean / n)
    return v2


# Return an array in which each position indicates the index of the city in cluster "i"
def get_sets(cluster, num):
    s = []
    for idx in range(num):
        s.append(
            set(
                [i for i, e in enumerate(cluster) if e == idx]
            )
        )
    return s


def clustering_step_4(cluster_num, feature_num, series, verb,pop,it,pc,pm,NN,D):
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE FOURTH STEP OF CLUSTERING HAS STARTED")
    print("***********************************************************************************************")
    print("")
    print("")
    # connect to the database
    conn = sqlite3.connect('db-reduced.db')
    c = conn.cursor()
    # extract the locations
    locations = c.execute('SELECT DISTINCT location_name FROM data')
    data_loc = locations.fetchall()
    # display some information about the final data displayed
    if verb == 1:
        print("***********************************************************************************************")
        print("IMPORTANT:")
        print("  - The data displayed at the end of step 4 indicates the ultimate results of the clustering.")
        print("  - For each data series, a list of clusters and the name of the cities that belong to them are displayed.")
        print("***********************************************************************************************")
        print("")
        print("")
    # ====== PERFORM CLUSTERING ACCORDING TO # of clusters got from step 1 and the # of months got from step 2 =========
    i = 0  # index to count down the series having been processed ("i" will be only used for displaying information)
    si = 0 # index of the name of excel files per data series
    data = {} # map city -> all data
    for tuple1 in series:  # browse series selected from step 3
        wb = Workbook() # initialise an excel work book
        # print(tuple1[0]) # uncomment to know which data series we is being processed
        si = si + 1  # increment the index of the serie each time one is browsed
        if verb == 1:  # display info about the data series being processed
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("Information n° %i being processed: " % i, tuple1[0])
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("")
            print("")
        data_x_months = np.zeros(15 * 12 // feature_num)  # stores the sample data that will undergo the clustering
        for tuple2 in data_loc:  # browse locations
            # print(tuple2[0])  # uncomment to know which city is being processed
            # ====== RETRIEVE THE RECORDS OF THE GIVEN SERIE FOR THE PROCESSED CITY  ===============================
            records = c.execute('SELECT * FROM data WHERE serie_name = ? AND location_name =  ? ',
                                (tuple1[0][:], tuple2[0][:]))
            data_rec = records.fetchall()
            data_mat = []  # the matrix contains the records of a city for a given series, year and period
            for tuple3 in data_rec:
                # print(tuple3) # uncomment to know the tuple of info being displayed
                data_mat = np.append(data_mat, tuple3[5])  # append the records
            # ===== build-up the matrix of records that will undergo clustering, lines: cities, columns:
            data_mat = reduce_vector(data_mat, feature_num)
            if tuple2[0][:] in data:
                data[tuple2[0][:]].extend(data_mat)
            else:
                data[tuple2[0][:]] = data_mat
            # ==== append the records of the cities =========
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
        cluster_labels = get_sets(clust.labels_, cluster_num)
        # print (clust.cluster_centers_) # print coordinate of each cluster's centre
        # print (clust.inertia_) # print the inertia of the final cluster = sum sum wi||xi-mi||^2
        #use for writing results down on excel file
        part_1 = str(si)
        part_2 = '.xls'
        row = 0 # initialise the row of excel sheet to be written on
        sheet = wb.add_sheet('clustering_data')   # add_sheet is used to create sheet.
        sheet.write(1, 0,tuple1[0]) # write down the name of serie 
        # display the clusters and the cities that belongs to each cluster
        for ind in range(0,cluster_num):
            row = row + 2 #☻ increment the row to leave two lines between each clusters
            print("===================================================================")
            print("The cities that belong to group (i.e. cluster) n° %i are:" %(ind+1))
            print("===================================================================")    
            for city in cluster_labels[ind]:
                row = row +1
                sheet.write(row, 0,data_loc[city][0]) 
                print(data_loc[city][0])
            print("")
            print("")         
        row = row+1
        sheet.write(row, 0,clust.inertia_) # write down the inertia of the clustering of the processed data series.       
        wb.save(part_1+part_2) # write down on the excel file
    # Clustering considering all series together
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print("Using all the series together")
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print("")
    print("")
    data_np = np.array(list(data.values()))
    data_loc = list(data.keys())
    clust = KMeans(n_clusters=cluster_num, init='k-means++', n_init=10, max_iter=300, tol=0.0001, verbose=0,
                   random_state=None, copy_x=True, algorithm='auto').fit(data_np)
    cluster_labels = get_sets(clust.labels_, cluster_num)
    # display the clusters and the cities that belongs to each cluster
    for ind in range(0, cluster_num):
        print("===================================================================")
        print("The cities that belong to group (i.e. cluster) n° %i are:" % (ind + 1))
        print("===================================================================")
        for city in cluster_labels[ind]:
            print(data_loc[city])
        print("")
        print("")

    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE FOURTH STEP OF CLUSTERING HAS FINISHED")
    print("***********************************************************************************************")
