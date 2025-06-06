import time

def cache_bust(request):
    """
    Add the current timestamp to templates to help with cache busting.
    """
    return {
        'timestamp': int(time.time())
    }
