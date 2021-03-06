#!/usr/bin/python3

"""
Run the following code from root directory:

python3.6 -m web.gen_models
"""

from sklearn.externals import joblib

from genrec.classifier import Classifier
from genrec.config import *
from genrec.db import Dataset
from genrec.features import FeatureExtractor
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Testcases -> list of (classifier parameters, display name) tuples
testcases = [
    ({'type': 'knn', 'clf_kwargs': { 'n_neighbors': 3}, 'name': 'kNN_3' }, 'kNN-3'),
    ({'type': 'knn', 'clf_kwargs': { 'n_neighbors': 5}, 'name': 'kNN_5' }, 'kNN_5'),
    ({'type': 'knn', 'clf_kwargs': { 'n_neighbors': 7}, 'name': 'kNN_7' }, 'kNN_7'),
    ({'type': 'knn', 'clf_kwargs': { 'n_neighbors': 9}, 'name': 'kNN_9' }, 'kNN_9'),
    ({'type': 'svm', 'clf_kwargs': { 'kernel': 'linear', 'cache_size': 2000 }, 'name': 'SVM_Linear' }, 'Linear Kernel SVM'),
    ({'type': 'svm', 'clf_kwargs': { 'kernel': 'rbf', 'cache_size': 2000, 'gamma': 0.15 }, 'name': 'SVM_RBF' }, 'RBF Kernel SVM'),
    ({'type': 'dtree', 'clf_kwargs': { 'criterion': 'entropy'}, 'name': 'Decision_Tree' }, 'Decision Tree'),
    ({'type': 'ada', 'clf_kwargs': { 'n_estimators': 50, 'learning_rate': 0.5 }, 'name': 'AdaBoost' }, 'AdaBoost'),
    ({'type': 'gnb', 'clf_kwargs': { }, 'name':'GaussianNB' }, ' Gaussian Naive-Bayes'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (20,) }, 'name': 'MLP_1S' }, 'MLP_1S'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (50,) }, 'name': 'MLP_1M' }, 'MLP_1M'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (100,) }, 'name': 'MLP_1L'}, 'MLP_1L'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (20, 20) }, 'name': 'MLP_2S' }, 'MLP_2S'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (50, 50) }, 'name': 'MLP_2M' }, 'MLP_2M'),
    ({'type': 'mlp', 'clf_kwargs': { 'hidden_layer_sizes': (100,100) }, 'name': 'MLP_2L'}, 'MLP_2L'),
]

def generate(dirpath='./web/classifiers/gtzan'):
    ft = FeatureExtractor()
    ds = Dataset(GENRES, ft)

    # If already have saved the timbral features
    ds.load_from_file('./db/timbral.json')

    X, y = ds.get_data_as_arrays()

    # encode genre labels
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)

    # normalize data before training
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    for clf_params, display_name in testcases:
        continue
        # Initialize classifier
        clf_params['dataset'] = 'gtzan'
        clf = Classifier(**clf_params)

        clf.fit(X, y) # train
        clf.to_file(f'{dirpath}/{clf_params["name"]}');

    # save scaler & encoder
    joblib.dump(scaler, f'{dirpath}/clf_scaler')
    joblib.dump(encoder, f'{dirpath}/clf_encoder')

if __name__ == '__main__':
    generate()

