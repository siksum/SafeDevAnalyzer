import sys

try:
    import numpy as np
except ImportError:
    print("ERROR: in order to use slither-simil, you need to install numpy")
    print("$ pip3 install numpy --user\n")
    sys.exit(-1)


def load_cache(infile, nsamples=None):
    cache = {}
    with np.load(infile, allow_pickle=True) as data:
        array = data["arr_0"][0]
        for i, (x, y) in enumerate(array):
            cache[x] = y
            if i == nsamples:
                break
    return cache

# def load_cache(infile, nsamples=None):
#     cache = {}
#     with np.load(infile, allow_pickle=True) as data:
#         array = data[data.files[0]][0]
#         for i, item in enumerate(array):
#             cache[i] = item
#             if i == nsamples:
#                 break

#     return cache


def save_cache(cache, outfile):
    np.savez(outfile, np.array(cache, dtype=object))
