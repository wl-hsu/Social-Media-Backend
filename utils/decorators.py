from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(method='GET', params=None):
    """
    When we use @required_params(params=['some_param'])
    The required_params function should return a decorator function, the parameters of this decorator function
    It is the function view_func wrapped by @required_params
    """

    # writing params=[] in the parameters is not a big problem in many cases
    # But from a good programming practice, the value in the parameter list of a function cannot be a mutable parameter
    if params is None:
        params = []

    def decorator(view_func):
        """
        The decorator function uses wraps to parse the parameters in view_func and pass them to _wrapped_view
        The instance parameter here is actually the self in view_func
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # After checking, call view_func wrapped by @required_params
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator