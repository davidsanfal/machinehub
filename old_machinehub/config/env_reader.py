"""
    Get variables from environment.
    Automatically handle types inferring datatype from default value.
"""
import os


default_type = {str: lambda x: x,
                type(None): lambda x: x,
                int: lambda x: int(x),
                float: lambda x: float(x),
                list: lambda x: x.split(","),
                bool: lambda x: x == '1'}


def get_env(env_key, default=None, environment=os.environ):

    '''Get the env variable associated with env_key'''
    env_var = environment.get(env_key, default)
    if env_var != default:
        func = default_type[type(default)]
        env_var = func(env_var)
    return env_var
