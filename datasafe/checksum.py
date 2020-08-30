import importlib


class Checksum:
    """
    Class for creating checksums

    Attributes
    ----------
    algorithm : :class:`str`
        Hash algorithm to use.

        Defaults to "md5", can be everything available in hashlib module.
    """

    def __init__(self):
        self.algorithm = 'md5'

    @staticmethod
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

    def checksum_of_file_contents(self, filename=''):
        """
        Create checksum for file contents

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to compute the hash for


        Returns
        -------
        checksum : :class:`str`
            Computed checksum

        """
        hash_function = self.object_from_name('hashlib', self.algorithm)
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_function.update(chunk)
        # noinspection PyUnresolvedReferences
        return hash_function.hexdigest()

    def checksum_of_list_of_strings(self, list_of_strings=None):
        """
        Create checksum for list of strings

        The strings will be sorted before generating the checksum. Hence, if you
        want to create a checksum of checksums (e.g., for a checksum of several
        files), sorting is independent of the filenames and only depends on the
        actual file contents, resulting in stable hashes.

        Parameters
        ----------
        list_of_strings : :class:`list`
            List of strings to compute hash for


        Returns
        -------
        checksum : :class:`str`
            Computed checksum

        """
        hash_function = self.object_from_name('hashlib', self.algorithm)
        for element in sorted(list_of_strings):
            hash_function.update(element.encode())
        # noinspection PyUnresolvedReferences
        return hash_function.hexdigest()

    def checksum(self, filenames=None):
        """
        Generate checksum for (list of) file(s).

        For a single file, the checksum will be generated of its content.

        For a list of files, for each file, the checksum of its contents will be
        generated and afterwards the checksum over the checksums.

        Parameters
        ----------
        filenames
            string or list of strings

            filename(s) of files to generate a checksum of their content(s)


        Returns
        -------
        checksum : :class:`str`
            Checksum generated over (list of) file(s)

        """
        if not isinstance(filenames, list):
            return self.checksum_of_file_contents(filenames)

        file_checksum = []
        for filename in filenames:
            file_checksum.append(
                self.checksum_of_file_contents(filename))

        return self.checksum_of_list_of_strings(file_checksum)


if __name__ == '__main__':
    # MD5 (sa620-01.xml) = db432cd074fe817703c87d34676332cd
    # MD5 (sa620-01.info) = 5e8f76e0ca076b8809193fea0fa03dd1

    # MD5 (both files) = c4bf65e5b8de8d7466ce6d9aea08395a

    path_to_files = '../tests/files/'
    irgendwas = Checksum()
    irgendwas.algorithm = 'sha256'

    print('')
    print(irgendwas.checksum(path_to_files + 'sa620-01.xml'))

    print(irgendwas.checksum([path_to_files + 'sa620-01.xml',
                              path_to_files + 'sa620-01.info']))
    print(irgendwas.checksum([path_to_files + 'sa620-01.info',
                              path_to_files + 'sa620-01.xml']))
