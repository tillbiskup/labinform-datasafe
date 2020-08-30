import collections
import os

import oyaml as yaml

import datasafe.create_checksum


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
    def _generate_checksum(filenames=None):
        checksum_generator = datasafe.create_checksum.Checksum()
        return checksum_generator.checksum(filenames=filenames)
