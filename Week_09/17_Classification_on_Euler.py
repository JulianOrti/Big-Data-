# -*- coding: utf-8 -*-
"""Brain-tumor-classification_on-Euler.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-VU7BdMRUD5N_iu4d63300mqZUvGkUVJ

# Use Euler to run python code

This week, we will see how to run python script on Euler, which might be necessary when you are dealing with large datasets.

For this exercise, we will use data of brain cancer gene expression.

You can find the raw data on Kaggle: https://www.kaggle.com/datasets/brunogrisci/brain-cancer-gene-expression-cumida

## Prepare your environment
"""

# Import libraries
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn import preprocessing
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn import metrics
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA
import time
import random
import json
import os

# Set random seed
random.seed(2022)

"""## Download the data"""

from google.colab import drive

drive.mount("/content/gdrive")

ls /content/gdrive/MyDrive/HS22_Big_Data_Analysis_in_Biomedical_Research_exercises

cd /content/gdrive/MyDrive/HS22_Big_Data_Analysis_in_Biomedical_Research_exercises

envs = json.load(open("kaggle(1).json", "r"))
os.environ["KAGGLE_USERNAME"] = envs['username']
os.environ["KAGGLE_KEY"] = envs['key']

!kaggle datasets list -s 'gene expression'

!mkdir kaggleBrainTumor

cd kaggleBrainTumor

# download the titanic data into the directory you created for it
!kaggle datasets download -d brunogrisci/brain-cancer-gene-expression-cumida

ls

!unzip brain-cancer-gene-expression-cumida.zip

ls

mv Brain_GSE50161.csv /content/gdrive/MyDrive/HS22_Big_Data_Analysis_in_Biomedical_Research_376-1723-00L/week_09/Euler-Lucie/data/

cd /content/gdrive/MyDrive/HS22_Big_Data_Analysis_in_Biomedical_Research_376-1723-00L/week_09/Euler-Lucie/

ls

cd code

# Declare paths
main_path = '../'
data_path = main_path + 'data/'
output_path = main_path + 'output/'

"""## Load the data"""

data = pd.read_csv(data_path + 'Brain_GSE50161.csv')

print(data.head())

print('This dataset is of shape', data.shape)

print('There are', data['samples'].nunique(), 'unique samples in this dataset.')

print('There are', data['type'].nunique(), 'unique phenotypes/labels in this dataset.')
print('The phenotypes present are', data['type'].unique())

"""## Aim of the analysis

We want to determine whether the 5 phenotypes can be predicted based on gene expression data.

Because this dataset includes the expression of 54'677 different genes, we will first write the code on Jupyter using a subset, before running the entire analysis on Euler.

## Subset the data
"""

# select for the first 103 columns, note that this line will be commented out on Euler
data_analysis = data.iloc[:, :102]

# in order to use the same variable name in Jupyter and Euler, you can create a copy of data 
# note that this line will be uncommented on Euler
# data_analysis = data 

print('The dataset used for the analysis is of size', data_analysis.shape)

print('Number of NAs in the dataset')

# We will only print the columns in which data is missing
for col in data_analysis.columns:
  if data_analysis[col].isna().sum() != 0:
    print('There are', data_analysis[col].isna().sum(), 'in column', col)

print('For-loop done') # adding this line allows you to have an output even if no column has missing data

# Scale the data, excluding the first 2 columns (categorical)

cols = data_analysis.columns[~data_analysis.columns.isin(['samples', 'type'])]
data_analysis[cols] = preprocessing.scale(data_analysis[cols], axis=0)

"""## Dimensionality reduction

### t-SNE

For more information on the t-SNE implementation in Python, see the [sklearn documentation for t-SNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html)
"""

twodproj = TSNE(n_components=2).fit_transform(data_analysis[cols])

plt.figure(figsize  = (10,10))

patient_phenotypes = data_analysis['type']
unique_labels = data_analysis['type'].unique()

for i in unique_labels:
    plt.scatter(twodproj[patient_phenotypes == i, 0], twodproj[patient_phenotypes == i, 1], label=i)
plt.title('t-SNE dimensionality reduction')
plt.legend()
plt.show()

# Don't forget to save your plot, especially when you work on Euler
plt.savefig(output_path + 'tSNE_plot.png')

"""## Class prediction"""

t0_gene = time.time()

# X is a dataframe with all the features/variables that we want to use for the classification
X = data_analysis[cols]
# y is a list containing the label to classify
y = data_analysis['type'].tolist()

'''
We first need to split out data into training and testing sets
We will fit the model on the training set and test it on the testing set
Note: we stratify the splitting according to the labels 
such that both the train and testing sets have a similar distribution
'''

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 2022, stratify = y)

# Specify the model to use and the hyperparameters
rf = ensemble.RandomForestClassifier(max_depth = 25, 
                                      criterion = "gini", 
                                      random_state = 2022)
# Fit the train data
rf = rf.fit(X_train, y_train)

# Predict the labels in the test set based on the model learnt on the train set
y_pred = rf.predict(X_test)

confusion_matrix(y_test, y_pred)

# Visualise the prediction results in a confusion matrix

plt.figure(figsize = (10,10))
plot_confusion_matrix(rf, X_test, y_test, cmap = plt.cm.Blues)
plt.title('Confusion matrix')
plt.xticks(rotation=90)
plt.show()

# Don't forget to save your plot, especially when you work on Euler
plt.savefig(output_path + 'confusion_plot.png')

t1_gene = time.time()

total_gene = t1_gene - t0_gene
print('It took', round(total_gene, 3), 'seconds to run the prediction using the gene expression data.')

# Output the classification report including multiple metrics

report = classification_report(y_test, y_pred, output_dict = True)
print(classification_report(y_test, y_pred))

# You can also save this report as a .csv file
report_dataframe = pd.DataFrame.from_dict(report)
report_dataframe.to_csv(output_path + 'class-prediction_report.csv')

"""### Class prediction including GridSearchCV

For more information about the implementation of grid search cross validation in python, you can refer to the corresponding sklearn page: [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
"""

t0_gene_CV = time.time()

# Declare the model to use, without specifying parameters (except from the seed here)
rf = ensemble.RandomForestClassifier(random_state = 2022)

# Decide the hyperparameters to be tested
min_samples_split = [2, 3, 4]                                      
max_depth = [5, 10, 25, 50, None]
criterion = ['gini','entropy']

# Combine all parameters in a dictionary
parameters_rf = dict(min_samples_split = min_samples_split,
                     criterion = criterion,
                     max_depth = max_depth)
print(parameters_rf)

# Train random forest model with combinations of all hyperparameters above using GridSearchCV
# GridSearchCV will find the hyperparameters that will give you the best predictions in cross validation according to the scoring method chosen
gridrf = GridSearchCV(rf, parameters_rf, cv = 10, scoring = 'accuracy')
gridrf.fit(X_train, y_train)
print(gridrf.best_params_)
t1_gene_CV = time.time()

# Predict the labels in the test set based on the model learnt on the train set
y_pred_CV = gridrf.predict(X_test)

# Visualise the prediction results in a confusion matrix

plt.figure(figsize = (10,10))
plot_confusion_matrix(gridrf, X_test, y_test, cmap = plt.cm.Blues)
plt.title('Confusion matrix')
plt.xticks(rotation = 90)
plt.show()

# Don't forget to save your plot, especially when you work on Euler
plt.savefig(output_path + 'confusion_plot_CV.png')

t1_gene_CV = time.time()

total_gene_CV = t1_gene_CV - t0_gene_CV
print('It took', round(total_gene_CV, 3), 'seconds to run the prediction using the gene expression data.')

# Output the classification report including multiple metrics

report_CV = classification_report(y_test, y_pred_CV, output_dict = True)
print(classification_report(y_test, y_pred_CV))

# You can also save this report as a .csv file
report_dataframe_CV = pd.DataFrame.from_dict(report_CV)
report_dataframe_CV.to_csv(output_path + 'class-prediction-CV_report.csv')

"""## Exercises

It is now your turn to play around with this dataset, first using a subset and then the entire set of data on Euler.

### Part a

Run a principal component (PC) analysis (PCA).
 - Visualise the different types of tumor according to the first 2 PCs.
 - Do the group separate well? 
 - How much of the variance is explained from those 2 PCs? (Hint: have a look at the output in [the PCA scikit-learn documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html))
 - How many components would you need to consider in order to capture 50% of the variance?
 
### Part b

We classified the different tumour types based on gene expression. This time, perform a similar classification but using the PCs instead of gene expression directly (choose the number of PCs that explain 50% of the variance). Don't forget that the data should be split in train and test sets, even to perform PCA. How is the model performing when using PCs compared to gene expression? How long does it take compared to the classification with the gene expression?

### Part a

### Part b
"""