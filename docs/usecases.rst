=========
Use cases
=========

For the time being, the following description of use cases is rather an idea how working with the LabInform datasafe package may look like than a description of what actually can be achieved.

Currently (as of 09/2024), a command-line interface (CLI) is still missing that would greatly facilitate working with the LabInform datasafe. Furthermore, the integration into *Recipe-driven data analysis* using the `ASpecD framework <https://docs.aspecd.de/>`_ and related packages is not yet complete.


Overview
========

* General scenario: one central place for all research data
* Setting up the server and storage backend
* Pre-registering an LOI before data acquisition
* Uploading data
* Accessing data (I): manual access
* Accessing data (II): from within a recipe


General scenario: one central place for all research data
=========================================================

The *raison d'être* of the LabInform datasafe is to have one central (local) place to store all "warm" research data and to provide access independent of the internal organisation of the data within the repository, by means of unique and persistent identifiers (LOIs).


Setting up the server and storage backend
=========================================

Before actually being able to work with the datasafe and store and retrieve data, you need to setup the server and storage backend components.

TBD


Pre-registering a LOI before data acquisition
=============================================

When starting a measurement or data acquisition, usually we have already most of the information necessary to create a LOI at hand: which type of measurement and what sample. The one thing we would like to *not* care about is the number of the current measurement. This implies that measurements on one sample with a given method are numbered consecutively.

Of course, pre-registering a LOI requires some way of access to the (local) datasafe. However, this is not necessarily the same computer you perform the measurements with, as all you are interested is the actual LOI and the pre-registering in the datasafe server (and with its backend), in order to have a unique ID and be able to later upload the files.

Suppose you have a "base" LOI with all information at hand, except the number of the measurement::

    42.1001/ds/exp/sa/42/cwepr/

Providing this "base" LOI to the datasafe to create and register the next LOI will return the registered LOI to you. Registering a LOI is a matter of issuing a command on the command line::

    datasafe create <LOI>

or in our particular case::

    datasafe create 42.1001/ds/exp/sa/42/cwepr/

Suppose that the last measurement stored in the datasafe has the number 20. In this case, the datasafe server will return the following pre-registered LOI to you::

    42.1001/ds/exp/sa/42/cwepr/21

Of course, you can (and should) do two things with this: use it for your internal documentation, and save the information for later, when uploading the actual data that you have acquired in the meantime.

For more information, see the documentation of the :meth:`datasafe.client.Client.create` method that is eventually used to perform this action.


Uploading data
==============

Once you have acquired your data and reserved/created a LOI for them, it is time to upload the data to the datasafe. In its simplest form, this would be a single command with only a LOI provided::

    datasafe upload 42.1001/ds/exp/sa/42/cwepr/21

This will upload all the files in the current directory to the datasafe using the LOI provided. If no manifest has been created, this will automatically be done for you. Note that an exception will be thrown and returned as error if data exist already for this LOI in the datasafe. This prevents you from accidentally overwriting your data. If, however, you would like to *update* rather than upload data, use the ``update`` command described below.

For more information, see the documentation of the :meth:`datasafe.client.Client.upload` method that is eventually used to perform this action.


Updating data
=============

Sometimes, you would like to update the data stored in the datasafe, *e.g.* fix a typo or otherwise incorrect information in the metadata. For this, you need to know the LOI corresponding to the dataset, and there need to be data present in the datasafe for this LOI. This is the big difference to the upload procedure. Otherwise, the basic use is quite similar::

    datasafe update 42.1001/ds/exp/sa/42/cwepr/21

This will upload all the files in the current directory to the datasafe using the LOI provided, thus updating the contents of the datasafe. As this overwrites the files present in the datasafe, make sure that you know exactly what you are doing.

For more information, see the documentation of the :meth:`datasafe.client.Client.update` method that is eventually used to perform this action.


Accessing data (I): manual access
=================================

Downloading data from the datasafe is as simple as issuing a single command, using nothing more than the corresponding LOI::

    datasafe dowload 42.1001/ds/exp/sa/42/cwepr/21

This will download the data corresponding to the LOI from the datasafe and store them locally. The LOI is checked for belonging to the datasafe. Further checks will be done on the server side, resulting in exceptions raised if there are some problems. Upon successful download data are checked for integrity and in case of possible data or metadata corruption a warning is issued.

For more information, see the documentation of the :meth:`datasafe.client.Client.download` method that is eventually used to perform this action.


Accessing data (II): from within a recipe
=========================================

**Recipe-driven data analysis** using the `ASpecD framework <https://docs.aspecd.de/>`_ and packages based on it is a paradigm-shift in data processing and analysis, requiring no longer programming skills. All tasks are defined using a simple YAML file that is afterwards "served" using a single command on the command line. Generally, an ASpecD recipe may look like this:


.. code-block:: yaml
    :linenos:

    format:
      type: ASpecD recipe
      version: '0.2'

    datasets:
      - /path/to/first/dataset
      - /path/to/second/dataset

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf


Here, the datasets are defined by paths in the (local) file system. How about using LOIs and having the data accessed directly from the datasafe? The same recipe would only change in lines 6 and 7:


.. code-block:: yaml
    :linenos:

    format:
      type: ASpecD recipe
      version: '0.2'

    datasets:
      - loi:42.1001/ds/exp/sa/42/cwepr/1
      - loi:42.1001/ds/exp/sa/42/cwepr/2

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf


Of course, this requires two things: a locally accessible installation of the LabInform datasafe and a specialised importer mechanism hooking into ASpecD to access the data from the locally configured datasafe via the LOI.

