"""
Server components of the LabInform datasafe.

Different server components can be distinguished:

* user-facing components (frontends)
* storage components (backends)

Note that "user" is a broad term here, meaning any person and program
accessing the datasafe. In this respect, the clients contained in
:mod:`datasafe.client` are users as well.

The backend components deal with the actual storage of data (in the file
system) and the access to them.


Frontends
=========

Frontends allow a "user" (mostly another program) to access the datasafe,
without needing any details of how the data are actually stored.

Currently, there are two frontends implemented, that have different use cases:

* :class:`Server`

  General frontend that can be used locally with
  :class:`datasafe.client.LocalClient`.

* :class:`HTTPServerAPI`

  API for the HTTP server running via flask.

  HTTP frontend that can be used via HTTP, *e.g.* using the
  :class:`datasafe.client.HTTPClient` class. Using HTTP, this allows
  generally to completely separate client and server in terms of their
  locations and access data even remotely. However, keep in mind that remote
  access comes with security implications that are currently not dealt with.

  The actual HTTP server is created with the function
  :func:`create_http_server`, but the API class is the interesting part here.


Backends
========

Backends deal with actually storing the data.

Currently, there is only one backend implemented:

* :class:`StorageBackend`

  A backend using the file system for storing data.


Things to decide
================

Some things that need to be decided about:

* Where to store configuration?

  At least the base directory for the datasafe needs to be defined in some way.

  Other configuration values could be the issuer (number after the "42." of
  a LOI)

Perhaps one could store the configuration in a separate configuration class
to start with and see how this goes...


Module documentation
====================

"""

import os
import shutil
import tempfile

from flask import Flask, request
from flask.views import MethodView

from datasafe import configuration
import datasafe.loi as loi_
from datasafe.exceptions import (
    MissingPathError,
    MissingContentError,
    MissingLoiError,
    InvalidLoiError,
    ExistingFileError,
    LoiNotFoundError,
    NoFileError,
)
from datasafe.manifest import Manifest
from datasafe.utils import change_working_dir


class Server:
    """
    Server part of the datasafe.

    The server interacts with the storage backend to store and retrieve
    contents and provides the user interface.

    It retrieves datasets, stores them and should check,
    whether its content is complete and not compromised.

    The transfer occurs as bytes of the zipped dataset that is received by
    the server, decoded, unzipped, and archived into the correct directory.

    Attributes
    ----------
    storage : :class:`StorageBackend`

    loi : :class:`datasafe.loi.Parser`

    """

    def __init__(self):
        self.storage = StorageBackend()
        self.loi = loi_.Parser()
        self._loi_checker = loi_.LoiChecker()

    def new(self, loi=""):
        """
        Create new LOI.

        The storage corresponding to the LOI will be created and the LOI
        returned if successful. This does, however, *not* add any data to
        the datasafe. Therefore, calling :meth:`new` will usually be
        followed by calling :meth:`upload` at some later point. On the other
        hand, before calling :meth:`upload`, you *need to* call :meth:`new`
        to create the new LOI storage space.

        Parameters
        ----------
        loi : :class:`str`
            LOI for which the resource should be created

        Returns
        -------
        loi : :class:`str`
            LOI the resource has been created for

        Raises
        ------
        datasafe.exceptions.MissingLoiError
            Raised if no LOI is provided

        datasafe.exceptions.InvalidLoiError
            Raised if LOI is not valid (for the given operation)

        """
        if not loi:
            raise MissingLoiError("No LOI provided.")
        self._check_loi(loi=loi, validate=False)
        id_parts = self.loi.split_id()
        if id_parts[0] != "exp":
            raise InvalidLoiError("Loi ist not a valid experiment LOI.")
        self._loi_checker.ignore_check = "LoiMeasurementNumberChecker"
        if not self._loi_checker.check(loi):
            raise InvalidLoiError("String is not a valid LOI.")
        date_checker = loi_.IsDateChecker()
        if date_checker.check(id_parts[1]):
            path = self.loi.separator.join(id_parts[0:3])
        else:
            path = self.loi.separator.join(id_parts[0:4])
        if not self.storage.exists(path):
            self.storage.create(path)
        new_path = self.storage.create_next_id(path)
        new_loi = self.loi.separator.join(
            [
                self.loi.root_issuer_separator.join(
                    [self.loi.root, self.loi.issuer]
                ),
                self.loi.type,
                *new_path.split(os.sep),
            ]
        )
        return new_loi

    def upload(self, loi="", content=None):
        """
        Upload data to the datasafe.

        Data are upload as bytes of the zipped content (dataset).

        Parameters
        ----------
        loi : :class:`str`
            LOI the storage should be created for

        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents to
            be stored via the backend


        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

            For details see :meth:`datasafe.manifest.Manifest.check_integrity`.


        Raises
        ------
        datasafe.exceptions.MissingLoiError
            Raised if no LOI is provided

        datasafe.exceptions.LoiNotFoundError
            Raised if resource corresponding to LOI does not exist

        datasafe.exceptions.ExistingFileError
            Raised if resource corresponding to LOI is not empty

        """
        if not loi:
            raise MissingLoiError("No LOI provided.")
        self._check_loi(loi=loi)
        if not self.storage.exists(self.loi.id):
            raise LoiNotFoundError("LOI does not exist.")
        if not self.storage.isempty(path=self.loi.id):
            raise ExistingFileError("Directory not empty.")
        return self.storage.deposit(path=self.loi.id, content=content)

    def download(self, loi=""):
        """
        Download data from the datasafe.

        Parameters
        ----------
        loi : :class:`str`
            LOI the data should be downloaded for

        Returns
        -------
        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents of
            the directory corresponding to path

        Raises
        ------
        datasafe.exceptions.MissingLoiError
            Raised if no LOI is provided

        datasafe.exceptions.LoiNotFoundError
            Raised if resource corresponding to LOI cannot be found

        datasafe.exceptions.MissingContentError
            Raised if resource corresponding to LOI has no content

        """
        if not loi:
            raise MissingLoiError("No LOI provided.")
        self._check_loi(loi=loi)
        if not self.storage.exists(self.loi.id):
            raise LoiNotFoundError("LOI does not exist.")
        if self.storage.isempty(self.loi.id):
            raise MissingContentError("LOI does not have content.")
        return self.storage.retrieve(path=self.loi.id)

    def update(self, loi="", content=None):
        """
        Update data in the datasafe.

        Data are upload as bytes of the zipped content (dataset).

        Parameters
        ----------
        loi : :class:`str`
            LOI the resource should be updated for

        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents to
            be updated via the backend


        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

            For details see :meth:`datasafe.manifest.Manifest.check_integrity`.


        Raises
        ------
        datasafe.exceptions.MissingLoiError
            Raised if no LOI is provided

        datasafe.exceptions.LoiNotFoundError
            Raised if resource corresponding to LOI does not exist

        datasafe.exceptions.NoFileError
            Raised if resource corresponding to LOI is empty

        """
        if not loi:
            raise MissingLoiError("No LOI provided.")
        self._check_loi(loi=loi)
        if not self.storage.exists(self.loi.id):
            raise LoiNotFoundError("LOI does not exist.")
        if self.storage.isempty(path=self.loi.id):
            raise NoFileError("Directory empty")
        self.storage.remove(path=self.loi.id, force=True)
        return self.storage.deposit(path=self.loi.id, content=content)

    def _check_loi(self, loi="", validate=True):
        self.loi.parse(loi)
        if self.loi.type != "ds":
            raise InvalidLoiError("LOI is not a datasafe LOI.")
        if validate:
            if not self._loi_checker.check(loi):
                raise InvalidLoiError("String is not a valid LOI.")


class StorageBackend:
    """
    File system backend for the datasafe, actually handling directories.

    The storage backend does not care at all about LOIs, but only operates
    on paths within the file system. As far as datasets are concerned,
    the backend requires a manifest file to accompany each dataset. However,
    it does *not* create such file. Furthermore, data are deposited (using
    :meth:`deposit`) and retrieved (using :meth:`retrieve`) as streams
    containing the contents of ZIP archives.

    Attributes
    ----------
    root_directory : :class:`str`
        base directory for the datasafe

    manifest_filename : :class:`str`
        name of manifest file

    """

    def __init__(self):
        self.config = configuration.StorageBackend()
        self.manifest_filename = (
            self.config.manifest_filename or Manifest().manifest_filename
        )
        self.root_directory = self.config.root_directory or ""

    def working_path(self, path=""):
        """
        Full path to working directory in datasafe

        Returns
        -------
        working_path : :class:`str`
            full path to work on

        """
        return os.path.join(self.root_directory, path)

    def create(self, path=""):
        """
        Create directory for given path.

        Parameters
        ----------
        path : :class:`str`
            path to create directory for

        Raises
        ------
        datasafe.exceptions.MissingPathError
            Raised if no path is provided

        """
        if not path:
            raise MissingPathError
        os.makedirs(self.working_path(path))

    def exists(self, path=""):
        """
        Check whether given path exists

        Parameters
        ----------
        path : :class:`str`
            path to check

        """
        return os.path.exists(self.working_path(path))

    def isempty(self, path=""):
        """
        Check whether directory corresponding to path is empty

        Parameters
        ----------
        path : :class:`str`
            path to check

        Returns
        -------
        result : :class:`bool`
            Returns true if directory corresponding to ``path`` is empty.

        Raises
        ------
        datasafe.exceptions.NoFileError
            Raised if no path is provided

        """
        if not os.path.exists(self.working_path(path)):
            raise NoFileError
        return not os.listdir(self.working_path(path))

    def remove(self, path="", force=False):
        """
        Remove directory corresponding to path.

        Usually, non-empty directories will not be removed but raise an
        :class:`OSError` exception.

        Parameters
        ----------
        path : :class:`str`
            path that should be removed

        force : :class:`bool`
            set to `True` when non-empty directory should be removed

            default: `False`

        Raises
        ------
        OSError
            Raised if a non-empty directory should be removed and
            ``force`` is set to ``False``

        """
        if force:
            shutil.rmtree(self.working_path(path))
        else:
            os.rmdir(self.working_path(path))

    def get_highest_id(self, path=""):
        """
        Get number of subdirectory corresponding to path with highest number

        Return last element of a sorted list of directory contents, assuming the
        directory to only contain subdirectories with numeric IDs.

        In case there is no numeric ID yet in the directory, it returns 0.

        .. todo::
            Handle directories whose names are not convertible to integers


        Parameters
        ----------
        path : :class:`str`
            path to get subdirectory with highest number for

        Returns
        -------
        id : :class:`int`
            subdirectory with the highest number in the directory
            corresponding to ``path``

        """
        directory_contents = os.listdir(self.working_path(path))
        # Important: Convert first to integers, then sort
        directory_contents = list(map(int, directory_contents))
        if not directory_contents:
            highest_id = 0
        else:
            highest_id = sorted(directory_contents)[-1]
        return highest_id

    def create_next_id(self, path=""):
        """
        Create next subdirectory in directory corresponding to path

        Parameters
        ----------
        path : :class:`str`
            path the subdirectory should be created in

        """
        new_path = os.path.join(path, str(self.get_highest_id(path) + 1))
        self.create(new_path)
        return new_path

    def deposit(self, path="", content=None):
        """
        Deposit data provided as content in directory corresponding to path.

        Content is the byte representation of a ZIP archive containing the
        actual content. This byte representation is saved in a temporary
        file and afterwards unpacked in the directory corresponding to path.

        After depositing the content (including unzipping), the checksums in
        the manifest are checked for consistency with newly generated
        checksums, and in case of inconsistencies, an exception is raised.

        Parameters
        ----------
        path : :class:`str`
            path to deposit content to

        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents to
            be extracted in the directory corresponding to path


        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

            For details see :meth:`datasafe.manifest.Manifest.check_integrity`.


        Raises
        ------
        datasafe.exceptions.MissingPathError
            Raised if no path is provided

        datasafe.exceptions.MissingContentError
            Raised if no content is provided

        """
        if not path:
            raise MissingPathError(message="No path provided.")
        if not content:
            raise MissingContentError(
                message="No content provided to deposit."
            )
        tmpfile = tempfile.mkstemp(suffix=".zip")
        with open(tmpfile[1], "wb") as file:
            file.write(content)
        shutil.unpack_archive(tmpfile[1], self.working_path(path))
        with change_working_dir(self.working_path(path)):
            manifest = Manifest()
            manifest.from_file(manifest.manifest_filename)
            integrity = manifest.check_integrity()
        os.remove(tmpfile[1])
        return integrity

    def retrieve(self, path=""):
        """
        Obtain data from directory corresponding to path

        The data are compressed as ZIP archive and the contents of the ZIP
        file is returned as bytes.

        Parameters
        ----------
        path : :class:`str`
            path the data should be retrieved for

        Returns
        -------
        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents of
            the directory corresponding to path

        Raises
        ------
        datasafe.directory.MissingPathError
            Raised if no path is provided

        OSError
            Raised if path does not exist

        """
        if not path:
            raise MissingPathError(message="No path provided.")
        tmpfile = tempfile.mkstemp()
        zip_archive = shutil.make_archive(
            base_name=tmpfile[1],
            format="zip",
            root_dir=self.working_path(path),
        )
        with open(zip_archive, "rb") as zip_file:
            contents = zip_file.read()
        # noinspection PyTypeChecker
        os.remove(tmpfile[1] + ".zip")
        os.remove(tmpfile[1])
        return contents

    def get_manifest(self, path=""):
        """
        Retrieve manifest of a dataset stored in path.

        Parameters
        ----------
        path : :class:`str`
            path to the dataset the manifest should be retrieved for

        Returns
        -------
        content : :class:`str`
            contents of the manifest file

        """
        if not path:
            raise MissingPathError(message="No path provided.")
        if not os.path.exists(path):
            raise MissingPathError(message=f"Path {path} does not exist.")
        if not os.path.exists(os.path.join(path, self.manifest_filename)):
            raise MissingContentError(message="No MANIFEST file found.")
        with open(
            os.path.join(path, self.manifest_filename), "r", encoding="utf8"
        ) as file:
            manifest_contents = file.read()
        return manifest_contents

    def get_index(self):
        """
        Return list of paths to datasets

        Such a list of paths to datasets is pretty useful if one intends to
        check locally for existing LOIs (corresponding to paths in the
        datasafe).

        If a path has been created already, but no data yet saved in there,
        as may happen during an experiment to reserve the corresponding LOI,
        this path will nevertheless be included.

        Returns
        -------
        paths : :class:`list`
            list of paths to datasets

        """
        if self.root_directory:
            top = self.root_directory
        else:
            top = "."
        paths = []
        for root, dirs, _ in os.walk(top):
            for dir_ in dirs:
                files_in_dir = os.listdir(os.path.join(root, dir_))
                if not files_in_dir or self.manifest_filename in files_in_dir:
                    paths.append(
                        os.path.join(root, dir_).replace(
                            os.path.join(top, ""), ""
                        )
                    )
        return paths

    def check_integrity(self, path=""):
        """
        Check integrity of dataset, comparing stored with generated checksums.

        To check the integrity of a dataset, the checksums stored within the
        manifest file will be compared to newly generated checksums over
        data and metadata together as well as over data alone.

        Parameters
        ----------
        path : :class:`str`
            path to the dataset the integrity should be checked for

        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

        """
        if self.manifest_filename not in os.listdir(path):
            raise MissingContentError(message="No manifest file found.")
        manifest = Manifest()
        manifest.from_file(os.path.join(path, self.manifest_filename))
        return manifest.check_integrity()


def create_http_server(test_config=None):
    """
    Create a HTTP server for accessing the datasafe.

    Parameters
    ----------
    test_config : :class:`dict`
        Configuration for HTTP server

    Returns
    -------
    app : :class:`flask.Flask`
        WSGI application created via flask

    """
    app = Flask(__name__)  # , instance_relative_config=True)
    # app.config.from_object(Config())
    if test_config:
        app.config.from_mapping(test_config)

    @app.route("/heartbeat")
    def heartbeat():
        return "alive"

    @app.route("/api/")
    def api_test():
        return "alive"

    dataset = HTTPServerAPI.as_view("datasets")
    app.add_url_rule("/api/<path:loi>", view_func=dataset)

    return app


class HTTPServerAPI(MethodView):
    """
    API view used in the HTTP server.

    The actual server is created via :func:`create_http_server` and operates
    via flask. This API view provides the actual API functionality to access
    the datasafe and its underlying storage backend via HTTP.

    The API provides methods for the HTTP methods, currently GET, POST, PUT,
    and PATCH.

    Furthermore, exceptions are converted into the appropriate HTTP status
    codes and the message of the exception is contained in the response
    body. Thus, clients such as :class:`datasafe.client.HTTPClient` can
    convert the HTTP status codes back into Python exceptions.

    Attributes
    ----------
    server : :class:`datasafe.server.Server`
        Server backend that communicates with the storage backend.

    """

    def __init__(self):
        self.server = Server()

    def get(self, loi=""):
        """
        Handle get requests.

        The following responses are currently returned, depending on the
        status the request resulted in:

        ========= ==== ==============================
        Status    Code data
        ========= ==== ==============================
        success   200  dataset contents (ZIP archive)
        no data   204  message
        not found 404  error message
        invalid   404  error message
        ========= ==== ==============================

        The status "no data" results from querying a LOI that has been
        created (using POST), but no data uploaded to so far.

        The status "invalid" differs from "not found" in that the LOI
        requested is invalid.

        Parameters
        ----------
        loi : :class:`str`
            LOI of get request

        Returns
        -------
        response : :class:`flask.Response`
            Response object

        """
        try:
            content = self.server.download(loi=loi)
            status = 200
        except MissingContentError:
            content = "LOI does not have any content"
            status = 204
        except (LoiNotFoundError, InvalidLoiError) as exception:
            content = exception.message
            status = 404
        return content, status

    def post(self, loi=""):
        """
        Handle POST requests.

        A POST request will only create a new empty resource connected to
        the LOI, but never upload data. For uploading, use put. While this
        may seem like not conforming to the typical usage of POST requests,
        the reason is simple: :meth:`post` returns the newly created LOI,
        while :meth:`put` returns the JSON representation of the integrity
        check dict. Hence, to be able to check that the data have been
        successfully arrived at the datasafe storage backend,
        it is essential to separate POST and PUT requests.

        The following responses are currently returned, depending on the
        status the request resulted in:

        ========= ==== ==============================
        Status    Code data
        ========= ==== ==============================
        created   201  newly created LOI
        invalid   404  error message
        ========= ==== ==============================

        Parameters
        ----------
        loi : :class:`str`
            LOI of post request

        Returns
        -------
        response : class:`flask.Response`
            Response object

        """
        try:
            content = self.server.new(loi=loi)
            status = 201
        except InvalidLoiError as exception:
            content = exception.message
            status = 404
        return content, status

    def put(
        self,
        loi="",
    ):
        """
        Handle PUT requests.

        PUT requests are used to transfer data to an *existing* resource of the
        datasafe. To create a new resource, use :meth:`post` beforehand. If
        data exist already at the resource, this will result in an error
        (status code 405, see table below).

        The following responses are currently returned, depending on the
        status the request resulted in:

        ================ ==== ===========================================
        Status           Code data
        ================ ==== ===========================================
        success          200  JSON representation of integrity check dict
        does not exist   400  error message
        missing content  400  error message
        invalid          404  error message
        existing content 405  error message
        ================ ==== ===========================================

        The status "does not exist" refers to the LOI the data should be put
        to not existing (in this case, you need to first create it using
        PUSH). Therefore, in this particular case, status code 400 instead
        of 404 ("not found") is returned.

        The status "missing content" refers to the request missing data.

        The status "existing content" refers to data already present at the
        storage referred to with the LOI. As generally, you could update the
        content using another method, a status code 405 ("method not
        allowed") is returned in this case.

        Parameters
        ----------
        loi : :class:`str`
            LOI of put request

        Returns
        -------
        response : class:`flask.Response`
            Response object

        """
        header = None
        try:
            content = self.server.upload(loi=loi, content=request.data)
            status = 200
        except InvalidLoiError as exception:
            content = exception.message
            status = 404
        except (LoiNotFoundError, MissingContentError) as exception:
            content = exception.message
            status = 400
        except ExistingFileError as exception:
            content = exception.message
            status = 405
            header = {"allow": "PATCH"}
        return content, status, header

    def patch(self, loi=""):
        """
        Handle PATCH requests.

        PATCH requests are used to *update* data at an existing resource of the
        datasafe. To upload new data to an existing resource,
        use :meth:`put`. If no data exist at the resource, this will result
        in an error (status code 405, see table below).

        The following responses are currently returned, depending on the
        status the request resulted in:

        =================== ==== ===========================================
        Status              Code data
        =================== ==== ===========================================
        success             200  JSON representation of integrity check dict
        does not exist      400  error message
        missing content     400  error message
        invalid             404  error message
        no resource content 405  error message
        =================== ==== ===========================================

        The status "does not exist" refers to the LOI the data should be put
        to not existing (in this case, you need to first create it using
        PUSH). Therefore, in this particular case, status code 400 instead
        of 404 ("not found") is returned.

        The status "missing content" refers to the request missing data.

        The status "no resource content" refers to no data present at the
        storage referred to with the LOI. As generally, you could upload new
        content using another method, a status code 405 ("method not
        allowed") is returned in this case.

        Parameters
        ----------
        loi : :class:`str`
            LOI of put request

        Returns
        -------
        response : class:`flask.Response`
            Response object

        """
        header = None
        try:
            content = self.server.update(loi=loi, content=request.data)
            status = 200
        except InvalidLoiError as exception:
            content = exception.message
            status = 404
        except (MissingContentError, LoiNotFoundError) as exception:
            content = exception.message
            status = 400
        except NoFileError as exception:
            content = exception.message
            status = 405
            header = {"allow": "PUT"}
        return content, status, header
