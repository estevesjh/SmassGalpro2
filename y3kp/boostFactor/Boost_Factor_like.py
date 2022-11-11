#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ebtihal Abdelaziz
# This code calculates likelihoods based on the difference between the data and the model. 
#data is also read in this module.

from __future__ import division, print_function
from cosmosis.datablock import names, option_section

from fitsio import FITS
import numpy as np
import os
import Boost_factor_util

# path = "/global/homes/e/eabdelaz/cluster_2022/profiles"
path = "/global/cfs/cdirs/des/jesteves/data/boost_factor/y1/profiles"

def setup(options):
#    This function makes a dictionary of the boost factor data given a lambda and redshift bins. 
    B= dict()
    z = np.round((np.unique(options["BoostFactor","zo_low"]) +np.unique(options["BoostFactor","zo_high"]))/2.,2)
    l = np.round((options["BoostFactor","lo_low"] +options["BoostFactor","lo_high"])/2.,2)
    bins = Boost_factor_util.lookup_table(l,z)
    for L in range(7):
        for Z in range(3):
            R,data_vector,sigma_B = np.genfromtxt(path+"/full-unblind-v2-mcal-zmix_y1clust_l{l}_z{z}_zpdf_boost.dat".format(l = L, z = Z),unpack=True)
            covariance = np.genfromtxt(path+"/full-unblind-v2-mcal-zmix_y1clust_l{l}_z{z}_zpdf_boost_cov.dat".format(l = L, z = Z),unpack=True)
# the error bars on the last two points of the data are tiny, so the MCMC is doing its best to fit for them. (They are tiny due to bad data)
#The following rewrites them. 
            ix=np.nonzero(sigma_B < 10**(-6))
            sigma_B[ix]=10**6
            covariance[ix,:]= 10**6
            covariance[:,ix]=10**6
            B[L,Z]=data_vector,sigma_B,covariance
    
    # first step: fit Rs, B0 for each bin
    # add datablock Rs, B0 for each bin
    
    return R,B,z,l,bins

def execute(block, config):
    #we are parsing through bins of redshift and lambda to calculate the likelihoods. 
    #the code allows for using the uncertainty given with the data or the covariance matrix. 
    R,B,z,l,bins = config
    chisqsum = 0
    for L in l:
        for Z in z:
            bin_number = str(bins[L,Z])[1:-1].replace(", ","")
            datablock_name="Boost_Factor_model_{:s}".format(bin_number)
            Model_B = block["BoostFactor", datablock_name]
            sigma_int = block["Boost_Factor_Model_Values", "scatter"]
            
            # to be implemented
            #sigma_int = block["Boost_Factor_Model_Values", "scatter_b0"]
            #sigma_rs = block["Boost_Factor_Model_Values", "scatter_rs"]
            
            data_vector,sigma_B,covarience = B[bins[L,Z]]
            diff = ((Model_B)-(data_vector))
            chisq = (diff)**2/(sigma_B**2+sigma_int**2)
            
            # to be implemented
            # diff2 = np.c_[(b0_fit-b0_predicted),(rs_fit-rs_predicted)]
            # pcov_int = np.array([[sigma_int_b0**2, 0], [0, sigma_int_rs**2]])
            # chisq += np.matmul(diff2, np.matmul(pcov+pcov_int, diff2))
            
#            precision = np.linalg.inv(covarience)
#            chisq = np.matmul(diff, np.matmul(precision, diff))
            chisqsum += chisq.sum()
    log_P = (-chisqsum/2)
 #   print('chisq:', chisqsum)
    #print('chisq:', chisqsum/((chisq.size-1)))
    block[names.likelihoods, 'Boost_Factor_like_like'] = log_P
    return 0
#            chisqsum += chisq.sum()
#    print('chisq:', chisqsum/(z.size*l.size*(Model_B.size-1)))

def cleanup(config):
    # nothing to do here
    pass

