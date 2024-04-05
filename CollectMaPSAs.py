import argparse
import sys, os
import csv
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
import matplotlib.pyplot as plt

from derivative import *
import MakeModulePlots

import warnings
warnings.filterwarnings("ignore")

def get_recent(cmd):

    files = os.popen(cmd).read().split()

    if len(files) < 1:
        print("Error: no files specified")
        return "0"

    # to be added: if a file contains "skipped test" then remove it from the list

    elif len(files) == 1:
        return files[0]

    else:
        maxnbr = 0
        maxidx = -1

        for j, f in enumerate(files):
            numbers_from_string = int(''.join(list(filter(str.isdigit, f))))
            if numbers_from_string > maxnbr:
                maxnbr = numbers_from_string
                maxidx = j
        return files[maxidx]

class MPA:
    """MPA class"""
    def __init__(self, mapsa_name, chip_number, log_file, scurves):
        self.mapsa_name = mapsa_name
        self.index = chip_number
        self.directory = '../Results_MPATesting/' + mapsa_name + '/'

        self.log_file = log_file

        self.serial_number = self.serial_number()
        self.fill_pixels()
        self.set_currents()
        #            self.add_derivative()

        if scurves:
            print("Saving s-curves")
            self.set_Scurves()

    def serial_number(self):
        if len(self.log_file) <= 1:
            return -1

        cmd = "grep \"Serial Number\" " + self.log_file
        number = os.popen(cmd).read()

        if "(" in number and ")" in number:

            number = number.split("(")[1].split(")")[0]

            pos, wafer_n, lot, status, process, adc_ref = number.split(",")

            val = int(pos)
            val += (2**8)*int(wafer_n)
            val += (2**13)*int(lot)
            val += (2**20)*int(status)
            val += (2**22)*int(process)
            val += (2**27)*int(adc_ref)

            pos =val & 0xFF
            wafer_n =(val >> 8) & 0x1F
            lot =(val >> 13) & 0x7F
            status =(val >> 20) & 0x3 
            process =(val >> 22) & 0x1F 
            adc_ref =(val >> 27) & 0x1F 

            return val

        else:
            return int(number.split("=")[1])
        
    def set_currents(self):

        if len(self.log_file) <= 1:
            self.I_ana = -1
            self.I_dig = -1
            self.I_pad = -1
            self.I_tot = -1

        # I_ana
        cmd = "grep P_ana " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        if len(y) <= 1:
            self.I_ana = -1
        else:
            self.I_ana = float(y[1])

        # I_dig
        cmd = "grep P_dig " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        if len(y) <=1:
            self.I_dig = -1
        else:
            self.I_dig = float(y[1])

        # I_pad
        cmd = "grep P_pad " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        if len(y) <= 1:
            self.I_pad = -1
        else:
            self.I_pad = float(y[1])

        # I_tot
        cmd = "grep Total: " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        if len(y) <=1:
            self.I_tot = -1
        else:
            self.I_tot = float(y[1])

        return

    def fill_pixels(self):

        self.pixels = pd.DataFrame()
        
        cmd = 'ls '+ self.directory + 'mpa_test_*_'+ str(self.index) + '_*_pixelalive.csv'
        if len(get_recent(cmd)) > 1:
            self.pixels = pd.read_csv(get_recent(cmd),index_col=0,header=0)
            self.pixels.columns = ['pa']
        else:
            self.pixels['pa'] = [-1]*1888
            
        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PostTrim_CAL_CAL_RMS.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['CAL_RMS'] = tmp['value']
#            self.pixels['CAL_RMS'][abs(self.pixels['CAL_RMS']-2.0)<0.000001] = -1
#            self.pixels['CAL_RMS'][self.pixels['pa']<100] = np.nan
#            print('CAL_RMS')
#            print(self.pixels['CAL_RMS'])
        else:
            self.pixels['CAL_RMS'] = [-1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PostTrim_CAL_CAL_Mean.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['CAL_Mean'] = tmp['value']
#            self.pixels['CAL_Mean'][self.pixels['CAL_RMS']<0] = np.nan
#            self.pixels['CAL_Mean'][self.pixels['pa']<100] = np.nan
#            print('CAL_Mean')
#            print(self.pixels['CAL_Mean'])
        else:
            self.pixels['CAL_Mean'] = [1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PostTrim_THR_THR_RMS.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['THR_RMS'] = tmp['value']
#            self.pixels['THR_RMS'][abs(self.pixels['THR_RMS']-2.0)<0.000001] = -1
#            self.pixels['THR_RMS'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['THR_RMS'] = [-1]*1888
            
        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PostTrim_THR_THR_Mean.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['THR_Mean'] = tmp['value']
#            self.pixels['THR_Mean'][self.pixels['THR_RMS']<0] = np.nan
#            self.pixels['THR_Mean'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['THR_Mean'] = [-1]*1888
            
        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PreTrim_CAL_CAL_RMS.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['CAL_RMS_pretrim'] = tmp['value']
            self.pixels['CAL_RMS_pretrim'][abs(self.pixels['CAL_RMS_pretrim']-2.0)<0.00001] = -1
            self.pixels['CAL_RMS_pretrim'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['CAL_RMS_pretrim'] = [-1]*1888
            
        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PreTrim_CAL_CAL_Mean.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['CAL_Mean_pretrim'] = tmp['value']
            self.pixels['CAL_Mean_pretrim'][self.pixels['CAL_RMS_pretrim']<0] = np.nan
            self.pixels['CAL_Mean_pretrim'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['CAL_Mean_pretrim'] = [-1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PreTrim_THR_THR_RMS.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['THR_RMS_pretrim'] = tmp['value']
            self.pixels['THR_RMS_pretrim'][abs(self.pixels['THR_RMS_pretrim']-2.0)<0.000001] = -1
            self.pixels['THR_RMS_pretrim'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['THR_RMS_pretrim'] = [-1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_PreTrim_THR_THR_Mean.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['THR_Mean_pretrim'] = tmp['value']
            self.pixels['THR_Mean_pretrim'][self.pixels['THR_RMS_pretrim']<0] = np.nan
            self.pixels['THR_Mean_pretrim'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['THR_Mean_pretrim'] = [-1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_BumpBonding_Noise_BadBump.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['Bump_RMS'] = tmp['value']
            self.pixels['Bump_RMS'][abs(self.pixels['Bump_RMS']-2.0)<0.000001] = -1
            self.pixels['Bump_RMS'][self.pixels['pa']<100] = np.nan
        else:
            self.pixels['Bump_RMS'] = [-1]*1888

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) + '_*_mask_test.csv'
        if len(get_recent(cmd)) > 1:
            tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
            self.pixels['mask'] = tmp['value']

            if abs(np.sum(tmp['value'])) > 0:
                print('Unmaskable',self.index)

        else:
            self.pixels['mask'] = [-1]*1888

        return

    # S curves
    def set_Scurves(self):

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) +'_*_PostTrim_CAL_CAL.csv'
        self.CALS = pd.read_csv(get_recent(cmd),index_col=0,header=0)

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) +'_*_PostTrim_THR_THR.csv'
        self.THRS = pd.read_csv(get_recent(cmd),index_col=0,header=0)

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) +'_*_PreTrim_CAL_CAL.csv'
        if len(get_recent(cmd)) > 1:
            self.CALS_pretrim = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        else:
            self.CALS_pretrim = -1

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) +'_*_PreTrim_THR_THR.csv'
        if len(get_recent(cmd)) > 1:
            self.THRS_pretrim = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        else:
            self.THRS_pretrim = -1

        cmd = 'ls '+ self.directory + 'mpa_test_*_'+str(self.index) +'_*_BumpBonding_SCurve_BadBump.csv'
        self.BumpS = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        
        return

class MaPSA:
    """MaPSA class"""
    def __init__(self, name, label, kapton, scurves=False):

        # Set some properties
        self.name = name
        self.label = label
        self.kapton = kapton
        self.directory = '../Results_MPATesting/' + self.name + '/'
        self.mpa_chips = []
        self.set_IV()

        # Add MPAs
        for i in range(1,17):
            cmd = 'ls '+ self.directory +'log*_'+ str(i) +'_*.log'
            log_file = get_recent(cmd)

            if log_file == '0':
                print("Chip "+str(i)+" was not tested. Skipping")
            else:
                chip = MPA(self.name,i,log_file,scurves)
                self.add_mpa(chip)
        
        # Pickle it
        print("Pickling MaPSA " + self.name)
        mapsafile = open('pickles/'+self.label+'.pkl', 'wb')
        pickle.dump(self, mapsafile)
        mapsafile.close()

        MakeModulePlots.PlotAllPlotsModulesAutomated(self.name,mapsaname=self.label,show_plot=False,save_plot=True)
        
    def add_mpa(self, mpa):
        if(len(self.mpa_chips) >= 16):
            print("Error: MaPSA already has 16 associated MPAs")
            return

        self.mpa_chips += [mpa]
        print("Constructed " + self.name + " Chip " + str(len(self.mpa_chips)))

        return

    def set_IV(self):

        cmd = 'ls ../Results_MPATesting/'+ self.name+ '/IVScan_'+self.name+'*.csv'
        csvfilename = get_recent(cmd)

        Vpoints = []
        Ipoints = []
        with open(csvfilename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:

                if row[0] == '':
                    continue

                if(float(row[-1]) !=0 ):
                    Vpoints += [float(row[len(row)-2])]
                    Ipoints += [float(row[-1])]
                else:
                    Vpoints += [float(row[len(row)-4])]
                    Ipoints += [float(row[len(row)-3])]
                    
        df = pd.DataFrame()
        df["V"] = Vpoints
        df["I"] = Ipoints
        self.IV = df

        fig = plt.figure(figsize=(10,5))
        plt.scatter(x=abs(df["V"]),y=abs(df["I"]))
        plt.xlabel("V [V]")
        plt.ylabel("I [uA]")
        plt.suptitle(self.name)

        if not os.path.exists("./plots/"+self.label):
            os.mkdir("./plots/"+self.label)
        fig.savefig("./plots/"+self.label+"/ScanIV_"+self.label+".png")
        fig.savefig("./plots/"+self.label+"/ScanIV_"+self.label+".pdf")

        plt.close()

        return 

def main():

    parser = argparse.ArgumentParser(description='MaPSA summary plots')
#    parser.add_argument('-n','--name',nargs='+',help='name of output directory')
    parser.add_argument('-f','--files',nargs='+',help='list of text files containing names of MaPSAs to process')
    args = parser.parse_args()

    mapsa_names = []
    mapsa_labels = []
    kapton = []
    mapsas = []
    
    for f1 in args.files:
        print('Reading MaPSA names from ' + f1)
        with open(f1) as f:
            reader = csv.reader(f,delimiter=' ')
            mapsa_info = [row for row in reader]
            mapsa_names = [row[0] for row in mapsa_info]
            mapsa_labels = [row[1] for row in mapsa_info]
            kapton = [row[2] for row in mapsa_info]

    print(mapsa_labels)

    scurves = True

    for i in range(len(mapsa_names)):

        # Read MaPSA object from file, if available
        fname = 'pickles/'+mapsa_labels[i]+'.pkl'
#        if os.path.isfile(fname):
#            print("Loading MaPSA " + mapsa_labels[i])
#            mapsa = pickle.load(open(fname,'rb'))
#        else: # Create it
        if not os.path.isfile(fname):
           mapsa = MaPSA(mapsa_names[i],mapsa_labels[i],kapton[i],scurves)
           mapsas += [mapsa]

#    name = args.name[0]

if __name__ == "__main__":
    main()
