import argparse
import sys, os
import csv
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import cPickle
import MakeModulePlots

badchips = ["HPK34_1-1","HPK36_1-1","HPK36_1-11","HPK32_2-2","HPK32_2-3","HPK32_2-14","QP_no13-10","QP_no14-5","QP_no18p2-14","QP_no27p1-13","QP_no24p1c-1","QuikPak_PS-p-P1-8","QuikPak_PS-p-P2_4-12"]

plt.rc('font', size=22, weight='bold')
plt.rc('axes', titlesize=22)#, labelsize=18)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=22)
plt.rc('figure', titlesize=22)

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
#        self.set_regerrs()

        self.fill_pixels()
        self.set_Scurves()

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
        self.pixels = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        self.pixels.columns = ['pa']

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_CAL_CAL_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['CAL_RMS'] = tmp['value']
        self.pixels['CAL_RMS'][abs(self.pixels['CAL_RMS']-2.0)<0.000001] = -1
        self.pixels['CAL_RMS'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_CAL_CAL_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['CAL_Mean'] = tmp['value']
        self.pixels['CAL_Mean'][self.pixels['CAL_RMS']<0] = np.nan
        self.pixels['CAL_Mean'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_THR_THR_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['THR_RMS'] = tmp['value']
        self.pixels['THR_RMS'][abs(self.pixels['THR_RMS']-2.0)<0.000001] = -1
        self.pixels['THR_RMS'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PostTrim_THR_THR_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['THR_Mean'] = tmp['value']
        self.pixels['THR_Mean'][self.pixels['THR_RMS']<0] = np.nan
        self.pixels['THR_Mean'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_CAL_CAL_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['CAL_RMS_pretrim'] = tmp['value']
        self.pixels['CAL_RMS_pretrim'][abs(self.pixels['CAL_RMS_pretrim']-2.0)<0.00001] = -1
        self.pixels['CAL_RMS_pretrim'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_CAL_CAL_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['CAL_Mean_pretrim'] = tmp['value']
        self.pixels['CAL_Mean_pretrim'][self.pixels['CAL_RMS_pretrim']<0] = np.nan
        self.pixels['CAL_Mean_pretrim'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_THR_THR_RMS.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['THR_RMS_pretrim'] = tmp['value']
        self.pixels['THR_RMS_pretrim'][abs(self.pixels['THR_RMS_pretrim']-2.0)<0.000001] = -1
        self.pixels['THR_RMS_pretrim'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_PreTrim_THR_THR_Mean.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['THR_Mean_pretrim'] = tmp['value']
        self.pixels['THR_Mean_pretrim'][self.pixels['THR_RMS_pretrim']<0] = np.nan
        self.pixels['THR_Mean_pretrim'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_BumpBonding_Noise_BadBump.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['Bump_RMS'] = tmp['value']
        self.pixels['Bump_RMS'][abs(self.pixels['Bump_RMS']-2.0)<0.000001] = -1
        self.pixels['Bump_RMS'][self.pixels['pa']<100] = np.nan

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) + '_*_mask_test.csv'
        tmp = pd.read_csv(get_recent(cmd),names=['index','value'],header=0)
        self.pixels['mask'] = tmp['value']
        self.pixels['mask'][self.pixels['pa']<100] = np.nan

        return

    # S curves
    def set_Scurves(self):

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'_*_PostTrim_CAL_CAL.csv'
        self.CALS = pd.read_csv(get_recent(cmd),index_col=0,header=0)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'_*_PostTrim_THR_THR.csv'
        self.THRS = pd.read_csv(get_recent(cmd),index_col=0,header=0)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'_*_PreTrim_CAL_CAL.csv'
        self.CALS_pretrim = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'_*_PreTrim_THR_THR.csv'
        self.THRS_pretrim = pd.read_csv(get_recent(cmd),index_col=0,header=0)

        cmd = 'ls '+ self.directory + 'mpa_test_*_Chip'+str(self.index) +'_*_BumpBonding_SCurve_BadBump.csv'
        self.BumpS = pd.read_csv(get_recent(cmd),index_col=0,header=0)
        
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

    print("Processing " + str(len(mapsas)) + " MaPSAs for IV plot")

    fig, ax = plt.subplots(figsize=(12,9))
    for m in mapsas:
        if m.name in ['QuikPak_PS-p-P1_kapton','QuikPak_PS-p-P1_4_kapton','QuikPak_PS-p-P2','QuikPak_PS-p-P2_4_kapton']:
            ax.plot(m.IV["V"],m.IV["I"],color='red')
        elif m.name in ['QP_no20p1b','QP_no20p1c','QP_no20p2','QP_no20p2b','QP_no22p1','QP_no22p2','QP_no22p2b','QP_no24p1','QP_no24p1b','QP_no24p1c','QP_no24p2','QP_no17p2b','QP_no17p2c']:
            ax.plot(m.IV["V"],m.IV["I"],color='green')
        else:
            ax.plot(m.IV["V"],m.IV["I"],color='blue')
#    ax.legend([m.name for m in mapsas],frameon=False)
    ax.set_xlabel("V [V]",fontweight='bold')
    ax.set_ylabel("I [uA]",fontweight='bold')
    ax.set_ylim(-5,1)

    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/IV.png",bbox_inches='tight')
    plt.savefig(outdir+"/IV.pdf",bbox_inches='tight')
    plt.clf()

    return

def MPA_currents(mapsas, outdir, log=True):

    print("Processing " + str(len(mapsas)) + " MaPSAs for current plots")

    I_ana = [[],[]]
    I_dig = [[],[]]
    I_pad = [[],[]]
    I_tot = [[],[]]

    nchips_good = 0
    nchips_bad = 0

    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                I_ana[0] += [chip.I_ana]
                I_dig[0] += [chip.I_dig]
                I_pad[0] += [chip.I_pad]
                I_tot[0] += [chip.I_tot]
                nchips_bad += 1
            else:
                I_ana[1] += [chip.I_ana]
                I_dig[1] += [chip.I_dig]
                I_pad[1] += [chip.I_pad]
                I_tot[1] += [chip.I_tot]
                nchips_good += 1

    fig1, ax1 = plt.subplots(figsize=(12,9))
    plt.hist(np.array(I_ana),bins=np.linspace(-10,100,20),histtype='bar',stacked=True)
#    plt.hist(x,bins=np.linspace(-10,100,20),histtype='bar',stacked=True)
    ax1.set_xlabel("I_ana [uA]",fontweight='bold')
    ax1.set_ylabel("MPAs",fontweight='bold')
    if log:
        ax1.set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
 #   plt.show()

    if log:
        plt.savefig(outdir+"/I_ana_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_ana_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/I_ana.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_ana.pdf",bbox_inches='tight')

    plt.clf()

    fig2, ax2 = plt.subplots(figsize=(12,9))
    plt.hist(np.array(I_dig),bins=np.linspace(-10,200,20),histtype='bar',stacked=True)
    ax2.set_xlabel("I_dig [uA]",fontweight='bold')
    ax2.set_ylabel("MPAs",fontweight='bold')
    if log:
        ax2.set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
 #   plt.show()

    if log:
        plt.savefig(outdir+"/I_dig_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_dig_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/I_dig.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_dig.pdf",bbox_inches='tight')

    plt.clf()

    fig3, ax3 = plt.subplots(figsize=(12,9))
    plt.hist(np.array(I_pad),bins=np.linspace(-10,50,20),histtype='bar',stacked=True)
    ax3.set_xlabel("I_pad [uA]",fontweight='bold')
    ax3.set_ylabel("MPAs",fontweight='bold')
    if log:
        ax3.set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
 #   plt.show()

    if log:
        plt.savefig(outdir+"/I_pad_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_pad_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/I_pad.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_pad.pdf",bbox_inches='tight')
        
    plt.clf()

    fig4, ax4 = plt.subplots(figsize=(12,9))
    plt.hist(np.array(I_tot),bins=np.linspace(-10,300,20),histtype='bar',stacked=True)
    ax4.set_xlabel("I_tot [uA]",fontweight='bold')
    ax4.set_ylabel("MPAs",fontweight='bold')
    if log:
        ax4.set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
 #   plt.show()

    if log:
        plt.savefig(outdir+"/I_tot_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_tot_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/I_tot.png",bbox_inches='tight')
        plt.savefig(outdir+"/I_tot.pdf",bbox_inches='tight')

    plt.clf()

    return

def MPA_registers(mapsas, outdir, log=True):

    print("Processing " + str(len(mapsas)) + " MaPSAs register plots")

    regerr_peri = [[],[]]
    regerr_row = [[],[]]
    regerr_pixel = [[],[]]

    nchips_good = 0
    nchips_bad = 0
    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                regerr_peri[0]  += [chip.regerr_peri]
                regerr_row[0]   += [chip.regerr_row]
                regerr_pixel[0] += [chip.regerr_pixel]
                nchips_bad += 1
            else:
                regerr_peri[1]  += [chip.regerr_peri]
                regerr_row[1]   += [chip.regerr_row]
                regerr_pixel[1] += [chip.regerr_pixel]
                nchips_good += 1

    fig, (ax1,ax2,ax3) = plt.subplots(1,3,sharey=True)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.set_figheight(9)
    fig.set_figwidth(12)

    ax1.hist(np.array(regerr_peri),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='bar',stacked=True)
    ax1.set_xlabel("Reg. Err. (Peri)",fontweight='bold')
    ax1.set_ylabel("MPAs",fontweight='bold')

    ax2.hist(np.array(regerr_row),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='bar',stacked=True)
    ax2.set_xlabel("Reg. Err. (Row)",fontweight='bold')

    ax3.hist(np.array(regerr_pixel),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5],histtype='bar',stacked=True)
    ax3.set_xlabel("Reg. Err. (Pix)",fontweight='bold')

    if log:
        ax1.set(yscale='log',ylim=[0.1,1000])
        ax2.set(yscale='log',ylim=[0.1,1000])
        ax3.set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        plt.savefig(outdir+"/Register_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/Register_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/Register.png",bbox_inches='tight')
        plt.savefig(outdir+"/Register.pdf",bbox_inches='tight')

    plt.clf()

    return

def MPA_memory(mapsas, outdir, log=True):
    print("Processing " + str(len(mapsas)) + " MaPSAs for memory plots")

    error1 = [[],[]]
    stuck1 = [[],[]]
    i2c1 = [[],[]]
    miss1 = [[],[]]

    nchips_good = 0
    nchips_bad = 0
    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                error1[0] += [chip.memerrs["error"]["1.0V"]]
                stuck1[0] += [chip.memerrs["stuck"]["1.0V"]]
                i2c1[0]   += [chip.memerrs["I2C"]["1.0V"]]
                miss1[0]  += [chip.memerrs["missing"]["1.0V"]]
                nchips_bad += 1
            else:
                error1[1] += [chip.memerrs["error"]["1.0V"]]
                stuck1[1] += [chip.memerrs["stuck"]["1.0V"]]
                i2c1[1]   += [chip.memerrs["I2C"]["1.0V"]]
                miss1[1]  += [chip.memerrs["missing"]["1.0V"]]
                nchips_good += 1

    fig, ax = plt.subplots(2,4, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.set_figheight(9)
    fig.set_figwidth(16)
    
    ax[0,0].hist(np.array(error1),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)
    ax[0,0].set_ylabel("MPAs (at 1.0 V)",fontweight='bold')

    ax[0,1].hist(np.array(stuck1),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)

    ax[0,2].hist(np.array(i2c1),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)

    ax[0,3].hist(np.array(miss1),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)

    error2 = [[],[]]
    stuck2 = [[],[]]
    i2c2 = [[],[]]
    miss2 = [[],[]]

    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                error2[0] += [chip.memerrs["error"]["1.2V"]]
                stuck2[0] += [chip.memerrs["stuck"]["1.2V"]]
                i2c2[0]   += [chip.memerrs["I2C"]["1.2V"]]
                miss2[0]  += [chip.memerrs["missing"]["1.2V"]]
            else:
                error2[1] += [chip.memerrs["error"]["1.2V"]]
                stuck2[1] += [chip.memerrs["stuck"]["1.2V"]]
                i2c2[1]   += [chip.memerrs["I2C"]["1.2V"]]
                miss2[1]  += [chip.memerrs["missing"]["1.2V"]]

    ax[1,0].hist(np.array(error2),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)
    ax[1,0].set_xlabel("error",fontweight='bold')
    ax[1,0].set_ylabel("MPAs (at 1.2 V)",fontweight='bold')

    ax[1,1].hist(np.array(stuck2),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)
    ax[1,1].set_xlabel("stuck",fontweight='bold')

    ax[1,2].hist(np.array(i2c2),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)
    ax[1,2].set_xlabel("I2C",fontweight='bold')

    ax[1,3].hist(np.array(miss2),bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5],histtype='bar',stacked=True)
    ax[1,3].set_xlabel("missing",fontweight='bold')

    for i in range(0,2):
        for j in range(0,4):
            ax[i,j].set(xlim=[-3,5])
            if log:
                ax[i,j].set(yscale='log',ylim=[0.1,1000])

    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        plt.savefig(outdir+"/Memory_log.png",bbox_inches='tight')
        plt.savefig(outdir+"/Memory_log.pdf",bbox_inches='tight')
    else:
        plt.savefig(outdir+"/Memory.png",bbox_inches='tight')
        plt.savefig(outdir+"/Memory.pdf",bbox_inches='tight')

    plt.clf()

    return

def pixel_plots(mapsas, outdir, log=True):

    print("Processing " + str(len(mapsas)) + " MaPSAs for pixel plots")

    allpix = pd.DataFrame([])
    allpix_bad = pd.DataFrame([])

    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                allpix_bad = allpix_bad.append(chip.pixels)
            else:
                allpix = allpix.append(chip.pixels)

    if len(allpix_bad) == 0:
        allpix_bad = pd.DataFrame(columns=allpix.columns)

    npix = len(allpix["pa"])
    print(npix)

    logmax = npix*50

    print("pa")
    fig1 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["pa"],allpix["pa"]),bins=np.linspace(-20,220,12),histtype='bar',stacked=True)
    plt.xlabel("alive",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig1.savefig(outdir+"/pa_log.png",bbox_inches='tight')
        fig1.savefig(outdir+"/pa_log.pdf",bbox_inches='tight')
    else:
        fig1.savefig(outdir+"/pa.png",bbox_inches='tight')
        fig1.savefig(outdir+"/pa.pdf",bbox_inches='tight')

    print("mask")
    plt.clf()
    fig2 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["mask"],allpix["mask"]),bins=[-1.5,-0.5,0.5,1.5],histtype='bar',stacked=True)
    plt.xlabel("mask",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig2.savefig(outdir+"/mask_log.png",bbox_inches='tight')
        fig2.savefig(outdir+"/mask_log.pdf",bbox_inches='tight')
    else:
        fig2.savefig(outdir+"/mask.png",bbox_inches='tight')
        fig2.savefig(outdir+"/mask.pdf",bbox_inches='tight')

    print("CAL_Mean")
    plt.clf()
    fig3 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["CAL_Mean"],allpix["CAL_Mean"]),bins=np.linspace(-10,50,30),histtype='bar',stacked=True)
    plt.xlabel("CAL mean",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig3.savefig(outdir+"/CAL_Mean_log.png",bbox_inches='tight')
        fig3.savefig(outdir+"/CAL_Mean_log.pdf",bbox_inches='tight')
    else:
        fig3.savefig(outdir+"/CAL_Mean.png",bbox_inches='tight')
        fig3.savefig(outdir+"/CAL_Mean.pdf",bbox_inches='tight')

    print("CAL_RMS")
    plt.clf()
    fig4 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["CAL_RMS"],allpix["CAL_RMS"]),bins=np.linspace(-2,7,30),histtype='bar',stacked=True)
    plt.xlabel("CAL noise",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig4.savefig(outdir+"/CAL_RMS_log.png",bbox_inches='tight')
        fig4.savefig(outdir+"/CAL_RMS_log.pdf",bbox_inches='tight')
    else:
        fig4.savefig(outdir+"/CAL_RMS.png",bbox_inches='tight')
        fig4.savefig(outdir+"/CAL_RMS.pdf",bbox_inches='tight')

    print("CAL_Mean_pretrim")
    plt.clf()
    fig5 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["CAL_Mean_pretrim"],allpix["CAL_Mean_pretrim"]),bins=np.linspace(-24,256,30),histtype='bar',stacked=True)
    plt.xlabel("CAL mean (pre-trim)",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()
 
    if log:
        fig5.savefig(outdir+"/CAL_Mean_pretrim_log.png",bbox_inches='tight')
        fig5.savefig(outdir+"/CAL_Mean_pretrim_log.pdf",bbox_inches='tight')
    else:
        fig5.savefig(outdir+"/CAL_Mean_pretrim.png",bbox_inches='tight')
        fig5.savefig(outdir+"/CAL_Mean_pretrim.pdf",bbox_inches='tight')

    print("CAL_RMS_pretrim")
    plt.clf()
    fig6 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["CAL_RMS_pretrim"],allpix["CAL_RMS_pretrim"]),bins=np.linspace(-2,7,30),histtype='bar',stacked=True)
    plt.xlabel("CAL noise (pre-trim)",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()
    
    if log:
        fig6.savefig(outdir+"/CAL_RMS_pretrim_log.png",bbox_inches='tight')
        fig6.savefig(outdir+"/CAL_RMS_pretrim_log.pdf",bbox_inches='tight')
    else:
        fig6.savefig(outdir+"/CAL_RMS_pretrim.png",bbox_inches='tight')
        fig6.savefig(outdir+"/CAL_RMS_pretrim.pdf",bbox_inches='tight')

    print("THR_Mean")
    plt.clf()
    fig7 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["THR_Mean"],allpix["THR_Mean"]),bins=np.linspace(-24,256,30),histtype='bar',stacked=True)
    plt.xlabel("THR mean",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()
    if log:
        fig7.savefig(outdir+"/THR_Mean_log.png",bbox_inches='tight')
        fig7.savefig(outdir+"/THR_Mean_log.pdf",bbox_inches='tight')
    else:
        fig7.savefig(outdir+"/THR_Mean.png",bbox_inches='tight')
        fig7.savefig(outdir+"/THR_Mean.pdf",bbox_inches='tight')

    print("THR_RMS")
    plt.clf()
    fig8 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["THR_RMS"],allpix["THR_RMS"]),bins=np.linspace(-2,7,30),histtype='bar',stacked=True)
    plt.xlabel("THR noise",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig8.savefig(outdir+"/THR_RMS_log.png",bbox_inches='tight')
        fig8.savefig(outdir+"/THR_RMS_log.pdf",bbox_inches='tight')
    else:
        fig8.savefig(outdir+"/THR_RMS.png",bbox_inches='tight')
        fig8.savefig(outdir+"/THR_RMS.pdf",bbox_inches='tight')

    print("THR_Mean_pretrim")
    plt.clf()
    fig9 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["THR_Mean_pretrim"],allpix["THR_Mean_pretrim"]),bins=np.linspace(-24,256,30),histtype='bar',stacked=True)
    plt.xlabel("THR mean (pre-trim)",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig9.savefig(outdir+"/THR_Mean_pretrim_log.png",bbox_inches='tight')
        fig9.savefig(outdir+"/THR_Mean_pretrim_log.pdf",bbox_inches='tight')
    else:
        fig9.savefig(outdir+"/THR_Mean_pretrim.png",bbox_inches='tight')
        fig9.savefig(outdir+"/THR_Mean_pretrim.pdf",bbox_inches='tight')

    print("THR_RMS_pretrim")
    plt.clf()
    fig10 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["THR_RMS_pretrim"],allpix["THR_RMS_pretrim"]),bins=np.linspace(-2,7,30),histtype='bar',stacked=True)
    plt.xlabel("THR noise (pre-trim)",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig10.savefig(outdir+"/THR_RMS_pretrim_log.png",bbox_inches='tight')
        fig10.savefig(outdir+"/THR_RMS_pretrim_log.pdf",bbox_inches='tight')
    else:
        fig10.savefig(outdir+"/THR_RMS_pretrim.png",bbox_inches='tight')
        fig10.savefig(outdir+"/THR_RMS_pretrim.pdf",bbox_inches='tight')

    print("Bump_RMS")
    plt.clf()
    fig12 = plt.figure(figsize=(12,9))
    plt.hist(np.array(allpix_bad["Bump_RMS"],allpix["Bump_RMS"]),bins=np.linspace(-2,7,30),histtype='bar',stacked=True)
    plt.xlabel("Bump test noise",fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    if log:
        plt.yscale('log')
        plt.ylim([0.1,logmax])
    plt.title(str(len(mapsas)) + " MaPSAs",fontweight='bold')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.tight_layout()
#    plt.show()

    if log:
        fig12.savefig(outdir+"/Bump_RMS_log.png",bbox_inches='tight')
        fig12.savefig(outdir+"/Bump_RMS_log.pdf",bbox_inches='tight')
    else:
        fig12.savefig(outdir+"/Bump_RMS.png",bbox_inches='tight')
        fig12.savefig(outdir+"/Bump_RMS.pdf",bbox_inches='tight')

    plt.clf()
    return

def pa_2d(mapsas,outdir):

    print("Processing " + str(len(mapsas)) + " MaPSAs for 2D pixel alive map")

    allpix = pd.DataFrame([0]*1888,columns=["w"])
    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                print("Skipping " + chip.mapsa_name + "-"+str(chip.index))
            else:
                allpix["w"][chip.pixels["pa"]<100] += 1

    x, y = np.meshgrid(np.linspace(0,117,118),np.linspace(0,15,16))

    xflat = x.reshape(-1)
    yflat = y.reshape(-1)

    fig, ax = plt.subplots(figsize=(6,10))
    plt.hist2d(xflat,yflat,bins=[118,16],weights=allpix["w"])

    cbar = plt.colorbar()
    cbar.set_label("dead/inefficient pixels",fontweight='bold')

    ax.set_xlabel("column",fontweight='bold')
    ax.set_ylabel("row",fontweight='bold')
 
    plt.tight_layout()
#    plt.show()

    plt.savefig(outdir+"/pa_2dmap.png",bbox_inches='tight')
    plt.savefig(outdir+"/pa_2dmap.pdf",bbox_inches='tight')

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

        # Read MaPSA object from file, if available
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
#    MPA_registers(mapsas, name)
    MPA_memory(mapsas, name)
    pixel_plots(mapsas, name)
    pa_2d(mapsas,name)

    MPA_currents(mapsas, name, 0)
#    MPA_registers(mapsas, name, 0)
    MPA_memory(mapsas, name, 0)
    pixel_plots(mapsas, name, 0)

if __name__ == "__main__":
    main()
