import datetime
import time


def time_of_request_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):

        start = time.time()

        response = get_response(request)

        end = time.time()
        print(f'Execution time: of {request.path} is {end - start} secs')

        return response

    return middleware
