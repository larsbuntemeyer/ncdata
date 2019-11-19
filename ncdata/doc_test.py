
"""This module provides a class to handle horizontal data used by :mod:`doc_test`
classes.
"""

import os

from pathlib import Path
#from PyRemo.OoPlot.Netcdf4Read import NetcdfRead
from netCDF4 import Dataset
import time
import logging


def get_cdo_history(datafile):
    history = datafile.history.splitlines()
    history.reverse()
    cdo_commands = []
    for line in history:
        if 'cdo' in line:
            cdo_commands.append(get_cdo_command_from_line(line))
    return cdo_commands


def test_function():
    """ This is my test function
    """
    pass


class FileReader(object):
    """Reads a NetCDF file, returns global and data field attributes.

    You can create a :class:`FileReader` object from scratch with this class.

    Written by Lars Buntemeyer  
    """

    def __init__(self, filename_str):
        """:class:`FileReader` constructor.
        
        **Arguments:**
            *filename_str:*
                The filename to read. 
        """
        self.filename_str = filename_str
        self.ignored_gridattrs = ['bounds', 'grid_mapping']
        self.ignored_variables = ['lat', 'lon', 'rlat', 'rlon']
        try:
            self.nc = Dataset(self.filename_str)
        except:
            raise Exception('could not read nc file: {}'.format(self.filename_str))

    def get_ncdict(self):
        """Returns a dictionary containing all global NetCDF attributes.
        """
        return {attr:self.nc.getncattr(attr) for attr in self.nc.ncattrs()}

    def get_varlist(self):
        """Returns a list of all NetCDF data fields. 
        """
        return self.nc.variables

    def get_cf_fields(self):
        """Returns a dictionary with all valid CF fields. NetCDF data fields
        that define a grid or mappring will be ignored.
        """
        fields = {} 
        return {varname: var for varname, var in self.nc.variables.items() \
                if varname not in self.get_ignored_nc_variables()}

    def get_ignored_nc_variables(self):
        """Returns a list of NetCDF data fields that should be ignored in
           the variable list of get_cf_fields.
        """
        ignored = self.ignored_variables
        metric  = []
        for varname, var in self.nc.variables.items():
            if varname in self.nc.dimensions:
                ignored.append(varname)
            metric += self.get_metric(varname)
        return ignored+metric

    def get_metric(self,varname):
        """Returns a list variable attributes that refers to
           grid attributes, e.g., grid mapping or bounds. 

        **Arguments:**
            *varname:*
                Name of the variable to check for attributes.

        """
        var     = self.nc.variables[varname]
        ncattrs = var.ncattrs()
        result = []
        for gridattr in self.ignored_gridattrs:
            if gridattr in ncattrs:
                result.append(var.getncattr(gridattr))
        return result
   
    def is_dimvar(self,varname):
        """Checks if a variable name refers to a NetCDF dimension.

        **Arguments:**
            *varname:*
                Name of the variable.

        """
        if varname in self.dimensions:
            return True
        else:
            return False

