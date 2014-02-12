import time
import functools


def timeit(func=None, print_args=False):

    if func is None:
        return functools.partial(timeit, print_args=print_args)

    @functools.wraps(func)
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


def print_args(func=None, pretty_print=False):

    if func is None:
        return functools.partial(print_args, pretty_print=pretty_print)

    @functools.wraps(func)
    def wrapper(*args, **kw_args):
        if pretty_print:
            print func.__name__
            for arg in args:
                print arg
            for kw, arg in kw_args.iteritems():
                print kw, ':', args
        else:
            print '%r (%r, %r)' % (func.__name__, args, kw_args)

        return func(*args, **kw_args)

    return wrapper
