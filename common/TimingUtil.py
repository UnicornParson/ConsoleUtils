import time
import sys

class CTimingUtil:
    timingLoggerWrapper = None

    @staticmethod
    def timing_impl(f):
        def wrap(*args, **kwargs):
            time1 = time.time()
            sarg = str(args)
            skwarg = str(kwargs)
            ret = f(*args, **kwargs)
            time2 = time.time()
            msg = f"{f.__name__} function took {((time2 - time1) * 1000.0)} ms. args({sarg},k: {skwarg})"
            if CTimingUtil.timingLoggerWrapper:
                CTimingUtil.timingLoggerWrapper.verboseLog(msg)
            else:
                print("no logger")
                sys.exit(-1)
            return ret
        return wrap

