import time                                                


def timeit(func, print_args=False):

    def wrapper(*args, **kw_args):
        start = time.time()
        result = func(*args, **kw_args)
        end = time.time()

        if print_args:
            print '%r (%r, %r) %2.5f sec' % (func.__name__, args, kw_args, end - start)
        else:
            print '%r %2.5f sec' % (func.__name__, end - start)
        return result

    return wrapper
