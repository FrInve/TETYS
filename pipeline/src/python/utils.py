import datetime as dt


def df_info(f):
    def wrapper(df, *args, **kwargs):
        tic = dt.datetime.now()
        result = f(df, *args, **kwargs)
        toc = dt.datetime.now()
        print("\n\n{} took {} time\n".format(f.__name__, toc - tic))
        print("After applying {}\n".format(f.__name__))
        print("Shape of df = {}\n".format(result.shape))
        print("Columns of df are {}\n".format(result.columns))
        print("Index of df is {}\n".format(result.index))
        for i in range(100): print("-", end='')
        return result
    return wrapper
