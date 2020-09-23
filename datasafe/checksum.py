"""
Checksums fulfil a twofold function within the dataset component of the
LabInform framework: They allow for easily checking whether the data items
of a dataset entry have been corrupted on transfer or during time, and they
allow for easily detecting duplicates.

To fulfil their duties, a few general design goals have been developed and
implemented:

* Checksums are always generated for file contents, not file names,
  thus rendering the file names (that may easily change) irrelevant for the
  actual checksum.

* Checksums over a list of files are generated per file (using its content),
  the generated checksums sorted and a checksum generated for the sorted
  list of checksums. Thus, filenames cannot interfere with the final
  checksum, as they are irrelevant for the sorting of the checksums the
  final checksum is generated for.

* For datasets, two checksums are generated, one spanning both, data and
  metadata, the other spanning only the data. The reason behind: Metadata
  are of human origin and therefore inherently prone to errors and subject
  to (in)frequent updates and corrections. Data, however, shall never
  change after they have been recorded.

A note on the algorithms used: The module allows to use all algorithms for
creating checksums that are currently supported by the :mod:`hashlib` module.
However, although MD5 usually is considered unsafe, for the purposes
checksums are used in the current context (*non-cryptographic*),
it is clearly sufficient. This is why still, the default algorithm used by
the :class:`Checksum` class is MD5.
"""

import importlib


class Generator:
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

    def _get_hash_function(self):
        return getattr(importlib.import_module('hashlib'), self.algorithm)()

    def hash_string(self, string=''):
        """
        Create checksum for string

        Parameters
        ----------
        string : :class:`str`
            String to compute hash for


        Returns
        -------
        checksum : :class:`str`
            Computed checksum

        """
        hash_function = self._get_hash_function()
        hash_function.update(string.encode())
        return hash_function.hexdigest()

    def hash_strings(self, list_of_strings=None):
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
        hash_function = self._get_hash_function()
        for element in sorted(list_of_strings):
            hash_function.update(element.encode())
        return hash_function.hexdigest()

    def generate(self, filenames=None):
        """
        Generate checksum for (list of) file(s).

        For a single file, the checksum will be generated of its content.

        For a list of files, for each file, the checksum of its contents will be
        generated and afterwards the checksum over the checksums.

        The checksums of the individual files will be sorted before generating
        the final checksum. Hence, sorting is independent of the filenames
        and only depends on the actual file contents, resulting in stable
        hashes.

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
            return self._hash_file_content(filenames)

        file_checksum = []
        for filename in filenames:
            file_checksum.append(
                self._hash_file_content(filename))

        return self.hash_strings(file_checksum)

    def _hash_file_content(self, filename):
        """
        Create checksum for file contents

        Reads file in binary format and blockwise (4K) for not crashing
        with large files.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to compute the hash for


        Returns
        -------
        checksum : :class:`str`
            Computed checksum

        """
        hash_function = self._get_hash_function()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_function.update(chunk)
        return hash_function.hexdigest()
