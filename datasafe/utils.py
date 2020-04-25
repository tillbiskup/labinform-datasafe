import importlib


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
