"""
General purpose functions and classes used in other modules.

To avoid circular dependencies, this module does not depend on any other
modules of the datasafe package, but it can be imported into every other
module.

.. todo::
    Probably, this module should eventually be moved to the utils subpackage
    of the LabInform package, as it may contain utils not only useful for
    the datasafe component.
"""


import contextlib
import importlib
import os


def object_from_name(module_name='', class_name=''):
    """
    Create object from module and class name

    Parameters
    ----------
    module_name : :class:`str`
        Name of the module containing the class

    class_name : :class:`str`
        Name of the class an object should be instantiated of

    Returns
    -------
    object : :class:`object`
        Object instantiated from module and class name

    """
    # load the module, will raise ImportError if module cannot be loaded
    module = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    class_ = getattr(module, class_name)
    return class_()


@contextlib.contextmanager
def change_working_dir(path=''):  # pylint: disable=redefined-outer-name
    """
    Context manager for temporarily changing the working directory.

    Sometimes it is necessary to temporarily change the working directory,
    but one would like to ensure that the directory is reverted even in case
    an exception is raised.

    Due to its nature as a context manager, this function can be used with a
    ``with`` statement. See below for an example.


    Parameters
    ----------
    path : :class:`str`
        Path the current working directory should be changed to.


    Examples
    --------
    To temporarily change the working directory:

    .. code-block::

        with change_working_dir(os.path.join('some', 'path')):
            # Do something that may raise an exception

    This can come in quite handy in case of tests.


    .. versionadded:: 0.6

    """
    oldpwd = os.getcwd()
    if path:
        os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)
