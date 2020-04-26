from mpi4py import MPI
import math
import pandas
import random
import numpy as np
import timeit
import sys
import json
import matplotlib.pyplot as plt



Result = {
  "Name": "Output"
}



def create_set(n, limit):
    setOfNumbers = set()
    while len(setOfNumbers) < n:
        setOfNumbers.add(random.randint(0, limit))
    return setOfNumbers

def add_list(arr1, arr2, x):
    l = len(arr1)
    for i in range(l):
        arr1[i] = arr1[i] + arr2[i]
    return  arr1
#mpiexec -n 2 python -m mpi4py C:/Users/KumKap/PycharmProjects/BE/HPC_Project/kmeans2.py new_2020.xlsx 2 xlsx YES
def cluster_assignment(k_x, k_y, recv_x, recv_y, assign, num_of_processes):
    k_min_index = 0
    num_of_clusters = len(k_x)
    length = len(recv_x)
    total_x = [0] * num_of_clusters
    total_y = [0] * num_of_clusters
    num_of_elements = [0] * num_of_clusters
    for i in range(0, length):
        min_dist = 100000000
        for j in range(num_of_clusters):
            x = abs(recv_x[i] - k_x[j])
            y = abs(recv_y[i] - k_y[j])
            temp_dist = math.sqrt((x * x) + (y * y))
            # new minimum distance found
            if (temp_dist < min_dist):
                min_dist = temp_dist
                k_min_index = j
        # update the cluster assignment of this data points
        assign[i] = k_min_index
        total_y[k_min_index] += recv_y[i]
        total_x[k_min_index] += recv_x[i]
        num_of_elements[k_min_index] += 1
    return assign, total_x, total_y, num_of_elements


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

argumentList = sys.argv
# mpiexec -n 3 python -m mpi4py kmeans.py filename clusters type head
head = argumentList[4]
type = argumentList[3]
numOfClusters = int(argumentList[2])
file_name = argumentList[1]
x_data = None
y_data = None
x_points = []
y_points = []
length = None
x_numpy = None
y_numpy = None
k_means_x = []
k_means_y = []
assignment_k = []
#Average time for all process: 7.398615250000001 seconds
#2.75223214286
#Maximum time for process: 7.4000055 seconds
#2.70400194262


#Average time for all process: 12.3848916 seconds
#Maximum time for process: 12.3859122 seconds
if rank == 0:

    if (type == "xlsx"):
        excel_data_x = pandas.read_excel(file_name, sheet_name='HPC', header=None, usecols="A")
        excel_data_y = pandas.read_excel(file_name, sheet_name='HPC', header=None, usecols="B")
        x_data = excel_data_x[0].tolist()
        y_data = excel_data_y[1].tolist()
        if (head == 'YES'):
            x_data.pop(0)
            y_data.pop(0)
    else:
        excel_data_x = pandas.read_csv(file_name, header=None)
        excel_data_y = pandas.read_csv(file_name, header=None)
        x_data = excel_data_x[0].tolist()
        y_data = excel_data_y[0].tolist()
        if (head == 'YES'):
            x_data.pop(0)
            y_data.pop(0)

    length_x = len(x_data)
    length_y = len(y_data)
    if (length_x != length_y):
        print("Unequal dataset found. Program terminated!")
        exit(1)

    if length_y % size != 0:
        temp = size - (length_y % size)
        length_y += temp
        length_x += temp
        pad = [0] * temp
        x_data = x_data + pad
        y_data = y_data + pad

    x_points = np.array(x_data, dtype=np.float64)
    y_points = np.array(y_data, dtype=np.float64)
    numOfClusters = comm.bcast(numOfClusters, root=0)
    length = comm.bcast(length_y, root=0)
    #rand_set = create_set(numOfClusters, length_x - 1)
    rand_set = []
    for j in range(numOfClusters):
        rand_set.append(j)

    assignment_k = [0] * length
    assignment_k = comm.bcast(assignment_k, root=0)
    for i in rand_set:
        k_means_x.append(x_data[i])
        k_means_y.append(y_data[i])

    k_means_x = np.array(k_means_x, dtype=np.float64)
    k_means_y = np.array(k_means_y, dtype=np.float64)
    x_numpy = np.array(x_data, dtype=np.uint64).reshape(size,length_y//size)
    y_numpy = np.array(y_data, dtype=np.uint64).reshape(size,length_y//size)

else:
    numOfClusters = comm.bcast(numOfClusters, root=0)
    length = comm.bcast(length, root=0)
    assignment_k = comm.bcast(assignment_k, root=0)

counterSumOp = MPI.Op.Create(add_list, commute=True)
start = timeit.default_timer()
x_data = comm.scatter(x_numpy, root=0)
y_data = comm.scatter(y_numpy, root=0)
k_assignment = np.array(assignment_k, dtype='i').reshape(size, length // size)

for i in range(150):
    k_means_x = comm.bcast(k_means_x)
    k_means_y = comm.bcast(k_means_y)
    recv_assignment = comm.scatter(k_assignment, root=0)
    assigned_at, total_x, total_y, num_of_elements = cluster_assignment(k_means_x, k_means_y, x_data, y_data, recv_assignment, size)

    comm.Gather(assigned_at, k_assignment, root=0)
    Total_x = comm.reduce(total_x, op=counterSumOp, root=0)
    Total_y = comm.reduce(total_y, op=counterSumOp, root=0)
    Total_n = comm.reduce(num_of_elements, op=counterSumOp, root=0)

    temp_assign = k_assignment.reshape(length, 1)
    if (rank == 0):
        for j in range(numOfClusters):
            if(Total_n[j] > 0):
                k_means_x[j] = Total_x[j]//Total_n[j]
                k_means_y[j] = Total_y[j]// Total_n[j]


stop = timeit.default_timer()
time_taken = stop - start
max_time = comm.reduce(time_taken, op=MPI.MAX, root=0)
avg_time = comm.reduce(time_taken, op=MPI.SUM, root=0)
if(rank == 0):
    avg_time = avg_time/size
    Result['avg_time'] = str(avg_time)
    Result['max_time'] = str(max_time)
    Result['centroid_x'] = str(k_means_x)
    Result['centroid_y'] = str(k_means_y)
    #
    # name = file_name.split(".")
    # workbook = xlsxwriter.Workbook(name[0] + '_output.xlsx')
    # worksheet = workbook.add_worksheet('result')
    # row = 0
    # col = 0
    # n = 10000
    # temp_assign = k_assignment.reshape(length, 1)
    # for i in range(n):
    #     x = x_points[i]
    #     y = y_points[i]
    #     z = int(temp_assign[i])
    #     cx = k_means_x[z]
    #     cy = k_means_y[z]
    #     worksheet.write(row, col, x)
    #     worksheet.write(row, col + 1, y)
    #     worksheet.write(row, col + 2, cx)
    #     worksheet.write(row, col + 3, cy)
    #     row += 1
    # workbook.close()
    #for x in range(numOfClusters):
        #print("Cluster centroid number",x," is:", "%.2f" % round(k_means_x[x], 2), "%.2f" % round(k_means_y[x], 2))
    y = json.dumps(Result)
    plt.scatter(x_points, y_points)
    plt.show()

    # the result is a JSON string:
    print(y)

