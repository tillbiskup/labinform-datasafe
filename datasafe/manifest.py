"""
Manifests for datasafe items.

Each item (currently: dataset) stored in the datasafe is accompanied by a
file containing a lot of (automatically obtained) useful information about
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

As an example, the contents of a manifest file for a dataset are shown below,
for a fictitious dataset consisting of two (empty) files (data in ``test`` and
metadata in ``test.info``):

.. code-block:: yaml

    format:
      type: datasafe dataset manifest
      version: 0.1.0
    dataset:
      loi: ''
      complete: false
    files:
      metadata:
      - name: test.info
        format: info file
        version: 0.1.0
      data:
        format: test
        names:
        - test
      checksums:
      - name: CHECKSUM
        format: MD5 checksum
        span: data, metadata
        value: 020eb29b524d7ba672d9d48bc72db455
      - name: CHECKSUM_data
        format: MD5 checksum
        span: data
        value: 74be16979710d4c4e7c6647856088456


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
        super().__init__(message)
        self.message = message


class Manifest:
    """
    Representation of the information contained in a manifest file

    A file named ``MANIFEST.yaml`` contains relevant information about the
    data storage of a single measurement. Beside the type and format of the
    ``MANIFEST.yaml`` itself, it contains the LOI of the dataset, the names,
    format and versions of data and metadata files and the respective
    checksums.

    Attributes
    ----------
    data_filenames : :class:`list`
        filenames of data files

    metadata_filenames : :class:`list`
        filenames of metadata files

    data_checksum : :class:`str`
        checksum over data only

    checksum : :class:`str`
        checksum over data and metadata

    manifest_filename : :class:`str`
        filename for Manifest file, defaults to ``MANIFEST.yaml``

    format_detector : :class:`datasafe.manifest.FormatDetector`
        Helper class to detect file formats

    """

    def __init__(self):
        self.data_filenames = []
        self.metadata_filenames = []
        self.data_checksum = ''
        self.checksum = ''
        self.manifest_filename = 'MANIFEST.yaml'
        self.format_detector = FormatDetector()

    def from_dict(self, manifest_dict):
        """
        Obtain information from (ordered) dict

        Parameters
        ----------
        manifest_dict : :class:`collections.OrderedDict`
            Dict containing information of a manifest

        """
        self.data_filenames = manifest_dict['files']['data']['names']
        for metadata_file in manifest_dict['files']['metadata']:
            self.metadata_filenames.append(metadata_file['name'])
        for checksum in manifest_dict['files']['checksums']:
            if 'metadata' in checksum['span']:
                self.checksum = checksum['value']
            else:
                self.data_checksum = checksum['value']

    def from_file(self, filename='MANIFEST.yaml'):
        """
        Obtain information from Manifest file

        Usually, manifests are stored as YAML file on the file system in
        files named ``MANIFEST.yaml``.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to read manifest from

            Default: "MANIFEST.yaml"

        Raises
        ------
        MissingInformationError
            Raised if no filename to read from is provided
        FileNotFoundError
            Raised if file to read from does not exist on the file system

        """
        if not filename:
            raise MissingInformationError(message="No filename provided")
        if not os.path.exists(filename):
            raise FileNotFoundError("File does not exist")
        with open(filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        self.from_dict(manifest_dict)

    def to_dict(self):
        """
        Return information contained in object as (ordered) dict

        Returns
        -------
        manifest_ : :class:`collections.OrderedDict`
            Manifest as (ordered) dict

        Raises
        ------
        MissingInformationError
            Raised if :attr:`data_filenames` is empty
        FileNotFoundError
            Raised if any of the files listed in either
            :attr:`data_filenames` or :attr:`metadata_filenames` does not
            exist on the file system
        """
        if not self.data_filenames:
            raise MissingInformationError(message='Data filenames missing')
        for filename in self.data_filenames:
            if not os.path.exists(filename):
                raise FileNotFoundError('Data file %s does not exist.' %
                                        filename)
        for filename in self.metadata_filenames:
            if not os.path.exists(filename):
                raise FileNotFoundError('Metadata file %s does not exist' %
                                        filename)
        manifest_ = self._create_manifest_dict()
        for filename in self.data_filenames:
            # noinspection PyTypeChecker
            manifest_['files']['data']['names'].append(filename)
        manifest_['files']['data']['format'] = self._get_data_format()
        manifest_['files']['metadata'] = self._get_metadata_info()
        manifest_['files']['checksums'].append(collections.OrderedDict([
            ('name', 'CHECKSUM'),
            ('format', 'MD5 checksum'),
            ('span', 'data, metadata'),
            ('value', self._generate_checksum(self.data_filenames +
                                              self.metadata_filenames)),
        ]))
        manifest_['files']['checksums'].append(collections.OrderedDict([
            ('name', 'CHECKSUM_data'),
            ('format', 'MD5 checksum'),
            ('span', 'data'),
            ('value', self._generate_checksum(self.data_filenames)),
        ]))
        return manifest_

    def to_file(self):
        """
        Safe manifest to file

        The information for the actual manifest file first gets collected in
        an ordered dict of the designated structure using :func:`to_dict`.
        The dict populated this way is then written to a yaml file (usually)
        named ``MANIFEST.yaml`` (as specified by :attr:`manifest_filename`).
        """
        with open(self.manifest_filename, mode='w+') as output_file:
            yaml.dump(self.to_dict(), output_file)

    @staticmethod
    def _create_manifest_dict():
        """
        Create basic structure of a manifest as (ordered) dict

        Returns
        -------
        manifest_ : :class:`collections.OrderedDict`
            basic structure of a manifest as (ordered) dict

        """
        manifest_format = collections.OrderedDict([
            ("type", "datasafe dataset manifest"),
            ("version", "0.1.0"),
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
        manifest_ = collections.OrderedDict(manifest_keys_level_one)
        return manifest_

    def _get_metadata_info(self):
        """ Retrieve general information about metadata file """
        self.format_detector.metadata_filenames = self.metadata_filenames
        return self.format_detector.metadata_format()

    def _get_data_format(self):
        """ Retrieve format of data files """
        self.format_detector.data_filenames = self.data_filenames
        return self.format_detector.data_format()

    @staticmethod
    def _generate_checksum(filenames=None):
        """
        Generate checksum over file(s) using the checksum module.

        Parameters
        ----------
        filenames : :class:`list`
            List containing data_filenames of which a checksum will be created.

        Returns
        -------
        result : :class:`str`
            Returns checksum (over checksums) of files.
        """
        checksum_generator = datasafe.checksum.Generator()
        return checksum_generator.generate(filenames=filenames)


class FormatDetector:
    """
    Helper class to detect file formats.

    For real use, you need to implement a class subclassing this class
    providing real information, as this class only provides dummy test output.

    As each format has its own peculiarities, you need to come up with
    sensible ways to actually detect both, metadata and data formats.
    Generally, it should be sufficient to provide an implementation for the
    private method :meth:`_detect_data_format` that returns the actual data
    format as string.

    However, at least info files and YAML files (with a certain structure)
    as metadata files are supported out of the box. To add detectors for
    further metadata formats, add methods with the naming scheme
    ``_parse_<extension>`` with "<extension>" being the file extension of
    your metadata file.

    For YAML files, requirements are that there exists a key "format" at the
    top level of the file that contains the keys "type" and "version".

    Attributes
    ----------
    data_filenames : :class:`list`
        filenames of data files

    metadata_filenames : :class:`list`
        filenames of metadata files


    Raises
    ------
    FileNotFoundError
        Raised if no data file(s) are provided

    """

    def __init__(self):
        self.data_filenames = []
        self.metadata_filenames = []

    def metadata_format(self):
        """
        Obtain format of the metadata file(s).

        Generally, the metadata format is checked using the file extension.

        Two formats are automatically detected: info (.info) and YAML (
        .yaml). To support other formats, you need to provide methods with
        the naming scheme ``_parse_<extension>`` with "<extension>" being
        the file extension of your metadata file.

        Returns
        -------
        metadata_info : class:`list`
            List of ordered dicts (:class:`collections.OrderedDict`) each
            containing "name", "format", and "version" as fields.

            If no metadata filenames are provided in
            :attr:`metadata_filenames`, an empty list is returned.

        """
        metadata_info = []
        for filename in self.metadata_filenames:
            extension = os.path.splitext(filename)[1]
            try:
                parse_method = getattr(self, '_parse_' + extension[1:])
                format_, version = parse_method(filename=filename)
            except AttributeError:
                format_ = 'test'
                version = '0.1.0'
            info = collections.OrderedDict([
                ('name', filename),
                ('format', format_),
                ('version', version)
            ])
            metadata_info.append(info)
        return metadata_info

    @staticmethod
    def _parse_info(filename=''):
        with open(filename, 'r') as file:
            info_line = file.readline()
        info_parts = info_line.split(' - ')
        _, version, _ = info_parts[1].split()
        format_ = info_parts[0].strip()
        return format_, version

    @staticmethod
    def _parse_yaml(filename=''):
        with open(filename, 'r') as file:
            info = yaml.safe_load(file)
        format_ = info['format']['type']
        version = info['format']['version']
        return format_, version

    def data_format(self):
        """
        Obtain format of the data file(s).

        You need to subclasses this class and override the non-public method
        :meth:`_detect_data_format` to actually detect the file format, as this
        method only provides "test" as format.

        Returns
        -------
        data_format : :class:`str`
            Name of the format of the data files


        Raises
        ------
        FileNotFoundError
            Raised if no data file(s) are provided

        """
        if not self.data_filenames:
            raise FileNotFoundError('No data filenames')
        return self._detect_data_format()

    # noinspection PyMethodMayBeStatic
    def _detect_data_format(self):
        return 'test'


if __name__ == '__main__':
    # Create Manifest.yaml file for demonstration purposes
    data_filename = 'test'
    metadata_filename = 'test.info'
    for filename_ in [data_filename, metadata_filename]:
        with open(filename_, 'w+') as f:
            f.write('')
    manifest_obj = Manifest()
    manifest_obj.data_filenames = [data_filename]
    manifest_obj.metadata_filenames = [metadata_filename]
    manifest_obj.to_file()
    for filename_ in [data_filename, metadata_filename]:
        os.remove(filename_)
