# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks_dev/utils.ipynb (unless otherwise specified).

__all__ = ['parallel_apply', 'get_default_args', 'inherit_docstrings', 'make_batches', 'sim_matrix_to_idx_and_score',
           'cosine_similarity', 'cosine_distance', 'similarity_plot', 'sparsify', 'hstack', 'vstack', 'stack',
           'RobustEncoder', 'parallel_apply', 'get_default_args', 'inherit_docstrings', 'make_batches',
           'sim_matrix_to_idx_and_score', 'cosine_similarity', 'cosine_distance', 'similarity_plot', 'sparsify',
           'hstack', 'vstack', 'stack', 'RobustEncoder']

# Cell
from warnings import warn
from inspect import getmembers, isfunction
import inspect

import numpy as np
from scipy import sparse

from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from joblib import Parallel, delayed, parallel_backend

try:
    from sparse_dot_topn import awesome_cossim_topn
except Exception as e:
    warn(f'could not load sparse_dot_topn: {e}')


# Cell
#util funcs and classes
def parallel_apply(func, iterator, n_jobs = -1, backend = 'loky', **func_kwargs):
    with parallel_backend(backend, n_jobs):
        results = Parallel()(delayed(func)(**func_kwargs) for i in iterator)
    return results

def get_default_args(func):
    '''THANKS TO mgilson at https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value'''
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def inherit_docstrings(cls):
    '''
    thanks to Martijn Pieters♦ at https://stackoverflow.com/questions/17393176/python-3-method-docstring-inheritance-without-breaking-decorators-or-violating
    '''
    for name, func in getmembers(cls, isfunction):
        if func.__doc__: continue
        for parent in cls.__mro__[1:]:
            if hasattr(parent, name):
                func.__doc__ = getattr(parent, name).__doc__
    return cls

# Cell
#TODO: implement minkowski distance with sparse_dot_topn
#TODO: implement RBF distance

#export
def make_batches(arr, batch_size = 100):
    '''make batches for batch query'''
    #lst = [i for i in arr]

    if arr.shape[0] < batch_size:
        batches = [arr]
    else:
        n_bs = arr.shape[0] // batch_size
        last_batch = arr.shape[0] - batch_size * n_bs
        batches = []
        i = 0
        for i in range(n_bs):
            yield arr[i * batch_size:(i + 1) * batch_size]

        if last_batch:
            yield arr[(i + 1) * batch_size:]

def sim_matrix_to_idx_and_score(sim_matrix):
    '''
    returns list of indexes (col index of row vector) and scores (similarity value) for each row, given a similarity matrix
    '''
    scores = []
    idxs = []
    for row in sim_matrix:
        idxs.append(row.nonzero()[-1])
        scores.append(row.data)

    return idxs, scores

def cosine_similarity(A, B, topn = 30, remove_diagonal = False, **kwargs):

    A,B = sparsify(A,B)
    A = normalize(A, norm  = 'l2').astype(np.float64)
    B = normalize(B, norm  = 'l2').astype(np.float64)
    dot = awesome_cossim_topn(A, B.T, ntop = topn, **kwargs)

    if remove_diagonal:
        dot.setdiag(0)
        dot.eliminate_zeros()

    return dot


def cosine_distance(A, B, topn = 30, remove_diagonal = False, **kwargs):

    #calculate sim
    dist = cosine_similarity(A, B, topn, remove_diagonal, **kwargs)
    #calculate distance
    dist.data = 1 - dist.data
    return dist

# Cell
def similarity_plot(vector, query_matrix):
    '''
    plots similarity plots like in https://gdmarmerola.github.io/forest-embeddings/
    '''
    return


# Cell
def sparsify(*arrs):
    '''
    makes input arrs sparse
    '''
    arrs = list(arrs)
    for i in range(len(arrs)):
        if not sparse.issparse(arrs[i]):
            arrs[i] = sparse.csr_matrix(arrs[i])

    return arrs

def _robust_stack(blocks, stack_method = 'stack', **kwargs):

    if any(sparse.issparse(i) for i in blocks):
        stacked = getattr(sparse, stack_method)(blocks, **kwargs)
    else:
        stacked = getattr(np, stack_method)(blocks, **kwargs)
    return stacked

def hstack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'hstack', **kwargs)

def vstack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'vstack', **kwargs)

def stack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'stack', **kwargs)


class RobustEncoder(BaseEstimator, TransformerMixin):

    def __init__(self,):
        '''
        A robust one hot encoder. Always return the same amount of nonzero value sin each transformed row.
        Has columns for unknown values
        '''
        return

    def fit(self, X, y = None, **kwawrgs):
        self.ordinalencoder_ = OrdinalEncoder(handle_unknown = 'use_encoded_value', unknown_value = -1).fit(X)

        X = self.ordinalencoder_.transform(X)

        categories = [np.arange(-1, len(cats)) for cats in self.ordinalencoder_.categories_]
        self.onehotencoder_ = OneHotEncoder(categories = categories).fit(X)
        return self

    def transform(self, X, **kwargs):
        X = self.ordinalencoder_.transform(X)
        return self.onehotencoder_.transform(X)

# Cell
from warnings import warn
from inspect import getmembers, isfunction
import inspect

import numpy as np
from scipy import sparse

from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from joblib import Parallel, delayed, parallel_backend

try:
    from sparse_dot_topn import awesome_cossim_topn
except Exception as e:
    warn(f'could not load sparse_dot_topn: {e}')


# Cell
#util funcs and classes
def parallel_apply(func, iterator, n_jobs = -1, backend = 'loky', **func_kwargs):
    with parallel_backend(backend, n_jobs):
        results = Parallel()(delayed(func)(i, **func_kwargs) for i in iterator)
    return results

def get_default_args(func):
    '''THANKS TO mgilson at https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value'''
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def inherit_docstrings(cls):
    '''
    thanks to Martijn Pieters♦ at https://stackoverflow.com/questions/17393176/python-3-method-docstring-inheritance-without-breaking-decorators-or-violating
    '''
    for name, func in getmembers(cls, isfunction):
        if func.__doc__: continue
        for parent in cls.__mro__[1:]:
            if hasattr(parent, name):
                func.__doc__ = getattr(parent, name).__doc__
    return cls

# Cell
#TODO: implement minkowski distance with sparse_dot_topn
#TODO: implement RBF distance

#export
def make_batches(arr, batch_size = 100):
    '''make batches for batch query'''
    #lst = [i for i in arr]

    if arr.shape[0] < batch_size:
        batches = [arr]
    else:
        n_bs = arr.shape[0] // batch_size
        last_batch = arr.shape[0] - batch_size * n_bs
        batches = []
        i = 0
        for i in range(n_bs):
            yield arr[i * batch_size:(i + 1) * batch_size]

        if last_batch:
            yield arr[(i + 1) * batch_size:]

def sim_matrix_to_idx_and_score(sim_matrix):
    '''
    returns list of indexes (col index of row vector) and scores (similarity value) for each row, given a similarity matrix
    '''
    scores = []
    idxs = []
    for row in sim_matrix:
        idxs.append(row.nonzero()[-1])
        scores.append(row.data)

    return idxs, scores

def cosine_similarity(A, B, topn = 30, remove_diagonal = False, **kwargs):

    A,B = sparsify(A,B)
    A = normalize(A, norm  = 'l2').astype(np.float64)
    B = normalize(B, norm  = 'l2').astype(np.float64)
    dot = awesome_cossim_topn(A, B.T, ntop = topn, **kwargs)

    if remove_diagonal:
        dot.setdiag(0)
        dot.eliminate_zeros()

    return dot


def cosine_distance(A, B, topn = 30, remove_diagonal = False, **kwargs):

    #calculate sim
    dist = cosine_similarity(A, B, topn, remove_diagonal, **kwargs)
    #calculate distance
    dist.data = 1 - dist.data
    return dist

# Cell
def similarity_plot(vector, query_matrix):
    '''
    plots similarity plots like in https://gdmarmerola.github.io/forest-embeddings/
    '''
    return


# Cell
def sparsify(*arrs):
    '''
    makes input arrs sparse
    '''
    arrs = list(arrs)
    for i in range(len(arrs)):
        if not sparse.issparse(arrs[i]):
            arrs[i] = sparse.csr_matrix(arrs[i])

    return arrs

def _robust_stack(blocks, stack_method = 'stack', **kwargs):

    if any(sparse.issparse(i) for i in blocks):
        stacked = getattr(sparse, stack_method)(blocks, **kwargs)
    else:
        stacked = getattr(np, stack_method)(blocks, **kwargs)
    return stacked

def hstack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'hstack', **kwargs)

def vstack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'vstack', **kwargs)

def stack(blocks, **kwargs):
    return _robust_stack(blocks, stack_method = 'stack', **kwargs)


class RobustEncoder(BaseEstimator, TransformerMixin):

    def __init__(self,):
        '''
        A robust one hot encoder. Always return the same amount of nonzero value sin each transformed row.
        Has columns for unknown values
        '''
        return

    def fit(self, X, y = None, **kwawrgs):
        self.ordinalencoder_ = OrdinalEncoder(handle_unknown = 'use_encoded_value', unknown_value = -1).fit(X)

        X = self.ordinalencoder_.transform(X)

        categories = [np.arange(-1, len(cats)) for cats in self.ordinalencoder_.categories_]
        self.onehotencoder_ = OneHotEncoder(categories = categories).fit(X)
        return self

    def transform(self, X, **kwargs):
        X = self.ordinalencoder_.transform(X)
        return self.onehotencoder_.transform(X)