"""
Each item (currently: dataset) stored in the datasafe is accompanied by a
file containing a lot of (autmatically obtained) useful information about
the item stored. Typically, the YAML format is used for the manifest file,
and the file named ``MANIFEST.yaml`` generically.

The idea behind manifests is to have easy access to information that could
be retrieved from the item stored, but not without having special
functionality such as data and metadata importers available. Thus,
the datasafe component is much more independent of other packages and modules.

In case of a dataset, the information contained ranges from general
information on the dataset (LOI, whether it is complete) to the format of
data and metadata to the actual file names and the checksums over data and
data and metadata.
"""


import collections
import os

import oyaml as yaml

import datasafe.checksum


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingInformationError(Error):
    """Exception raised when necessary information is not provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFileError(Error):
    """Exception raised when required file does not exist

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Generator:
    """
    Collect information and write ``MANIFEST.yaml`` document

    ``MANIFEST.yaml`` contains relevant information about the data storage of a
    single measurement. Beside the type and format of the ``MANIFEST.yaml``
    itself, it contains the LOI of the dataset, the names, format and
    versions of data and metadata files and the respective checksums.

    The information for the actual ``MANIFEST.yaml`` document first gets
    collected in an ordered dict of the designated structure. The dict
    populated this way is then written to a yaml file.

    Attributes
    ----------
    manifest : :class:`collections.OrderedDict`

    filename : :class:`str`
        Output filename, defaults to ``MANIFEST.yaml``

    filenames : :class:`dict`
        Lists of data and metadata files.
   """
    def __init__(self):
        manifest_format = collections.OrderedDict([
            ("type", "datasafe dataset manifest"),
            ("version", "0.1.0.dev4"),
        ])
        manifest_dataset = collections.OrderedDict([
            ("loi", ""),
            ("complete", False),
        ])
        manifest_files = collections.OrderedDict([
            ("metadata", []),
            ("data", collections.OrderedDict([('format', ''), ('names', [])])),
            ("checksums", []),
        ])
        manifest_keys_level_one = [
            ('format', manifest_format),
            ('dataset', manifest_dataset),
            ('files', manifest_files),
        ]
        self.manifest = collections.OrderedDict(manifest_keys_level_one)
        self.filename = 'MANIFEST.yaml'
        self.filenames = {'data': [], 'metadata': []}

    def populate(self):
        """
        Populate given manifest structure with information.

        Fills manifest dict containing information about data and metadata.
        """
        if not self.filenames['data']:
            raise MissingInformationError(message='Data filenames missing')
        if not self.filenames['metadata']:
            raise MissingInformationError(message='Metadata filenames missing')
        for filename in self.filenames['data']:
            if not os.path.exists(filename):
                raise MissingFileError(message='data file(s) not existent')
        for filename in self.filenames['metadata']:
            if not os.path.exists(filename):
                raise MissingFileError(message='metadata file(s) not existent')
        for filename in self.filenames['data']:
            # noinspection PyTypeChecker
            self.manifest['files']['data']['names'].append(filename)
        self.manifest['files']['data']['format'] = self._get_data_format(
            self.filenames['data'])
        for filename in self.filenames['metadata']:
            metadata_info = self._get_metadata_info(filename)
            self.manifest['files']['metadata'].append(metadata_info)
        self.manifest['files']['checksums'].append(collections.OrderedDict([
            ('name', 'CHECKSUM'),
            ('format', 'MD5 checksum'),
            ('span', 'data, metadata'),
            ('value', self._generate_checksum(self.filenames['data'] +
                                              self.filenames['metadata'])),
        ]))
        self.manifest['files']['checksums'].append(collections.OrderedDict([
            ('name', 'CHECKSUM_data'),
            ('format', 'MD5 checksum'),
            ('span', 'data'),
            ('value', self._generate_checksum(self.filenames['data'])),
        ]))

    def write(self):
        """
        Output manifest dict to yaml file.
        """
        with open(self.filename, mode='w+') as output_file:
            yaml.dump(self.manifest, output_file)

    @staticmethod
    def _get_metadata_info(filename=''):
        """
        Retrieve general information about metadata file

        .. todo::
            Needs to be converted into a factory method calling the relevant
            metadata importers and retrieve the actual information about
            format and version from the metadata file itself.

        """
        metadata_info = collections.OrderedDict([
            ('name', filename),
            ('format', 'info file'),
            ('version', '0.1.0')
        ])
        return metadata_info

    @staticmethod
    def _get_data_format(filenames=None):
        """
        Retrieve format of data files

        .. todo::
            Needs to be converted into a factory method.

        """
        data_format = 'test'
        return data_format

    @staticmethod
    def _generate_checksum(filenames=None):
        """
        Generate checksum over file(s) using the checksum module.

        Parameters
        ----------
        filenames : :class:`list`
            List containing filenames of which a checksum will be created.

        Returns
        -------
        result : :class:`str`
            Returns checksum (over checksums) of files.
        """
        checksum_generator = datasafe.checksum.Checksum()
        return checksum_generator.checksum(filenames=filenames)
