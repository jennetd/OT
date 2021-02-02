import argparse
import sys, os
import csv
#import pickle as pkl
import cPickle

def get_recent(cmd):

    files = os.popen(cmd).read().split()

    if len(files) < 1:
        print("Error: no files specified")
        return ["error"]

    elif len(files) == 1:
        return files[0]

    else:
        maxnbr = 0
        maxidx = -1
        for j, f in enumerate(files):
            numbers_from_string = filter(str.isdigit, f)                                                          
            if numbers_from_string > maxnbr:                                                                      
                maxnbr = numbers_from_string                                                                      
                maxidx = j        
        return files[maxidx]

# needs added:
# memory - number of errors per chip, look for weird examples/ failures. Tests memory of mapsa where hit info is stored. Writing known values to memory that stores hits/trigger.
# registry tests - number of errors per chip, look for weird examples/ failures. Programs each register on MPA and reads it back. 3 tests - periphery, whole MPA, individual pixels.
# pixel alive - map of dead and inefficient pixels. Z = number of chips. Single MPA map, if time full mapsa (low stats)

class MPA:
    """MPA class"""
    def __init__(self, mapsa_name, chip_number):
        self.mapsa_name = mapsa_name
        self.index = chip_number
        self.directory = '/uscms/home/jennetd/nobackup/mapsa-round2/Results_MPATesting/' + mapsa_name + '/'

        cmd = 'ls '+ self.directory +'log*_Chip'+ str(self.index) +'_*.log'
        self.log_file = get_recent(cmd)
        
        self.set_currents()
        self.set_Scurves()
        self.set_MEANandRMS()

    def set_currents(self):
        # I_ana
        cmd = "grep P_ana " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        self.I_ana = float(y[1])

        # I_dig
        cmd = "grep P_dig " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        self.I_dig = float(y[1])

        # I_pad
        cmd = "grep P_pad " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        self.I_pad = float(y[1])

        # I_tot
        cmd = "grep Total: " + self.log_file
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        self.I_tot = float(y[1])

        return

    def read_values(self, cmd):
        csvfilename = get_recent(cmd)
        values = []
        with open(csvfilename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[0] == '':
                    continue
                pixedid = int(row[0])
                value = float(row[1])
                values.append(value)
        return values        

    def set_MEANandRMS(self):

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_CAL_CAL_Mean.csv'
        self.CAL_Mean = self.read_values(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_CAL_CAL_RMS.csv'
        self.CAL_RMS = self.read_values(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_THR_THR_Mean.csv'
        self.THR_Mean = self.read_values(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_THR_THR_RMS.csv'
        self.THR_RMS = self.read_values(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_CAL_CAL_Mean.csv'
        self.CAL_Mean_pretrim = self.read_values(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_CAL_CAL_RMS.csv'
        self.CAL_RMS_pretrim = self.read_values(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_THR_THR_Mean.csv'
        self.THR_Mean_pretrim = self.read_values(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_THR_THR_RMS.csv'
        self.THR_RMS_pretrim = self.read_values(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_BumpBonding_Offset_BadBump.csv'
        self.Bump_Mean = self.read_values(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_BumpBonding_Noise_BadBump.csv'
        self.Bump_RMS = self.read_values(cmd)

    # S curves
    def read_Scurves(self, cmd):
        csvfilename = get_recent(cmd)
        values = []
        with open(csvfilename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[0] == '':
                    continue
                pixedid = int(row[0])
                value = [float(i) for i in row]
                value.pop(0)
                values.append(value)
        return values

    def set_Scurves(self):

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_CAL_CAL.csv'
        self.CALS = self.read_Scurves(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PostTrim_THR_THR.csv'
        self.THRS = self.read_Scurves(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_CAL_CAL.csv'
        self.CALS_pretrim = self.read_Scurves(cmd)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_PreTrim_THR_THR.csv'
        self.THRS_pretrim = self.read_Scurves(cmd)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'*_BumpBonding_SCurve_BadBump.csv'
        self.BumpS = self.read_Scurves(cmd)
        
        return

# Needs added: IV
class MaPSA:
    """MaPSA class"""
    def __init__(self, name):
        self.name = name
        self.directory = '/uscms/home/jennetd/nobackup/mapsa-round2/Results_MPATesting/' + name + '/'
        self.mpa_chips = []

    def add_mpa(self, mpa):
        if(len(self.mpa_chips) >= 16):
            print("Error: MaPSA already has 16 associated MPAs")
            return

        self.mpa_chips += [mpa]
        print("Constructed " + self.name + " Chip " + str(len(self.mpa_chips)))

        return

def main():

    parser = argparse.ArgumentParser(description='MaPSA summary plots')
    parser.add_argument('-n','--name',nargs='+',help='name of output directory')
    parser.add_argument('-f','--files',nargs='+',help='list of text files containing names of MaPSAs to process')
    args = parser.parse_args()

    mapsas = []

    for f1 in args.files:
        print('Reading MaPSA names from ' + f1)
        with open(f1) as f:
            reader = csv.reader(f)
            mapsas = [row[0] for row in reader]
    print(mapsas)

    for m in mapsas:

        new_mapsa = MaPSA(m)
        print(new_mapsa.directory)

        for i in range(1,17):
            chip = MPA(m,i)
            new_mapsa.add_mpa(chip)

        print("Pickling MaPSA " + m)
        mapsafile = open('pickles/'+m+'.pkl', 'wb')
        cPickle.dump(new_mapsa, mapsafile, protocol=-1)
        mapsafile.close()

if __name__ == "__main__":
    main()
