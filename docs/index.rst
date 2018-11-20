.. EV Spatial Model documentation master file, created by
   sphinx-quickstart on Mon Sep 24 09:52:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

*********************
Overview and Examples
*********************

:Author:
    Mahmoud Shepero

:Developer:
    `Mahmoud Shepero <http://katalog.uu.se/empinfo/?id=N16-259>`_

:Email:
    mahmoud.shepero@angstrom.uu.se

:Version:
    0.0.1 of 24-09-2018

:License:
    `GNU General Public License v3.0 <https://www.gnu.org/>`_

:Acknowledgement:
    Special thanks to `Joakim Munkhammar <http://katalog.uu.se/empinfo/?id=N10-1405>`_ for his theoretical contributions.

Introduction
============
This is a spatial model to estimate the charging load of electric vehicles in
cities. The model is published in *Spatial Markov chain model for electric
vehicle charging in cities using geographical information system (GIS) data,
Applied Energy, 231C (2018), pp. 1089-1099*.

The model uses discrete Markov chain to spatially model the mobility of
cars in cities. If we assume that cars are moving between parking places. It
also assumes that parking places in cities can be clustered–based on nearby buildings–into
three distinct categories: Work, Home, and Other. Work category includes workplaces,
hospitals, universities and schools. Home describes residential places. Other
describes shopping, leisure, cultural, and religious locations.

.. image:: images/markovChainModel.pdf
   :height: 300 px
   :width: 300 px
   :align: center




Indixes and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

**Summary of model classes and functions:**

.. autosummary::

   ev.EV
   parkinglot.ParkingLot
   markov.Markov
   simulation.Simulation
   extractDistances.extractDistances
   extractFiles.readMatrixfiles



********
Examples
********

In this part few examples are provided. For a simple example to run the model
for one week is provided in the file *toyExample.py*.

Example 1::

    for i in list:
        print i



**********************
Model implementation
**********************

In this Section a detailed description for the model implementation is provided.

Electric vehicles
=================

.. automodule:: ev

.. autoclass:: EV
   :members:

.. autosummary::


Parking lots
============

.. automodule:: parkinglot

.. autoclass:: ParkingLot
   :members:

.. autosummary::

Markov chain implementation
===========================

.. automodule:: markov

.. autoclass:: Markov
   :members:

.. autosummary::

Model simulation implementation
===============================

.. automodule:: simulation

.. autoclass:: Simulation
   :members:

.. autosummary::

Auxiliary functions
===================

.. automodule:: extractDistances
   :members:

.. automodule:: extractFiles
   :members:

.. automodule:: auxiliary
   :members:
