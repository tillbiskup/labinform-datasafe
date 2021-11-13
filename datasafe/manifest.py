"""
Manifests for datasafe items.

.. sidebar:: Manifest

    *Shipping:* Document listing the cargo (...) of a ship, aircraft or
    vehicle for the use of customs or other officials.

    *Computing:* File containing metadata for a group of accompanying files
    forming part of a coherent unit.


Each item (currently: dataset) stored in the datasafe is accompanied by a
file containing a lot of (automatically obtained) useful information about
the item stored. Typically, the YAML format is used for the manifest file,
and the file named ``MANIFEST.yaml`` generically.

Manifests provide eays access to information on the items of a dataset such as
data format, associated files and their meanings, and checksums allowing to
detect data corruption. Particularly information regarding the file format
could be retrieved from the item(s) stored, but only by using specialised
data and metadata imporers. Thus, manifests allow the the datasafe component
to be much more independent of other packages and modules.


.. note::

    While manifest files are a general concept, currently they are only
    implemented for datasets stored in the datasafe. This will, however,
    most probably change in the future with the further development of the
    datasafe.


Manifests for datasets
======================

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
        format: cwEPR Info file
        version: 0.1.4
      data:
        format: test
        names:
        - test
    checksums:
    - name: CHECKSUM
      format: MD5 checksum
      span: data, metadata
      value: f46475b4905fe2e1a388dc5c6a07ecbc
    - name: CHECKSUM_data
      format: MD5 checksum
      span: data
      value: 74be16979710d4c4e7c6647856088456


A few comments on this example:

* The file identifies its own format, using the ``format`` key on the
  highest level, including type and version. This allows for automatically
  handling different formats and different versions of the same format.

* YAML is a human-readable and (even more important) human-*writable*
  standard supported by many programming languages. Hence, information
  stored in this way can be easily processed both, by other programs as well
  as in the (far) future. Text files are probably the only format with real
  longtime support.

* Checksums are used to allow for integrity checks, *i.e.* inadvertent
  change of data or metadata. At the same time, as they are generated using
  the *content*, but *not the names* of the files, they can be used to check
  for duplicates.

* Using MD5 as a hashing algorithm may raise some criticism. Clearly, MD5 shall
  not be used any more for security purposes, as it needs to be considered
  broken (since years already, as of 2021). However, to only check for
  inadvertend changes (or duplicates) of data, it is still a good choice,
  due to being fast and still widely supported.


Working with manifests
======================

To work with manifests in a program, the YAML file needs to be represented
in form of an object, and this object should be able to get its contents
from as well as writing its contents to a YAML file. Furthermore, wouldn't
it be helpful if a manifest object could check for the integrity of the
accompanying files, (re)creating checksums and comparing them to those
stored in the manifest?

This is what the :class:`Manifest` class provides you with. Suppose you have
a dataset and an accompanying manifest. Checking the integrity of the
dataset could be as simple as:

.. code-block::

    manifest = Manifest()
    manifest.from_file()
    integrity = manifest.check_integrity()

    if not all(integrity.values()):
        fails = [key for key, value in integrity.items() if not value]
        for fail in fails:
            print(f"The following checksum failed: '{fail}'")


Of course, in your code, you will most probably do more sensible things than
only printing which checksum check failed.

Conversely, if you would want to create a manifest file, in the simplest
case all you would need to do is to specify which filenames are data and
metadata files, respectively:

.. code-block::

    manifest = Manifest()
    manifest.data_filenames = [<your data filenames>]
    manifest.metadata_filenames = [<your metadata filenames>]
    manifest.to_file()


This would create a file ``MANIFEST.yaml`` including the auto-generated
checksums and the information regarding the metadata file format (as long as
it is either the info file format or YAML).


File format detection
=====================

A big question remains: How to (automatically) detect the file format of a
given dataset? Probably there is no general solution to this problem that
would work in all possible cases. Furthermore, it is implausible for this
package to contain format detectors for all file formats one could think of.
Therefore, the following strategy will be used:

* File format detection is delegated to helper functions that are provided
  with the list of filenames a dataset consists of.

* Using the Python plugin architecture (entry points), users can provide
  their own helper functions to detect file formats.


.. important::

    The ideas described above are (as of 11/2021) still only ideas that
    remain to be implemented. Furthermore, most probably the package will
    provide file format detectors for at least (some) EPR data formats.


Module documentation
====================

"""

import os

import oyaml as yaml

import datasafe.checksum
from datasafe.exceptions import MissingInformationError, NoFileError


class Manifest:
    """
    Representation of the information contained in a manifest file

    A file named ``MANIFEST.yaml`` contains relevant information about the
    data storage of a single measurement. Besides the type and format of the
    ``MANIFEST.yaml`` itself, it contains the LOI of the dataset, the names,
    format and versions of data and metadata files and the respective
    checksums.

    Attributes
    ----------
    loi : :class:`str`
        lab object identifier (LOI) corresponding to dataset

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
        self.loi = ''
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
        self.metadata_filenames = []
        for metadata_file in manifest_dict['files']['metadata']:
            self.metadata_filenames.append(metadata_file['name'])
        for checksum in manifest_dict['checksums']:
            if 'metadata' in checksum['span']:
                self.checksum = checksum['value']
            else:
                self.data_checksum = checksum['value']
        self.loi = manifest_dict['dataset']['loi']

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
        datasafe.exceptions.MissingInformationError
            Raised if no filename to read from is provided
        datasafe.exceptions.NoFileError
            Raised if file to read from does not exist on the file system

        """
        if not filename:
            raise MissingInformationError(message="No filename provided")
        if not os.path.exists(filename):
            raise NoFileError("File does not exist")
        with open(filename, 'r', encoding='utf8') as file:
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
        NoFileError
            Raised if any of the files listed in either
            :attr:`data_filenames` or :attr:`metadata_filenames` does not
            exist on the file system

        """
        if not self.data_filenames:
            raise MissingInformationError(message='Data filenames missing')
        for filename in self.data_filenames:
            if not os.path.exists(filename):
                raise NoFileError(f'Data file {filename} does not exist.')
        for filename in self.metadata_filenames:
            if not os.path.exists(filename):
                raise NoFileError(f'Metadata file {filename} does not '
                                  'exist')
        manifest_ = self._create_manifest_dict()
        for filename in self.data_filenames:
            # noinspection PyTypeChecker
            manifest_['files']['data']['names'].append(filename)
        manifest_['files']['data']['format'] = self._get_data_format()
        manifest_['files']['metadata'] = self._get_metadata_info()
        manifest_['checksums'].append({
            'name': 'CHECKSUM',
            'format': 'MD5 checksum',
            'span': 'data, metadata',
            'value': self._generate_checksum(self.data_filenames +
                                             self.metadata_filenames),
        })
        manifest_['checksums'].append({
            'name': 'CHECKSUM_data',
            'format': 'MD5 checksum',
            'span': 'data',
            'value': self._generate_checksum(self.data_filenames),
        })
        manifest_['dataset']['loi'] = self.loi
        return manifest_

    def to_file(self):
        """
        Safe manifest to file

        The information for the actual manifest file first gets collected in
        an ordered dict of the designated structure using :func:`to_dict`.
        The dict populated this way is then written to a yaml file (usually)
        named ``MANIFEST.yaml`` (as specified by :attr:`manifest_filename`).
        """
        with open(self.manifest_filename, mode='w+', encoding='utf8') as \
                output_file:
            yaml.dump(self.to_dict(), output_file)

    def check_integrity(self):
        """
        Check integrity of dataset, comparing stored with generated checksums.

        To check the integrity of a dataset, the checksums stored within the
        manifest file will be compared to newly generated checksums over
        data and metadata together as well as over data alone.

        Allows to check for consistency of manifest and data, and hence to
        detect any corruption of the data. You may check for integrity like
        this:

        .. code-block::

            integrity = manifest.check_integrity()
            if not all(integrity.values()):
                fails = [key for key, value in integrity.items() if not value]
                for fail in fails:
                    print(f"The following checksum failed: '{fail}'")

        This would first check if there are any failed checks, and if so,
        for each fail print the failing key. Of course, in your case you
        will do more sensible things than just printing the keys.


        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values


        Raises
        ------
        datasafe.exceptions.MissingInformationError
            Raised if not all necessary information is available.

        """
        if not all([self.data_filenames, self.metadata_filenames,
                    self.data_checksum, self.checksum]):
            raise MissingInformationError('Some information missing')
        checksum = self._generate_checksum(self.data_filenames +
                                           self.metadata_filenames)
        data_checksum = self._generate_checksum(self.data_filenames)
        integrity = {
            'data': data_checksum == self.data_checksum,
            'all': checksum == self.checksum,
        }
        return integrity

    @staticmethod
    def _create_manifest_dict():
        """
        Create basic structure of a manifest as (ordered) dict

        Returns
        -------
        manifest_ : :class:`collections.OrderedDict`
            basic structure of a manifest as (ordered) dict

        """
        manifest_format = {
            "type": "datasafe dataset manifest",
            "version": "0.1.0",
        }
        manifest_dataset = {
            "loi": "",
            "complete": False,
        }
        manifest_files = {
            "metadata": [],
            "data": {'format': '', 'names': []},
        }
        manifest_keys_level_one = [
            ('format', manifest_format),
            ('dataset', manifest_dataset),
            ('files', manifest_files),
            ('checksums', []),
        ]
        manifest_ = dict(manifest_keys_level_one)
        return manifest_

    def _get_metadata_info(self):
        """Retrieve general information about metadata file."""
        self.format_detector.metadata_filenames = self.metadata_filenames
        return self.format_detector.metadata_format()

    def _get_data_format(self):
        """Retrieve format of data files."""
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
    datasafe.exceptions.NoFileError
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
            info = {
                'name': filename,
                'format': format_,
                'version': version
            }
            metadata_info.append(info)
        return metadata_info

    @staticmethod
    def _parse_info(filename=''):
        with open(filename, 'r', encoding='utf8') as file:
            info_line = file.readline()
        info_parts = info_line.split(' - ')
        _, version, _ = info_parts[1].split()
        format_ = info_parts[0].strip()
        return format_, version

    @staticmethod
    def _parse_yaml(filename=''):
        with open(filename, 'r', encoding='utf8') as file:
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
        datasafe.exceptions.NoFileError
            Raised if no data file(s) are provided

        """
        if not self.data_filenames:
            raise NoFileError('No data filenames')
        return self._detect_data_format()

    # noinspection PyMethodMayBeStatic
    def _detect_data_format(self):  # noqa
        return 'test'


if __name__ == '__main__':
    # Create Manifest.yaml file for demonstration purposes
    DATA_FILENAME = 'test'
    METADATA_FILENAME = 'test.info'
    with open(DATA_FILENAME, 'w+', encoding='utf8') as f:
        f.write('')
    with open(METADATA_FILENAME, 'w+', encoding='utf8') as f:
        f.write('cwEPR Info file - v. 0.1.4 (2020-01-21)')
    manifest_obj = Manifest()
    manifest_obj.data_filenames = [DATA_FILENAME]
    manifest_obj.metadata_filenames = [METADATA_FILENAME]
    manifest_obj.to_file()
    for filename_ in [DATA_FILENAME, METADATA_FILENAME]:
        os.remove(filename_)
