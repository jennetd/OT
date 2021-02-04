import argparse
import sys, os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import mplhep as hep
#plt.style.use([hep.style.ROOT])

import cPickle

import MakeModulePlots

def get_recent(cmd):

    files = os.popen(cmd).read().split()

    if len(files) < 1:
        print("Error: no files specified")
        return "0"

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

class MPA:
    """MPA class"""
    def __init__(self, mapsa_name, chip_number):
        self.mapsa_name = mapsa_name
        self.index = chip_number
        self.directory = '/uscms/home/jennetd/nobackup/mapsa-round2/Results_MPATesting/' + mapsa_name + '/'

        cmd = 'ls '+ self.directory +'log*_Chip'+ str(self.index) +'_*.log'
        self.log_file = get_recent(cmd)

        self.set_currents()
        self.set_memerrs()
        self.set_regerrs()

        self.fill_pixels()

#        self.set_Scurves()

    def set_currents(self):

        if len(self.log_file) <= 1:
            self.I_ana = -1
            self.I_dig = -1
            self.I_pad = -1
            self.I_tot = -1
            return

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

    def set_regerrs(self):

        if len(self.log_file) <= 1:
            self.regerr_peri = -2
            self.regerr_row = -2
            self.regerr_pixel = -2
            return

        # Peri errors
        cmd = "grep 'Total MPA errors:' " + self.log_file
        x = os.popen(cmd).read()
        y = x.split()[-1]
        self.regerr_peri = float(y)

        # Row errors              
        cmd = "grep 'Total row errors:' " + self.log_file
        x = os.popen(cmd).read()
        y = x.split()[-1]
        self.regerr_row = float(y)

        # Pixel errors              
        cmd = "grep 'Total pixel errors:' " + self.log_file
        x = os.popen(cmd).read()
        y = x.split()[-1]
        self.regerr_pixel = float(y)

        return

    def set_memerrs(self):

        df = pd.DataFrame(index=['1.0V','1.2V'],columns=['error','stuck','I2C','missing'])

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+ str(self.index) + '_*_Mem105_Summary.csv' 
        csvfilename = get_recent(cmd)
        if csvfilename != "0":
            with open(csvfilename, 'r') as f:
                reader = csv.reader(f, delimiter=' ')
                for row in reader:
                    if row[0] == '':
                        continue
                    df['error']['1.0V'] = float(row[0])
                    df['stuck']['1.0V'] = float(row[0])
                    df['I2C']['1.0V'] = float(row[0])
                    df['missing']['1.0V'] = float(row[0])

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+ str(self.index) + '_*_Mem125_Summary.csv'
        csvfilename = get_recent(cmd)
        if csvfilename != "0":
            with open(csvfilename, 'r') as f:
                reader = csv.reader(f, delimiter=' ')
                for row in reader:
                    if row[0] == '':
                        continue
                    df['error']['1.2V'] = float(row[0])
                    df['stuck']['1.2V'] = float(row[0])
                    df['I2C']['1.2V'] = float(row[0])
                    df['missing']['1.2V'] = float(row[0])

        df = df.fillna(value=-2)

        self.memerrs = df
        return

    def fill_pixels(self):

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+ str(self.index) + '_*_pixelalive.csv'
        self.pixels = pd.read_csv(get_recent(cmd),index_col=0)
        self.pixels.columns = ['pa']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_CAL_CAL_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['CAL_Mean'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_CAL_CAL_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['CAL_RMS'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_THR_THR_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['THR_Mean'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_THR_THR_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['THR_RMS'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_CAL_CAL_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['CAL_Mean_pretrim'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_CAL_CAL_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['CAL_RMS_pretrim'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_THR_THR_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['THR_Mean_pretrim'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_THR_THR_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['THR_RMS_pretrim'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_BumpBonding_Offset_BadBump.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['Bump_Mean'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_BumpBonding_Noise_BadBump.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['Bump_RMS'] = tmp['value']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_mask_test.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'])
        self.pixels['mask'] = tmp['value']

        return

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

class MaPSA:
    """MaPSA class"""
    def __init__(self, name):

        # Set some properties
        self.name = name
        self.directory = '/uscms/home/jennetd/nobackup/mapsa-round2/Results_MPATesting/' + self.name + '/'
        self.mpa_chips = []
        self.set_IV()

        # Add MPAs
        for i in range(1,17):
            chip = MPA(self.name,i)
            self.add_mpa(chip)
        
        # Pickle it
        print("Pickling MaPSA " + self.name)
        mapsafile = open('pickles/'+self.name+'.pkl', 'wb')
        cPickle.dump(self, mapsafile, protocol=-1)
        mapsafile.close()

#        MakeModulePlots.PlotAllPlotsModulesAutomated(self.name,show_plot=False,save_plot=True)

    def add_mpa(self, mpa):
        if(len(self.mpa_chips) >= 16):
            print("Error: MaPSA already has 16 associated MPAs")
            return

        self.mpa_chips += [mpa]
        print("Constructed " + self.name + " Chip " + str(len(self.mpa_chips)))

        return

    def set_IV(self):
        csvfilename = self.directory+'IV.csv'
        Vpoints = []
        Ipoints = []
        with open(csvfilename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
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

        return 

def MaPSA_IV(mapsas, outdir):
    # print entries -- number of mapsas

    print("Processing " + str(len(mapsas)) + " MaPSAs for IV plot")

    fig, ax = plt.subplots()
    for m in mapsas:
        ax.plot(m.IV["V"],m.IV["I"])
#    ax.legend([m.name for m in mapsas])
    ax.set(xlabel="V [V]", ylabel="I [uA]",ylim=[-5,1])

    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/IV.png",bbox_inches='tight')
    plt.savefig(outdir+"/IV.pdf",bbox_inches='tight')
    plt.clf()

    return

def MPA_currents(mapsas, outdir):

    print("Processing " + str(len(mapsas)) + " MaPSAs for current plots")

    I_ana = []
    I_dig = []
    I_pad = []
    I_tot = []

    nchips = 0
    for m in mapsas:
        I_ana += [chip.I_ana for chip in m.mpa_chips]
        I_dig += [chip.I_dig for chip in m.mpa_chips]
        I_pad += [chip.I_pad for chip in m.mpa_chips]
        I_tot += [chip.I_tot for chip in m.mpa_chips]
        nchips += len(m.mpa_chips)

    fig, ax = plt.subplots(2,2)
#    fig1.suptitle(str(len(mapsas)) + " MaPSAs, " + str(nchips) + " MPAs")
    ax[0,0].hist(I_ana,bins=np.linspace(-10,100,20),histtype='step')
    ax[0,0].set(xlabel="I_ana [uA]",ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax[1,0].hist(I_dig,bins=np.linspace(-10,200,20),histtype='step')
    ax[1,0].set(xlabel="I_dig [uA]",ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax[0,1].hist(I_pad,bins=np.linspace(-10,50,20),histtype='step')
    ax[0,1].set(xlabel="I_pad [uA]",ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax[1,1].hist(I_tot,bins=np.linspace(-10,300,20),histtype='step')
    ax[1,1].set(xlabel="I_tot [uA]",ylabel="MPAs",yscale='log',ylim=[0.1,1000])

    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/Current.png",bbox_inches='tight')
    plt.savefig(outdir+"/Current.pdf",bbox_inches='tight')
    plt.clf()

    return

def MPA_registers(mapsas, outdir):
    print("Processing " + str(len(mapsas)) + " MaPSAs register plots")
    # print entries -- number of mapsas, number of mpas   

    regerr_peri = []
    regerr_row = []
    regerr_pixel = []

    nchips = 0
    for m in mapsas:
        regerr_peri  += [chip.regerr_peri for chip in m.mpa_chips]
        regerr_row   += [chip.regerr_row for chip in m.mpa_chips]
        regerr_pixel += [chip.regerr_pixel for chip in m.mpa_chips]
        nchips += len(m.mpa_chips)

    fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True)
    ax1.hist(regerr_peri,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='step')
    ax1.set(xlabel="Reg. Err. (Peri)",ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax2.hist(regerr_row,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='step')
    ax2.set(xlabel="Reg. Err. (Row)",yscale='log',ylim=[0.1,1000])
    ax3.hist(regerr_pixel,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='step')
    ax3.set(xlabel="Reg. Err. (Pix)",yscale='log',ylim=[0.1,1000])

    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/Register.png",bbox_inches='tight')
    plt.savefig(outdir+"/Register.pdf",bbox_inches='tight')
    plt.clf()

    return

def MPA_memory(mapsas, outdir):
    print("Processing " + str(len(mapsas)) + " MaPSAs for memory plots")

    error1 = []
    stuck1 = []
    i2c1 = []
    miss1 = []

    nchips = 0
    for m in mapsas:
        error1 += [chip.memerrs["error"]["1.0V"] for chip in m.mpa_chips]
        stuck1 += [chip.memerrs["stuck"]["1.0V"] for chip in m.mpa_chips]
        i2c1   += [chip.memerrs["I2C"]["1.0V"] for chip in m.mpa_chips]
        miss1  += [chip.memerrs["missing"]["1.0V"] for chip in m.mpa_chips]
        nchips += len(m.mpa_chips)

    fig, ax = plt.subplots(2,4, sharey=True)
#    fig3.suptitle(str(len(mapsas)) + " MaPSAs, " + str(nchips) + " MPAs")
    ax[0,0].hist(error1,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[0,0].set(xlabel="error (1.0V)",xlim=[-3,5],ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax[0,1].hist(stuck1,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[0,1].set(xlabel="stuck (1.0V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])
    ax[0,2].hist(i2c1,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[0,2].set(xlabel="I2C (1.0V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])
    ax[0,3].hist(miss1,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[0,3].set(xlabel="missing (1.0V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])

    error2 = []
    stuck2 = []
    i2c2 = []
    miss2 = []

    for m in mapsas:
        error2 += [chip.memerrs["error"]["1.2V"] for chip in m.mpa_chips]
        stuck2 += [chip.memerrs["stuck"]["1.2V"] for chip in m.mpa_chips]
        i2c2   += [chip.memerrs["I2C"]["1.2V"] for chip in m.mpa_chips]
        miss2  += [chip.memerrs["missing"]["1.2V"] for chip in m.mpa_chips]

    ax[1,0].hist(error2,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[1,0].set(xlabel="error (1.2V)",xlim=[-3,5],ylabel="MPAs",yscale='log',ylim=[0.1,1000])
    ax[1,1].hist(stuck2,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[1,1].set(xlabel="stuck (1.2V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])
    ax[1,2].hist(i2c2,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[1,2].set(xlabel="I2C (1.2V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])
    ax[1,3].hist(miss2,bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='step')
    ax[1,3].set(xlabel="missing (1.2V)",xlim=[-3,5],yscale='log',ylim=[0.1,1000])

    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/Memory.png",bbox_inches='tight')
    plt.savefig(outdir+"/Memory.pdf",bbox_inches='tight')
    plt.clf()

    return

def pixel_plots(mapsas, outdir):

    print("Processing " + str(len(mapsas)) + " MaPSAs for pixel plots")

    allpix = pd.DataFrame([])
    for m in mapsas:
        for chip in m.mpa_chips:
            allpix = allpix.append(chip.pixels)

    npix = len(allpix["pa"])

    fig1 = plt.gcf()
    plt.hist(allpix["pa"],bins=np.linspace(-20,220,12),histtype='step')
    plt.xlabel("alive")
    plt.ylabel("Pixels")
    plt.yscale('log')
    plt.ylim([0.1,1000000])
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " pixels")
#    plt.show()
    fig1.savefig(outdir+"/pa.png",bbox_inches='tight')
    fig1.savefig(outdir+"/pa.pdf",bbox_inches='tight')

    npix = len(allpix["pa"][allpix["pa"]>0])

    plt.clf()
    fig2 = plt.gcf()
    plt.hist(allpix["mask"][allpix["pa"]>0],bins=[-1.5,-0.5,0.5,1.5],histtype='step')
    plt.xlabel("mask")
    plt.ylabel("Pixels")
    plt.yscale('log')
    plt.ylim([0.1,1000000])
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig2.savefig(outdir+"/mask.png",bbox_inches='tight')
    fig2.savefig(outdir+"/mask.pdf",bbox_inches='tight')

    plt.clf()
    fig3 = plt.gcf()
    plt.hist(allpix["CAL_Mean"][allpix["pa"]>0],bins=np.linspace(0,50,20),histtype='step')
    plt.xlabel("CAL offset")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig3.savefig(outdir+"/CAL_Mean.png",bbox_inches='tight')
    fig3.savefig(outdir+"/CAL_Mean.pdf",bbox_inches='tight')

    plt.clf()
    fig4 = plt.gcf()
    plt.hist(allpix["CAL_RMS"][allpix["pa"]>0],bins=np.linspace(0,7,20),histtype='step')
    plt.xlabel("CAL noise")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig4.savefig(outdir+"/CAL_RMS.png",bbox_inches='tight')
    fig4.savefig(outdir+"/CAL_RMS.pdf",bbox_inches='tight')

    plt.clf()
    fig5 = plt.gcf()
    plt.hist(allpix["CAL_Mean_pretrim"][allpix["pa"]>0],bins=np.linspace(0,200,20),histtype='step')
    plt.xlabel("CAL offset (pre-trim)")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig5.savefig(outdir+"/CAL_Mean_pretrim.png",bbox_inches='tight')
    fig5.savefig(outdir+"/CAL_Mean_pretrim.pdf",bbox_inches='tight')

    plt.clf()
    fig6 = plt.gcf()
    plt.hist(allpix["CAL_RMS_pretrim"][allpix["pa"]>0],bins=np.linspace(0,7,20),histtype='step')
    plt.xlabel("CAL noise (pre-trim)")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig6.savefig(outdir+"/CAL_RMS_pretrim.png",bbox_inches='tight')
    fig6.savefig(outdir+"/CAL_RMS_pretrim.pdf",bbox_inches='tight')

    plt.clf()
    fig7 = plt.gcf()
    plt.hist(allpix["THR_Mean"][allpix["pa"]>0],bins=np.linspace(0,200,20),histtype='step')
    plt.xlabel("THR offset")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig7.savefig(outdir+"/THR_Mean.png",bbox_inches='tight')
    fig7.savefig(outdir+"/THR_Mean.pdf",bbox_inches='tight')

    plt.clf()
    fig8 = plt.gcf()
    plt.hist(allpix["THR_RMS"][allpix["pa"]>0],bins=np.linspace(0,7,20),histtype='step')
    plt.xlabel("THR noise")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig8.savefig(outdir+"/THR_RMS.png",bbox_inches='tight')
    fig8.savefig(outdir+"/THR_RMS.pdf",bbox_inches='tight')

    plt.clf()
    fig9 = plt.gcf()
    plt.hist(allpix["THR_Mean_pretrim"][allpix["pa"]>0],bins=np.linspace(0,200,20),histtype='step')
    plt.xlabel("THR offset (pre-trim)")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig9.savefig(outdir+"/THR_Mean_pretrim.png",bbox_inches='tight')
    fig9.savefig(outdir+"/THR_Mean_pretrim.pdf",bbox_inches='tight')

    plt.clf()
    fig10 = plt.gcf()
    plt.hist(allpix["THR_RMS_pretrim"][allpix["pa"]>0],bins=np.linspace(0,7,20),histtype='step')
    plt.xlabel("THR noise (pre-trim)")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig10.savefig(outdir+"/THR_RMS_pretrim.png",bbox_inches='tight')
    fig10.savefig(outdir+"/THR_RMS_pretrim.pdf",bbox_inches='tight')

    plt.clf()
    fig11 = plt.gcf()
    plt.hist(allpix["Bump_Mean"][allpix["pa"]>0],bins=np.linspace(0,5,20),histtype='step')
    plt.xlabel("Bump test offset")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig11.savefig(outdir+"/Bump_Mean.png",bbox_inches='tight')
    fig11.savefig(outdir+"/Bump_Mean.pdf",bbox_inches='tight')

    plt.clf()
    fig12 = plt.gcf()
    plt.hist(allpix["Bump_RMS"][allpix["pa"]>0],bins=np.linspace(0,7,20),histtype='step')
    plt.xlabel("Bump test noise")
    plt.ylabel("Pixels")
    plt.title(str(len(mapsas)) + " MaPSAs, " + str(npix) + " live pixels")
#    plt.show()
    fig12.savefig(outdir+"/Bump_RMS.png",bbox_inches='tight')
    fig12.savefig(outdir+"/Bump_RMS.pdf",bbox_inches='tight')

    plt.clf()
    return

def main():

    parser = argparse.ArgumentParser(description='MaPSA summary plots')
    parser.add_argument('-n','--name',nargs='+',help='name of output directory')
    parser.add_argument('-f','--files',nargs='+',help='list of text files containing names of MaPSAs to process')
    args = parser.parse_args()

    mapsa_names = []
    mapsas = []
    
    for f1 in args.files:
        print('Reading MaPSA names from ' + f1)
        with open(f1) as f:
            reader = csv.reader(f)
            mapsa_names = [row[0] for row in reader]
    print(mapsa_names)

    for m in mapsa_names:

        # Read if from file, if available
        fname = 'pickles/'+m+'.pkl'
        if os.path.isfile(fname):
            print("Loading MaPSA " + m)
            mapsa = cPickle.load(open(fname,'rb'))
        else: # Create it
            mapsa = MaPSA(m)

        mapsas += [mapsa]

    name = args.name[0]

    MaPSA_IV(mapsas, name)
    MPA_currents(mapsas, name)
    MPA_registers(mapsas, name)
    MPA_memory(mapsas, name)
    pixel_plots(mapsas, name)

if __name__ == "__main__":
    main()
