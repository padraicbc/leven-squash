import hashlib
import timeit
import time

from nose import with_setup


def sha1_new():
    hashlib.new("sha1").hexdigest()

def sha1_con():
    hashli
    b.sha1.hexdigest()

def benchmark_digest_constructors():
    print('benchmarking hashlib.new vs. hashlib.constructors')

    t_new = timeit.Timer("sha1_new('asdf' * 100)")
    t_new.timeit()