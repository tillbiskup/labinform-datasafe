========
Concepts
========

The LabInform datasafe implements a number of concepts that are briefly described below.


Repository
==========

The LabInform datasafe is a *repository for "warm" research data*, but what is a repository, anyway? As in the research data management bubble many terms are used but too often neither properly defined nor fully understood, let's start with a definition:


repository:
    publication platform for *i.a.* research data usually provided by institutions, organisations or companies. Tasks are storing research data on a long-term basis, documenting the research data with metadata, regulating access (including licences) to the research data and assigning a PID to each item.


Prominent examples of public repositories for research data are `Zenodo <https://zenodo.org/>`_ (hosted by `CERN <https://cern.ch/>`_) or `figshare <https://figshare.com/>`_, but there are others available of course as well.

While those public repositories are well-suited for publishing the data accompanying a textual publication, *i.e.* the data the results and conclusions of the textual publication is based on, these platforms are no real option for storing all those yet unpublished data (*"warm" research data*) from their initial acquisition up to the point where they may eventually be used in a publication or published themselves.

Usually, those "warm" research data are stored on some hard drive, either on the computer attached to the devices used for data acquisition and/or the local hard drives of those people involved in processing and analysing the data. However, at least in academia and in the context of small research groups, there is often no real strategy how to store the data independent of the file system hierarchy of an individual researcher in a way that they are accessible (from within the research group) after months or years, and particularly even if the person originally recording the data is long gone.

The LabInform datasafe serves as the "central data dump" of a research group and provides access via unique and persistent identifiers (see below), abstracting entirely from the local file system by means of its client-server architecture.


Access via unique and persistent identifiers
============================================

Usually, research data (at least the digital ones) reside as files in the file system of some hard drive, at best on a network drive that is regularly backed up. However, paths in a file system are neither necessarily unique nor really persistent or long(er)-term stable.

In order to be more reproducible with our data analysis, we not only need a gap-less record of each step of the data processing and analysis starting with the actual data -- see the `ASpecD framework <https://docs.aspecd.de/>`_ for this purpose --, but we need unique and persistent identifiers as well, allowing to locate the data that were used in the analysis.

Most of the data we acquire will never be published, but that does not mean that these data are useless or of inferior quality. Too often we simply cannot find the data any more, and as soon as somebody reorganises the directory hierarchy containing the data, all paths used in prior analysis usually breaks, together with reproducibility and traceability.

The LabInform datasafe makes use of the *Lab Object Identifier* (LOI), a concept very similar to the well-known *digital object identifier* (DOI). The major difference between DOI and LOI: the latter is issued locally and does not depend on any external service provider. This allows to register an LOI for every single dataset we record, as well as for every individual sample, analysis, resulting graphical representation, setup, or whatever else needs to be addressed uniquely.

While the LOI is a useful concept in a much broader context, for the LabInform datasafe it is used to uniquely and persistently address the contents (mainly research data) of the local repository.

A note on the term "persistent identifier": Some people think that only IDs issued by a public organisation are truly persistent. However, this is a quite narrow view, and even the organisations behind DOI, ARK, ORCID, ISBN, or whatever else are not old enough to prove actually persistent. Furthermore, persistent basically means that the identifier will not change, and that you are able to deduce which resource it once pointed to, even if the resource is long gone.


Client-server architecture
==========================

A key concept of the LabInform datasafe is to abstract away from the actual storage of the "warm" research data it contains. Never bother on which hard drive and in what directory to look for the data you need *urgently now* for your current publication. This abstraction requires using some kind of interface, and in digital terms, it is implemented using a client-server architecture, where clients ask a server for a resource, using a particular protocol and unique identifier for the resource.

The entire internet is based on the client-server architecture, and you can setup the same locally. Eventually, it does not matter where the server is located, as long as it is accessible. Of course, storing your precious research data, the LabInform datasafe server component should better be located in a safe place entirely under your control.


Checksums for detecting data corruption
=======================================

Preserving digital data for a long time is a still unsolved problem. Furthermore, flipping a single bit may be sufficient to corrupt an entire file, rendering it unreadable and hence useless. While minimising the chances for loss of data is the realm of backup and storage strategies, checksums can be used to *detect* data corruption, both during transport and on rest.

The LabInform datasafe uses checksums (cryptographic hashes) extensively to detect problems during data transfer between server and client. As it stores the checksums in the datasafe as well, these checksums can be used to detect data corruption on the server side as well.
