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


def timeit_repeat(func=None, reps=2):

    if func is None:
        return functools.partial(timeit_repeat, reps=reps)

    @functools.wraps(func)
    def wrapper(*args, **kw_args):
        rep_times = []

        for x in xrange(reps):
            start = time.time()
            result = func(*args, **kw_args)
            end = time.time()
            time_used = end - start
            rep_times.append(time_used)

        print '%r avg. time: %d' % (func.__name__, (sum(rep_times) / len(rep_times)))

        return result

    return wrapper