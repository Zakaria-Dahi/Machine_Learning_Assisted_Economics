# -*- coding: utf-8 -*-
"""
Created on -------------------
"""

# Used to connect and query the database
import sqlite3
# libs for array use
import numpy as np
# lib containing the predefined K-MEANS in python
from sklearn.cluster import KMeans
# lib used to generate the possible permutation of N digits
from itertools import permutations
# the DcGA producing initial centroids
from cGA import cGA 
# lib used to write on excel files
from xlwt import Workbook 

# Given a vector reduces it, accumulating each n values in one (mean value)
def reduce_vector(v: list, n: int) -> list:
    v2 = []
    for i in range(0, len(v), n):
        mean = 0
        for j in range(i, i + n):
            mean += v[j]
        v2.append(mean / n)
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


# distance between two clustersing (it tests all possible combinations)
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


def clustering_step_3(cluster_num, feature_num, N, verb,pop,it,pc,pm,NN,D):
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE THIRD STEP OF CLUSTERING HAS STARTED")
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
    # display some information about the final data displayed
    if verb == 1:
        print("***********************************************************************************************")
        print("IMPORTANT:")
        print("  - The data displayed at the end of step 3 indicates the data series to be maintained in the 4th step.")
        print("***********************************************************************************************")

        # ====== PERFORM CLUSTERING ACCORDING TO # of clusters got from step 1 and the # of months got from step 2 =========
    i = 0  # index to count down the series having been processed ("i" will be only used for displaying information)
    # will store the number of the cluster to whom each city belongs and this for every data series
    cluster_labels = np.zeros(52)
    # stores the description of the data series (will be used to return the name of the data series that will be
    # considered for clustering in step 4)
    series_desc = np.zeros(1)
    for tuple1 in data_ser:  # browse series
        i = i + 1  # increment the index of the serie each time one is browsed
        if verb == 1:  # display info about the data series being processed
            print("Information n° %i being processed: " % i, tuple1[0])
        data_x_months = np.zeros(15 * 12 // feature_num)  # stores the sample data that will undergo the clustering
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
            data_mat = reduce_vector(data_mat, feature_num)
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
        cluster_labels = np.vstack((cluster_labels, clust.labels_))  # append the result of the clustering
        num_series = i  # stores the number of series contained in the database
        series_desc = np.append(series_desc, tuple1)  # append the name of the data series being processed
    # ======== COMPUTE DISTANCE BETWEEN N!xN PAIRS OF DATA SERIES =========
    series_desc = np.delete(series_desc, 0, 0)  # delete the first unuseful zero
    cluster_labels = np.delete(cluster_labels, 0, 0)  # delete the unuseful set of zeros at the begining
    # print(len(cluster_labels)) # uncomment to know the number of feature configurations considered
    # print(len(cluster_labels[0])) # uncomment to know the number of cities considered
    # print(cluster_labels) # uncomment to print the result of clustering in each of the 6 feature configurations    
    distance_clustering = []  # will contain the distances between the clusteering of each pair of data series
    pairs_index = np.zeros(2)  # will contain the index of each pair of data series
    # compute the distance between the clustering of each pair of data series
    for i in range(0, num_series):
        for j in range(i + 1, num_series):
            # compute the distance between the data series of each pair
            distance = distance_clusters(cluster_labels[i][:], cluster_labels[j][:], cluster_num)
            # append the distance of the processed pairs of data series to the list of previously-computed distances
            distance_clustering.append(distance)
            # add the index of the processed pair of data series
            pairs_index = np.vstack((pairs_index, [i, j]))
            # display the distance between the clustering
            if verb == 1:
                print("The distance between the data series", (i + 1), "and ", (j + 1), "is:", distance)
    pairs_index = np.delete(pairs_index, 0, 0)  # delete the first line of uneuseful zeros
    # convert the array into numpy array so that .argsort works (see next line)
    distance_clustering = np.array(distance_clustering)
    # extract the pair of series having a distance <= N
    indx = []
    for i in range(0, len(distance_clustering)):
        if distance_clustering[i] <= N:
            indx = np.append(indx, i)

    data_series_list = np.zeros(1)
    if indx is not []:  # to avoid the case where no pair of series has a distance <= N
        LS = np.zeros(2)
        for i in range(0, len(indx)):
            LS = np.vstack((LS, pairs_index[int(indx[i])][:]))
        LS = np.delete(LS, 0, 0)  # delete the line of uneuseful zeros
        series_index = np.unique(LS)
        for i in range(num_series):
            if i not in series_index:
                data_series_list = np.vstack((data_series_list, series_desc[i]))
        if verb == 1:
            print(f"{len(data_series_list) - 1} data series automatically added: {data_series_list[1:]}")
        # extract the number of times in which each series appears in the LS extracted pairs
        while LS != []:
            series_index, occurence = np.unique(LS, return_counts=True)
            indx_serie_maintain = (-occurence).argsort()[:1]
            # append the name of the data series to be maintained in step 4 of clustering
            data_series_list = np.vstack((data_series_list, series_desc[int(series_index[indx_serie_maintain[0]])]))
            # delete the pairs of series that includes the series that just has been maintained
            LS_temp = np.zeros(2)  # a temporary list of series that will consisted LS for the next iteration
            for i in range(0, len(LS)):
                if (LS[i][0] != series_index[indx_serie_maintain[0]]) and (
                        LS[i][1] != series_index[indx_serie_maintain[0]]):
                    LS_temp = np.vstack((LS_temp, LS[i][:]))
            LS_temp = np.delete(LS_temp, 0, 0)
            LS = LS_temp
    data_series_list = np.delete(data_series_list, 0, 0)  # delete the first cell of unuseful zero
    # store the list of maintened data series
    wb = Workbook() # open a new workbood
    sh = wb.add_sheet('data') # add a new sheet
    for index_series in range(len(data_series_list)):
         record = data_series_list[index_series]
         record_2 = record[0]
         sh.write(index_series,0,record_2) # write down the distance in excel file       
    wb.save('step3_data.xls')  # save the wokbook     
    # display the final result of the execution            
    print("***********************************************************************************************")
    print(f"The {len(data_series_list)} data series to be maintained during the 4th step are: \n", data_series_list)
    print("***********************************************************************************************")

    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE THIRD STEP OF CLUSTERING HAS FINISHED")
    print("***********************************************************************************************")
    return data_series_list
