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

Example 1, download all the OSM tags within a region:

.. code-block:: none

    /*
    Get all the tags of the amenity in this bounding box, save them into csv.
    The bounding box is given lat, long, lat, long. 
    This example gets the values for Gotland, Sweden
    */
    [out:csv(amenity)]
    [bbox:56.905303,18.091240,58.001904,19.347141];
    (	
        way
        ;
        >;
    );
    out;
        
Save the previous text into a file say *query.txt*, and to download the OSM tags you need to send this query to OSM Overpass API by doing the following

.. code-block:: bash

   $ wget -O Output.csv --post-file=query.txt "https://overpass-api.de/api/interpreter"

This code will save a csv file with all the tags in the amenity field in Gotland, Sweden. Note that there might be many empty rows.

Example 2, download OSM map with certain tags, e.g., parking locations in Gotland:

.. code-block:: none

    /* 
    Download the parking locations in Gotland, Sweden.
    */
    [bbox:56.905303,18.091240,58.001904,19.347141];
    (
      way
        ["building"~"garage|garages",i];
      
      way
        ["amenity"~"parking|parking_space",i];
    );
    (
        ._;
        >;
    );
    out; 

Similar to Example 1, we can download the data:

.. code-block:: bash

    $ wget -O output.osm --post-file=query.txt "https://overpass-api.de/api/interpreter"

Remeber to change the output file extension to *osm* instead of *csv*.



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
