import os


def find_last_id(path=''):
    """
    Find last (numeric) ID used in a particular directory of the datasafe

    Return last element of a sorted list of directory contents, assuming the
    directory to only contain subdirectories with numeric IDs.

    In case there is no numeric ID yet in the directory, it returns 0.

    Parameters
    ----------
    path : :class:`str`
        directory path to look for latest ID in

    Returns
    -------
    last_id : :class:`int`
        Highest ID in current directory

    """
    directory_contents = os.listdir(path)
    # Important: Convert first to integers, then sort
    directory_contents = list(map(int, directory_contents))
    if not directory_contents:
        highest_id = 0
    else:
        highest_id = sorted(directory_contents)[-1]
    return highest_id


def create_new_directory(path='', new_dir=''):
    """
    Create a new directory within the given path.

    Parameters
    ----------
    path : :class:`str`
        Directory to create the new directory in

    new_dir : :class:`str`
        Name of new directory to create

    """
    complete_path = os.path.join(path, new_dir)
    os.mkdir(path=complete_path)
    return


def create_directory_for_new_dataset(path=''):
    """
    Create directory in datasafe for new dataset.

    Parameters
    ----------
    path : :class:`str`
        Path to create new directory in

    Returns
    -------
    new_id : :class:`int`
        ID of newly created directory

    """
    highest_id = find_last_id(path=temporary_datasafe)
    new_id = highest_id + 1
    create_new_directory(path=temporary_datasafe, new_dir=str(new_id))
    return new_id


temporary_datasafe = 'tmpsafe'

last_id = find_last_id(path=temporary_datasafe)
print(last_id)

print(create_directory_for_new_dataset(path=temporary_datasafe))
