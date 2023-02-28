# -*- coding: utf-8 -*-
"""
Created on ----------------------------
"""

# Used to connect and query the database
import sqlite3
# libs for array use, plots, etc.
import numpy as np
# import matplotlib.pyplot as plt
# lib containing the predefined K-MEANS in python
from sklearn.cluster import KMeans
# lib used to identify programmatically the elbow 
from kneed import KneeLocator
# lib to compute the median of elbows
import statistics
# the DcGA producing initial centroids
from cGA import cGA 
# lib used to write on excel files
from xlwt import Workbook 

def clustering_step_1(verb,pop,it,pc,pm,NN,D):
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE FIRST STEP OF CLUSTERING HAS STARTED")
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

    if verb == 1:
        print("***********************************************************************************************")
        print("IMPORTANT:")
        print("  - The data displayed for each serie is a 1x11 array.")
        print("  - The 10 first values are the results of the clustering (i.e.dispertion) using 1 .. 10 clusters.")
        print("  - The index of the value represents the number of clusters used.")
        print("  - The 11th value is the value of the elbow (ideal number of clusters to be used).")
        print("- At the end of execution, the ideal number of clusters to be used for the clustering (i.e. Medians of "
              "all the elbows).")
        print("***********************************************************************************************")

    # ============================================== EXTRACT THE 33 SERIES =============================================
    i = 0  # index to count down the series having been processed
    stored_elbows = []  # used to stock the value of elbows found for each serie of information
    record_data = np.zeros(11) # will stock the final results written on excel file
    for tuple1 in data_ser:
        i = i + 1  # increment the idex of the serie each time one is browsed
        displayed_data = []  # it is the 1x11 values array that contains the value of dispertion when applying
        # cluseting using 1 .. 10 clusters and the 11th value is the value of the elbow
        data_all = np.zeros(180)  # just used because vstack needs not null matrix
        if verb == 1:
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("Information n° %i being processed: " % i,
                  tuple1[0])  # uncomment to know which serie you are browsing
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        for tuple2 in data_loc:
            # print(tuple2[0]) # uncomment to know which city you are browsing
            # ====== RETRIEVE ALL THE RECORDS (15x12) OF THE GIVEN SERIE FOR THE PROCESSED CITY  =======================
            records = c.execute('SELECT * FROM data WHERE serie_name = ? AND location_name =  ? ',
                                (tuple1[0][:], tuple2[0][:]))
            data_rec = records.fetchall()
            data_mat = []  # the matrix that will contain the records of a city for a given serie, year and period
            for tuple3 in data_rec:
                # print(tuple3) # uncomment to know the tuple of info being displayed
                data_mat = np.append(data_mat, tuple3[5])  # append the records
            # ===== build-up the matrix of records that will undergo clustering, lines: cities, columns: records of
            # the cities (180:15 years x12 months) =========
            data_all = np.vstack((data_all, data_mat))
        data_all = np.delete(data_all, 0, 0)  # delete the first row of unuseful zeros (see above)
        # print(len(data_all[0])) # uncomment to check the number of records
        # print(len(data_all))  # uncomment to check the number of cities
        dispertion = []  # contains the dispertion value after applying each clustering: will be used for computing
        # the elbow
        # ============= PERFORM K-MEANS CLUSTERING USING 1 .. 10 CENTROIDS =============================================
        dim = len(data_all[:,0]) # extract the number of cities = size of te GA's individual
        for centro in range(10):
            # compute the initial centroids via DcGA
            centroids = cGA(pop,dim,it,pc,pm,data_all,centro,NN,D)
            # perform the K-means clustering: info about parameters can be found in
            # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
            clust = KMeans(n_clusters=centro + 1, init=centroids, n_init=10, max_iter=300, tol=0.0001, verbose=0,
                           random_state=None, copy_x=True, algorithm='auto').fit(data_all)
            # print(clust.labels_) # uncomment to observe the labels of the clusters to which belong each city print(
            # clust.inertia_) # uncomment to observe the value of dispertion: sum of squared distances between each
            # city and nearest centroid
            dispertion = np.append(dispertion, clust.inertia_)  # append the dispertion computing using x centroids
            # ============ USED TO PLOT THE RESULT OF THE CLUSTERING : cannot plot all the 180 features/sample =========
            # plt.figure(clear =True)
            # plt.plot()
            # plt.scatter(data_all[:,0],data_all[:,1], c=y_pred) 
            # plt.title("Results After Applying K-means with %i Clusters" % (centro+1))
            # ==========================================================================================================
        # print(dispertion) # uncomment to display the array containing all the dispertion values
        displayed_data = np.append(displayed_data, dispertion)  # append the result of clustering using 1 .. 10 clusters
        # ====== used to plot the evolution of dispertion to extract the elbow manually  ========
        # plt.plot(dispertion)
        # plt.xlabel("# of clusters")
        # plt.ylabel("value of dispertion")
        # ====== EXTRACT THE ELBOW PROGRAMMATICALLY  ========
        elbow = KneeLocator(range(1, 11), dispertion, curve="convex", direction="decreasing")
        # print(elbow.elbow) # uncomment if you want to display the elbow computed
        stored_elbows = np.append(stored_elbows, elbow.elbow)  # append the elbow to the array stocking elbows
        displayed_data = np.append(displayed_data, elbow.elbow)  # append the elbow to the final result (1x11 array)
        record_data = np.vstack((record_data,displayed_data)) # vertically append the results for the processed clustering
        if verb == 1:
            print(displayed_data)  # print the clustering data (1x11 array: 10 dispertion values of clustering +
            # value of the elbow)
    record_data = np.delete(record_data,0,0) # delete the first row of unuseful zeros
    if verb == 1:
        print("***********************************************************************************************")
        print("Ideal # of clusters to be used for the clustering (Median of elbows) is %i: " % statistics.median(
            stored_elbows))
        print("***********************************************************************************************")
    print("***********************************************************************************************")
    print("                      THE PROCESSING OF THE FIRST STEP OF CLUSTERING HAS FINISHED")
    print("***********************************************************************************************")
    """
    write down results on the excel file
    """
    print(record_data) # print the recorded data on console
    wb = Workbook() # open a new workbood
    sh = wb.add_sheet('data') # add a new sheet
    for index1 in range (i):
        for index2 in range(11): # there is 11 columns
            sh.write(index1,index2,record_data[index1][index2])
    wb.save('step1_data.xls')  # save the wokbook  
    return int(statistics.median(stored_elbows))
