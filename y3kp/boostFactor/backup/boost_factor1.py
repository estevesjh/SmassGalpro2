#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ebtihal Abdelaziz
# This code creates the boost factor model vector. 
import numpy as np
from cosmosis.datablock import names
from cosmosis.datablock import option_section
import Boost_factor_util


def setup(options):
    #in this section, we read the data to obtain the value of R .
    R,data_vector,sigma_B = np.genfromtxt("/global/homes/e/eabdelaz/cluster_2022/profiles/full-unblind-v2-mcal-zmix_y1clust_l{l}_z{z}_zpdf_boost.dat".format(l = 0, z = 0),unpack=True)
    z = np.round((np.unique(options["BoostFactor","zo_low"]) +np.unique(options["BoostFactor","zo_high"]))/2.,2)
    l = np.round((options["BoostFactor","lo_low"] +options["BoostFactor","lo_high"])/2.,2)
    #This needs to be removed once we read R from data block instead of data file. For other reasons why we are doing this check Bosst_factor_like. 
    variance = np.ones(R.size)*0.1**2
#creating lookup tabels
    bins = Boost_factor_util.lookup_table(l,z)
    return R,bins,z,l

def execute(block, config):
    #we are calculatng the model here and saving it in the boostfactor block.
    R,bins,z,l = config
    for L in l:
        for Z in z:
            bin_number = str(bins[L,Z])[1:-1].replace(", ","")
            Rs = block["Boost_Factor_Model_Values", "Rs"]
            B0 = block["Boost_Factor_Model_Values", "B0"]
            alpha_Rs = block["Boost_Factor_Model_Values", "alpha_Rs"]
            beta_Rs = block["Boost_Factor_Model_Values", "beta_Rs"]
            alpha_B0 = block["Boost_Factor_Model_Values", "alpha_B0"]
            beta_B0 = block["Boost_Factor_Model_Values", "beta_B0"]
            rs,b0 = Boost_factor_util.Boost_Factor_param(Z,L,Rs,alpha_Rs,beta_Rs,B0,alpha_B0,beta_B0)
            Boost_Factor=Boost_factor_util.Boost_Factor_Model(R, rs, b0)
            datablock_name="Boost_Factor_Model_{:s}".format(bin_number)
            block.put_double_array_1d("BoostFactor",datablock_name,Boost_Factor)
    return 0
   # there can be a function here to apply the boost factor to correlation functions

def cleanup(config):
     # nothing to do here!  We just include this
     # for completeness
     return 0


