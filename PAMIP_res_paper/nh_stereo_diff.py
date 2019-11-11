#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 13:12:45 2019

@author: jstreffi-local

Input arguments:
	1 	Id of first experiment
	2	Id of second experiment
	3	Resulution of experiments
	4 	Parameter name in netcdf file
	5 	Parameter name in name of netcdf file
	6 	Basepath of experiments on this machine
	7	Number by which the variable should be diveded before plotting (e.g 9.81 for pressure)
	8 	Plotoutput path on this machine
	9	Name of colormap module
	10	List of colorbar points
"""

import sys
import numpy as np
from scipy.io import netcdf
from scipy import interpolate
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.pylab import *
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import Ngl

np.random.seed(12345678)

if str(sys.argv[9]) == "true":
	print("hashing insignifcant changes")


if __name__ == '__main__':
    exp1=str(sys.argv[1])
    exp2=str(sys.argv[2])
    res=str(sys.argv[3])
    basepath=str(sys.argv[6])
    outpath=str(sys.argv[8])
    datapath1=basepath+res+'/Experiment_'+exp1+'/ensemble_mean/'
    datapath2=basepath+res+'/Experiment_'+exp2+'/ensemble_mean/'
    if str(sys.argv[9]) == "true":
       datapath3=outpath+'/large/'
    
    if str(sys.argv[11]) == "colorbar_TR_15":
       from colorbar_TR_15 import cmap_TR
    if str(sys.argv[11]) == "colorbar_TR_70":
       from colorbar_TR_70 import cmap_TR

    param=str(sys.argv[4])
    paramname=str(sys.argv[5])
    mapticks=map(float, sys.argv[10].split(','))
    
    itimes=0
    fig = plt.figure(figsize=(8,8))
    
    for season in ['_DJF', '_MAM', '_JJA', '_SON']:
    
       ncfile1 = datapath1+paramname+'_ensmean'+season+'.nc'
       ncfile2 = datapath2+paramname+'_ensmean'+season+'.nc'
       if str(sys.argv[9]) == "true":
          ncfile3 = datapath3+res+'_ensstd_'+paramname+season+'_'+exp1+'-'+exp2+'.nc'
          print ncfile3
       print ncfile1
       print ncfile2
    
    
       dataset1 = Dataset(ncfile1) 
       dataset2 = Dataset(ncfile2) 
       if str(sys.argv[9]) == "true":
          dataset3 = Dataset(ncfile3) 
       
       # Loading data from datasets
       data1 = dataset1.variables[param][:]
       data2 = dataset2.variables[param][:]
       if str(sys.argv[9]) == "true":
          data3 = dataset3.variables[param][:]

       # in case data has multiple levels, select only the 6th one (50000 hPa)
       print(np.squeeze(data1).shape)
       print(len(np.squeeze(data1).shape))
       if (len(np.squeeze(data1).shape)) == 3:
          data1 = data1[0,5,:,:]
          data2 = data2[0,5,:,:]
          data3 = data3[0,5,:,:]


       # Split data and concatenate in reverse order to turn by 180° to Prime meridian
       ds1,ds2 = np.hsplit(np.squeeze(data1),2)
       data_cat1 = np.concatenate((ds2,ds1),axis=1)/float(sys.argv[7])
       ds1,ds2 = np.hsplit(np.squeeze(data2),2)
       data_cat2 = np.concatenate((ds2,ds1),axis=1)/float(sys.argv[7])
       if str(sys.argv[9]) == "true":
          ds1,ds2 = np.hsplit(np.squeeze(data3),2)
          data_cat3 = np.concatenate((ds2,ds1),axis=1)/float(sys.argv[7])


       # Loading coords, turning longitude coordiante by 180° to Prime meridian
       lons = dataset1.variables[u'lon'][:]-180
       lats = dataset1.variables[u'lat'][:]

       # add cyclic point to data array and longitude
       data_cat1 ,lons = Ngl.add_cyclic(data_cat1, lons)		
       data_cat2 = Ngl.add_cyclic(data_cat2)	
       if str(sys.argv[9]) == "true":
          data_cat3 = Ngl.add_cyclic(data_cat3)	
    

       # Calculate where the standard deviation of dataset 1 is larger than the difference between 1 and 2
       if str(sys.argv[9]) == "true":
          data4 = data_cat3 < np.absolute(data_cat2-data_cat1)


       # Set position of subplot and some general settings for cartopy
       ax=plt.subplot(2,2,itimes+1,projection=ccrs.NorthPolarStereo())
       ax.set_extent([-180, 180, 29, 29], ccrs.PlateCarree())
       ax.add_feature(cfeature.COASTLINE)

       # Configuring cartopy gridlines
       gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=0.3, color='black',  alpha=0.5)
       gl.xlocator = mticker.FixedLocator([-180,-135,-90,-45,0,45,90,135,180])
       gl.ylocator = mticker.FixedLocator([80, 60, 30, 0])



       plt.tight_layout(pad=2)
    
       cmap_TR.set_over("darkred")
       cmap_TR.set_under("deeppink")

       if str(sys.argv[9]) == "true":
          im=plt.contourf(lons, lats, data4, hatches=[' ','...'],cmap=cmap_TR, extend='both',transform=ccrs.PlateCarree(),zorder=2, alpha=0)
       im=plt.contourf(lons, lats, data_cat2-data_cat1, levels=mapticks, cmap=cmap_TR, extend='both',transform=ccrs.PlateCarree(),zorder=1)
  
       if ( itimes == 0 ):
          plt.text(0.00, 1.03, 'DJF', horizontalalignment='left', fontsize=18, transform=ax.transAxes)
       elif ( itimes == 1):
          plt.text(0.00, 1.03, 'MAM', horizontalalignment='left', fontsize=18, transform=ax.transAxes)
       elif ( itimes == 2):
          plt.text(0.00, 1.03, 'JJA', horizontalalignment='left', fontsize=18, transform=ax.transAxes)
       elif ( itimes == 3):
          plt.text(0.00, 1.03, 'SON', horizontalalignment='left', fontsize=18, transform=ax.transAxes)
       
        
       itimes=itimes+1
    
fig.subplots_adjust(left=0.01, right=0.85, bottom=0, top=0.98, wspace = 0.1, hspace=-0.1)
cbar_ax = fig.add_axes([0.88, 0.06, 0.03, 0.87])
cbar_ax.tick_params(labelsize=int(sys.argv[12])) 
fig.colorbar(im, cax=cbar_ax, orientation='vertical', extend='both',ticks=mapticks)
fig.savefig(outpath+paramname+'_'+exp2+'_'+exp1+'_'+res+'_map_diff.png')


