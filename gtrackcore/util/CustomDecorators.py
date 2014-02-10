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


def print_args(func, pretty_print=False):

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
