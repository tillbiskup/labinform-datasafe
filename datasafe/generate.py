import os


class Generate:
    """
    Class for whatever...

    Attributes
    ----------
    path : :class:`str`
        base directory for the datasafe

    """

    def __init__(self):
        self.path = ''

    def find_last_id(self):
        """
        Find last (numeric) ID used in a particular directory of the datasafe

        Return last element of a sorted list of directory contents, assuming the
        directory to only contain subdirectories with numeric IDs.

        In case there is no numeric ID yet in the directory, it returns 0.

        Returns
        -------
        last_id : :class:`int`
            Highest ID in current directory

        """
        directory_contents = os.listdir(self.path)
        # Important: Convert first to integers, then sort
        directory_contents = list(map(int, directory_contents))
        if not directory_contents:
            highest_id = 0
        else:
            highest_id = sorted(directory_contents)[-1]
        return highest_id

    def create_new_directory(self, new_dir=''):
        """
        Create a new directory within the given path.

        Parameters
        ----------
        new_dir : :class:`str`
            Name of new directory to create

        """
        complete_path = os.path.join(self.path, new_dir)
        os.mkdir(path=complete_path)
        return

    def create_directory_for_new_dataset(self):
        """
        Create directory in datasafe for new dataset.

        Returns
        -------
        new_id : :class:`int`
            ID of newly created directory

        """
        highest_id = self.find_last_id()
        new_id = highest_id + 1
        self.create_new_directory(new_dir=str(new_id))
        return new_id


if __name__ == '__main__':
    temporary_datasafe = '../tests/files/tmpsafe'

    irgendwas = Generate()
    irgendwas.path = temporary_datasafe

    last_id = irgendwas.find_last_id()
    print(last_id)

    print(irgendwas.create_directory_for_new_dataset())
