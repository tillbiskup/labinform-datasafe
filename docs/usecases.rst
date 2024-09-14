=========
Use cases
=========

For the time being, the following description of use cases is rather an idea how working with the LabInform datasafe package may look like than a description of what actually can be achieved.

Currently (as of 09/2024), a command-line interface (CLI) is still missing that would greatly facilitate working with the LabInform datasafe. Furthermore, the integration into *Recipe-driven data analysis* using the `ASpecD framework <https://docs.aspecd.de/>`_ and related packages is not yet complete.


Overview
========

* General scenario: one central place for all research data
* Pre-registering an LOI before data acquisition
* Uploading data
* Accessing data (I): manual access
* Accessing data (II): from within a recipe


General scenario: one central place for all research data
=========================================================

The *raison d'être* of the LabInform datasafe is to have one central (local) place to store all "warm" research data and to provide access independent of the internal organisation of the data within the repository, by means of unique and persistent identifiers (LOIs).



Pre-registering a LOI before data acquisition
=============================================


Uploading data
==============


Accessing data (I): manual access
=================================


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

