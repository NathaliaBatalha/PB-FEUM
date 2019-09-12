# PB-FEUM
This is a demonstration of the PB-FEUM, an algorithm capable of computing spatially varying distribution of material properties. 

This Demo is for a 2D case. 

The material properties generated for the Virtual Experiment, assumed a random correlated field with scale of 0.25, cross-correlation between variables of 0.5 and coefficient of variation of 0.1. 

The mean values for Young's modulus and Poisson's ratio are 29269MPa and 0.203, respectively. The uniform pressure over the plate is 19.5MPa.

Please follow the steps:

1 - Please clone the repository. 
2 - Update the path on line 23 of 'Abaqus_script_100el.py'. The path should be where your repository is saved. 
3 - Choose the material properties file to be simulated, changing the .txt name on line 28 of 'Abaqus_script_100el.py'.
4 - Open Abaqus Cae and run the script 'Abaqus_script_100el.py'. 
5 - Abaqus documentation provides the steps to export solutions, such as strain and stress fields. Please check: http://130.149.89.49:2080/v6.11/index.html

 
