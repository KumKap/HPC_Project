from mpi4py import MPI
import math
import pandas
import random
import numpy as np
import xlsxwriter
import timeit


def create_set(n):
    setOfNumbers = set()
    while len(setOfNumbers) < n:
        setOfNumbers.add(random.randint(0, 9999))
    return setOfNumbers


def cluster_assignment(k_x, k_y, recv_x, recv_y, assign, num_of_processes):
    k_min_index = 0
    num_of_clusters = len(k_x)
    length = len(recv_x)
    for i in range(0, length):
        min_dist = 10000000
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
    return assign

# def cluster_assignment(k_x, recv_x, assign, num_of_processes):
#     k_min_index = 0
#     num_of_clusters = len(k_x)
#     length = len(recv_x)
#     for i in range(0, length):
#         min_dist = 10000000
#         for j in range(num_of_clusters):
#             x = abs(recv_x[i] - k_x[j])
#             temp_dist = x
#             # new minimum distance found
#             if (temp_dist < min_dist):
#                 min_dist = temp_dist
#                 k_min_index = j
#         # update the cluster assignment of this data points
#         assign[i] = k_min_index
#     return assign

# def calculate_Kmeans(k_means_x, data_x_points,  k_assignment, num_of_clusters, no_of_elements):
#     for i in range(num_of_clusters):
#         total_x = 0
#         numOfpoints = 0
#         for j in range(no_of_elements):
#             if (k_assignment[j] == i):
#                 total_x += data_x_points[j]
#                 numOfpoints = numOfpoints + 1
#
#         if (numOfpoints != 0):
#             print("Cluster point: ",k_means_x[i], " has ",numOfpoints, " points assigned to it." )
#             k_means_x[i] = total_x // numOfpoints
#
#     return  k_means_x


def calculate_Kmeans(k_means_x, k_means_y, data_x_points, data_y_points, k_assignment, num_of_clusters, no_of_elements):
    for i in range(num_of_clusters):
        total_x = 0
        total_y = 0
        numOfpoints = 0
        for j in range(no_of_elements):
            if (k_assignment[j] == i):
                total_x += data_x_points[j]
                total_y += data_y_points[j]
                numOfpoints = numOfpoints + 1

        if (numOfpoints != 0):
            #print("Cluster point: ",k_means_x[i], ",",k_means_y[i], " has ",numOfpoints, " points assigned to it." )
            #print("Total of x: ",total_x, " Total of y: ",total_y)
            k_means_x[i] = total_x // numOfpoints
            k_means_y[i] = total_y // numOfpoints
    return  k_means_x, k_means_y

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

x_data = None
y_data = None
x_points = []
y_points = []
numOfClusters = None
length = None
x_numpy = None
y_numpy = None
k_means_x = []
k_means_y = []
assignment_k = []

if rank == 0:

    excel_data_x = pandas.read_excel('dataset.xlsx', sheet_name='HPC', header=None, usecols="A")
    excel_data_y = pandas.read_excel('dataset.xlsx', sheet_name='HPC', header=None, usecols="B")
    x_data = excel_data_x[0].tolist()
    y_data = excel_data_y[1].tolist()
    x_points = x_data
    y_points = y_data
    # x_data = x_data[0:1000]
    # y_data = y_data[0:1000]
    # # print(y_data[0:100])

    length_x = len(x_data)
    length_y = len(y_data)

    if (length_x != length_y):
        print("Unequal dataset found. Program terminated!")
        exit(1)
    #del(x_data)
    #del (y_data)


    numOfClusters = 4
    numOfClusters = comm.bcast(numOfClusters, root=0)
    length = comm.bcast(length_y, root=0)

    rand_set = create_set(4)
    assignment_k = [0] * length
    # assignment_k[0] = 1
    # assignment_k[1999] = 2
    # assignment_k[2000] = 3
    # assignment_k[3999] = 4
    # assignment_k[4000] = 5
    # assignment_k[5999] = 6
    # assignment_k[6000] = 7
    # assignment_k[7999] = 8

    assignment_k = comm.bcast(assignment_k, root=0)
    for i in rand_set:
        k_means_x.append(x_data[i])
        k_means_y.append(y_data[i])
    # print(k_means_x)

    x_numpy = np.array(x_data, dtype="i").reshape(size,length_y//size)
    y_numpy = np.array(y_data, dtype="i").reshape(size,length_y//size)


else:
    numOfClusters = comm.bcast(numOfClusters, root=0)
    length = comm.bcast(length, root=0)
    assignment_k = comm.bcast(assignment_k, root=0)
    #print('rank', rank, 'knows that are:', numOfClusters, " clusters")
    #print('rank', rank, 'knows that are:', length, " clusters")

# mpiexec -n numprocs python -m mpi4py pyfile
# mpiexec -n 3 python -m mpi4py kmeans.py
start = timeit.default_timer()

x_data = comm.scatter(x_numpy, root=0)
y_data = comm.scatter(y_numpy, root=0)
#print('rank', rank, 'has data:', x_data, y_data)
k_assignment = np.array(assignment_k, dtype='i').reshape(size, length // size)

for i in range(100):
    k_means_x = comm.bcast(k_means_x)
    k_means_y = comm.bcast(k_means_y)
    recv_assignment = comm.scatter(k_assignment, root=0)
    #print('rank', rank, 'has centroids:', k_means_x) ,# k_means_y)
    #print('rank', rank, 'has centroids:', )
    #print('rank', rank, 'has assigment:', recv_assignment)
    assigned_at = cluster_assignment(k_means_x, k_means_y, x_data, y_data, recv_assignment, size)
    #print("Assigned at:", assigned_at)
    comm.Gather(assigned_at, k_assignment, root=0)
    # print(k_assignment)
    # print(type(k_assignment))
    # print(len(k_assignment))
    temp_assign = k_assignment.reshape(length, 1)
    if (rank == 0):
        k_means_x, k_means_y= calculate_Kmeans(k_means_x, k_means_y, x_points, y_points, temp_assign, numOfClusters, length)
    # print("At iteration:",i, "Centroids are:",k_means_x, k_means_y)

if (rank == 0):
    print(k_means_x, k_means_y)
stop = timeit.default_timer()

print('Time: ', stop - start)


if(rank == 0):
    workbook = xlsxwriter.Workbook('dataset6.xlsx')
    worksheet = workbook.add_worksheet("result6")
    row = 0
    col = 0
    n = 10000
    temp_assign = k_assignment.reshape(length, 1)
    for i in range(n):
        x = x_points[i]
        y = y_points[i]
        z = int(temp_assign[i])
        cx = k_means_x[z]
        cy = k_means_y[z]
        worksheet.write(row, col, x)
        worksheet.write(row, col + 1, y)
        worksheet.write(row, col + 2, cx)
        worksheet.write(row, col + 3, cy)
        row += 1
    workbook.close()