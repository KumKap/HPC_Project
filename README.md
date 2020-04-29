# HPC_Project
HPC Project (Sem 8, MU) based on optimizing KMEANS (2D only) using MPI in Python.<br/>
Use pip install -r requirements.txt to setup the environment.<br/>
Download MS MPI from https://www.microsoft.com/en-us/download/details.aspx?id=57467 <br/>
Set the MSMPI path (by default C:\Program Files\Microsoft MPI\Bin) in the %PATH% environment variable. <br/>
Run using command: mpiexec -n 2 python -m mpi4py kmeans2.py new_2020_3.xlsx 2 xlsx YES <br/>
Parameters: mpiexec -n num_of_process python -m mpi4py kmeans.py filename clusters type head <br/>
You will also require xampp server if you want to run the web app(optional).<br/>
Folder HPC consist of Web App interface for the project. Directly place it in htdocs of XAMPP Folder.<br/>
Folder HPC_Project (inside HPC) has two variation of Kmeans. <br/>
Kmeans2 works relatively better as it optimizes the calculation of new centroids.<br/>
Folder Dataset contains validation sets for the program. Data file name indicates the actual number of proper cluster sets in the file.<br/>
dataset.py in Dataset Folder can help you create your own customized dataset.
