from CollectMaPSAs import *
import ROOT
import cPickle
import matplotlib.pyplot as plt

plt.rc('font', size=18, weight='bold', family='sans-serif')
plt.rc('axes', titlesize=18)#, labelsize=18)
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)
plt.rc('legend', fontsize=18)
plt.rc('figure', titlesize=18)

def stacked_hist(arr1,arr2,bins,xtitle,ytitle,logmax=0):

    fig1, ax1 = plt.subplots(figsize=(8,6))

    plt.hist(np.array([arr1,arr2]),bins=bins,histtype='bar',stacked=True,color=mycolors,edgecolor='black')
    plt.legend(["Bad MPA","Good MPA"],frameon=False)
    plt.hist(np.array([arr1,arr2]),bins=bins,histtype='bar',stacked=True,color=mycolors)
    if len(arr1) > 0:
        plt.hist(np.concatenate((arr1,arr2)),bins=bins,histtype='step',color='black')
        plt.hist(np.array(arr1),bins=bins,histtype='step',color='black')
    else:
        plt.hist(np.array(arr2),bins=bins,histtype='step',color='black')
    ax1.set_xlabel(xtitle,fontweight='bold')
    ax1.set_ylabel(ytitle,fontweight='bold')
    plt.title(str(len(mapsas)) + " " + vendor +" MaPSAs",fontweight='bold')

    if logmax > 0:
        ax1.set(yscale='log',ylim=[0.1,logmax])

    return fig1

# Draw IV plot
def IV_plot():
    print("Processing " + str(len(mapsas)) + " MaPSAs for IV plot")

    fig, ax = plt.subplots(figsize=(8,6))
    for m in mapsas:
        if m.IV["I"][60] > 10:
            ax.plot(abs(m.IV["V"]),abs(m.IV["I"]),color='red')
        else:
            ax.plot(abs(m.IV["V"]),abs(m.IV["I"]),color='royalblue')

    ax.set_xlabel("$V$ [V]",fontweight='bold')
    ax.set_ylabel("$I$ [mA]",fontweight='bold')
    ax.set_ylim(-1,10)
    plt.title(str(len(mapsas)) + " " + vendor +" MaPSAs",fontweight='bold')

    plt.tight_layout()

    fig.savefig(outdir+"/IV.png",bbox_inches='tight')
    fig.savefig(outdir+"/IV.pdf",bbox_inches='tight')

    plt.close()
    plt.clf()

# Plot MPA memory test results
def memory_plot():
    print("Processing " + str(len(mapsas)) + " MaPSAs for memory plots")

    Mem1 = {}
    Mem1['error'] = [[],[]]
    Mem1['stuck'] = [[],[]]
    Mem1['i2c'] = [[],[]]
    Mem1['miss'] = [[],[]]
    
    Mem2 = {}
    Mem2['error'] = [[],[]]
    Mem2['stuck'] = [[],[]]
    Mem2['i2c'] = [[],[]]
    Mem2['miss'] = [[],[]]

    nchips_good = 0
    nchips_bad = 0
    
    minval = -2.5
    maxval = 4.5

    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                Mem1['error'][0] += [np.clip(chip.memerrs["error"]["1.0V"],minval,maxval)]
                Mem1['stuck'][0] += [np.clip(chip.memerrs["stuck"]["1.0V"],minval,maxval)]
                Mem1['i2c'][0]   += [np.clip(chip.memerrs["I2C"]["1.0V"],minval,maxval)]
                Mem1['miss'][0]  += [np.clip(chip.memerrs["missing"]["1.0V"],minval,maxval)]
                
                Mem2['error'][0] += [np.clip(chip.memerrs["error"]["1.2V"],minval,maxval)]
                Mem2['stuck'][0] += [np.clip(chip.memerrs["stuck"]["1.2V"],minval,maxval)]
                Mem2['i2c'][0]   += [np.clip(chip.memerrs["I2C"]["1.2V"],minval,maxval)]
                Mem2['miss'][0]  += [np.clip(chip.memerrs["missing"]["1.2V"],minval,maxval)]
                
                nchips_bad += 1
            else:
                Mem1['error'][1] += [np.clip(chip.memerrs["error"]["1.0V"],minval,maxval)]
                Mem1['stuck'][1] += [np.clip(chip.memerrs["stuck"]["1.0V"],minval,maxval)]
                Mem1['i2c'][1]   += [np.clip(chip.memerrs["I2C"]["1.0V"],minval,maxval)]
                Mem1['miss'][1]  += [np.clip(chip.memerrs["missing"]["1.0V"],minval,maxval)]
                
                Mem2['error'][1] += [np.clip(chip.memerrs["error"]["1.2V"],minval,maxval)]
                Mem2['stuck'][1] += [np.clip(chip.memerrs["stuck"]["1.2V"],minval,maxval)]
                Mem2['i2c'][1]   += [np.clip(chip.memerrs["I2C"]["1.2V"],minval,maxval)]
                Mem2['miss'][1]  += [np.clip(chip.memerrs["missing"]["1.2V"],minval,maxval)]
            
                nchips_good += 1

    bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5]

    fig, ax = plt.subplots(2,4, sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.set_figheight(9)
    fig.set_figwidth(16)
    
    ax[0,0].hist(np.array(Mem1['error']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[0,0].hist(np.array(Mem1['error'][0]+Mem1['error'][1]),bins=bins,histtype='step',color='black')
    ax[0,0].hist(np.array(Mem1['error'][0]),bins=bins,histtype='step',color='black')
    ax[0,0].set_ylabel("MPAs (at 1.0 V)",fontweight='bold')
    
    ax[0,1].hist(np.array(Mem1['stuck']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[0,1].hist(np.array(Mem1['stuck'][0]+Mem1['stuck'][1]),bins=bins,histtype='step',color='black')
    ax[0,1].hist(np.array(Mem1['stuck'][0]),bins=bins,histtype='step',color='black')
    
    ax[0,2].hist(np.array(Mem1['i2c']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[0,2].hist(np.array(Mem1['i2c'][0]+Mem1['i2c'][1]),bins=bins,histtype='step',color='black')
    ax[0,2].hist(np.array(Mem1['i2c'][0]),bins=bins,histtype='step',color='black')
    
    ax[0,3].hist(np.array(Mem1['miss']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[0,3].hist(np.array(Mem1['miss'][0]+Mem1['miss'][1]),bins=bins,histtype='step',color='black')
    ax[0,3].hist(np.array(Mem1['miss'][0]),bins=bins,histtype='step',color='black')
    
    ax[1,0].hist(np.array(Mem2['error']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[1,0].hist(np.array(Mem2['error'][0]+Mem2['error'][1]),bins=bins,histtype='step',color='black')
    ax[1,0].hist(np.array(Mem2['error'][0]),bins=bins,histtype='step',color='black')
    ax[1,0].set_ylabel("MPAs (at 1.0 V)",fontweight='bold')
    
    ax[1,1].hist(np.array(Mem2['stuck']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[1,1].hist(np.array(Mem2['stuck'][0]+Mem2['stuck'][1]),bins=bins,histtype='step',color='black')
    ax[1,1].hist(np.array(Mem2['stuck'][0]),bins=bins,histtype='step',color='black')
    
    ax[1,2].hist(np.array(Mem2['i2c']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[1,2].hist(np.array(Mem2['i2c'][0]+Mem2['i2c'][1]),bins=bins,histtype='step',color='black')
    ax[1,2].hist(np.array(Mem2['i2c'][0]),bins=bins,histtype='step',color='black')
    
    ax[1,3].hist(np.array(Mem2['error']),bins=bins,histtype='bar',stacked=True,color=mycolors,edgecolor='black')
    plt.legend(["Bad MPA","Good MPA"],frameon=False,bbox_to_anchor=(1.05, 1))
    ax[1,3].hist(np.array(Mem2['miss']),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax[1,3].hist(np.array(Mem2['miss'][0]+Mem2['miss'][1]),bins=bins,histtype='step',color='black')
    ax[1,3].hist(np.array(Mem2['miss'][0]),bins=bins,histtype='step',color='black')
    
    ax[1,0].set_xlabel("error",fontweight='bold')
    ax[1,0].set_ylabel("MPAs (at 1.2 V)",fontweight='bold')
    ax[1,1].set_xlabel("stuck",fontweight='bold')
    ax[1,2].set_xlabel("I2C",fontweight='bold')
    ax[1,3].set_xlabel("missing",fontweight='bold')
    
    for i in range(0,2):
        for j in range(0,4):
            ax[i,j].set(xlim=[-3,5])
            
    plt.tight_layout()

    # Linear scale
    fig.savefig(outdir+"/Memory.png",bbox_inches='tight')
    fig.savefig(outdir+"/Memory.pdf",bbox_inches='tight')

    # Log scale
    for i in range(0,2):
        for j in range(0,4):
            ax[i,j].set(yscale='log',ylim=[0.1,1000])
        
    fig.savefig(outdir+"/Memory_log.png",bbox_inches='tight')
    fig.savefig(outdir+"/Memory_log.pdf",bbox_inches='tight')
    
    plt.close()
    plt.clf()

# Plot MPA current draws 
def current_plot():
    print("Processing " + str(len(mapsas)) + " MaPSAs for current plots")

    I = {}
    I['ana'] = [[],[]]
    I['dig'] = [[],[]]
    I['pad'] = [[],[]]
    I['tot'] = [[],[]]

    Inames = {}
    Inames['ana'] = "$I_{analog}$ [mA]"
    Inames['dig'] = "$I_{digital}$ [mA]"
    Inames['pad'] = "$I_{pad}$ [mA]"
    Inames['tot'] = "$I_{total}$ [mA]"

    nchips_good = 0
    nchips_bad = 0

    minval = 0
    maxval = 1000

    for m in mapsas:
        for chip in m.mpa_chips:

            if(chip.I_tot > 200):
                print(m.name,chip.index)

            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                I['ana'][0] += [np.clip(chip.I_ana,minval,maxval)]
                I['dig'][0] += [np.clip(chip.I_dig,minval,maxval)]
                I['pad'][0] += [np.clip(chip.I_pad,minval,maxval)]
                I['tot'][0] += [chip.I_tot]
                nchips_bad += 1
            else:
                I['ana'][1] += [np.clip(chip.I_ana,minval,maxval)]
                I['dig'][1] += [np.clip(chip.I_dig,minval,maxval)]
                I['pad'][1] += [np.clip(chip.I_pad,minval,maxval)]
                I['tot'][1] += [np.clip(chip.I_tot,minval,maxval)]
                nchips_good += 1

    for c in I.keys():

        bins = np.linspace(0,300,20)

        # Linear scale
        fig1 = stacked_hist(I[c][0],I[c][1],bins,Inames[c],"MPAs",logmax=0)
        fig1.savefig(outdir+"/I_"+c+".png",bbox_inches='tight')
        fig1.savefig(outdir+"/I_"+c+".pdf",bbox_inches='tight')
        plt.close()
        plt.clf()

        # Log scale
        fig2 = stacked_hist(I[c][0],I[c][1],bins,Inames[c],"MPAs",logmax=1000)
        fig2.savefig(outdir+"/I_"+c+"_log.png",bbox_inches='tight')
        fig2.savefig(outdir+"/I_"+c+"_log.pdf",bbox_inches='tight')
        plt.close()
        plt.clf()

# Draw plots of register errors
def register_plot():
    print("Processing " + str(len(mapsas)) + " MaPSAs register plots")
    
    regerr = {}
    regerr["peri"] = [[],[]]
    regerr["row"] = [[],[]]
    regerr["pixel"] = [[],[]]
    
    nchips_good = 0
    nchips_bad = 0
    
    minval=-2.5
    maxval=2.5
    
    for m in mapsas:
        for chip in m.mpa_chips:
            if chip.mapsa_name+"-"+str(chip.index) in badchips:
                regerr["peri"][0]  += [np.clip(chip.regerr_peri,minval,maxval)]
                regerr["row"][0]   += [np.clip(chip.regerr_row,minval,maxval)]
                regerr["pixel"][0] += [np.clip(chip.regerr_pixel,minval,maxval)]
                nchips_bad += 1
            else:
                regerr["peri"][1]  += [np.clip(chip.regerr_peri,minval,maxval)]
                regerr["row"][1]   += [np.clip(chip.regerr_row,minval,maxval)]
                regerr["pixel"][1] += [np.clip(chip.regerr_pixel,minval,maxval)]
                nchips_good += 1
                
    fig, (ax1,ax2,ax3) = plt.subplots(1,3,sharey=True)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.set_figheight(9)
    fig.set_figwidth(15)

    bins=[-2.5,-1.5,-0.5,0.5,1.5,2.5]

    ax1.hist(np.array(regerr["peri"]),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax1.hist(np.array(regerr["peri"][0]+regerr["peri"][1]),bins=bins,histtype='step',color='black')
    ax1.hist(np.array(regerr["peri"][0]),bins=bins,histtype='step',color='black')
    ax1.set_xlabel("Reg. Err. (Peri)",fontweight='bold')
    ax1.set_ylabel("MPAs",fontweight='bold')
    
    ax2.hist(np.array(regerr["row"]),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax2.hist(np.array(regerr["row"][0]+regerr["peri"][1]),bins=bins,histtype='step',color='black')
    ax2.hist(np.array(regerr["row"][0]),bins=bins,histtype='step',color='black')
    ax2.set_xlabel("Reg. Err. (Row)",fontweight='bold')

    ax3.hist(np.array(regerr["pixel"]),bins=bins,histtype='bar',stacked=True,color=mycolors,edgecolor='black')
    plt.legend(["Bad MPA","Good MPA"],frameon=False,bbox_to_anchor=(1.05, 1))
    ax3.hist(np.array(regerr["pixel"]),bins=bins,histtype='bar',stacked=True,color=mycolors)
    ax3.hist(np.array(regerr["pixel"][0]+regerr["peri"][1]),bins=bins,histtype='step',color='black')
    ax3.hist(np.array(regerr["pixel"][0]),bins=bins,histtype='step',color='black')
    ax3.set_xlabel("Reg. Err. (Pix)",fontweight='bold')

    plt.tight_layout()

    # Linear scale
    fig.savefig(outdir+"/Register.png",bbox_inches='tight')
    fig.savefig(outdir+"/Register.pdf",bbox_inches='tight')

    # Log scale
    ax1.set(yscale='log',ylim=[0.1,1000])
    ax2.set(yscale='log',ylim=[0.1,1000])
    ax3.set(yscale='log',ylim=[0.1,1000])

    fig.savefig(outdir+"/Register_log.png",bbox_inches='tight')
    fig.savefig(outdir+"/Register_log.pdf",bbox_inches='tight')
    plt.close()
    plt.clf()

def pixel_overlay(var1, var2, xtitle, names, bins):

    arr1 = np.clip(allpix[var1],bins[0],bins[-1])
    arr2 = np.clip(allpix[var2],bins[0],bins[-1])

    mu1 = np.mean(arr1)
    sigma1 = np.std(arr1)
    mu2 = np.mean(arr2)
    sigma2 = np.std(arr2)
    
    fig1 = plt.figure(figsize=(8,6))
    plt.hist(arr1,bins=bins,histtype='step',color='black')
    plt.hist(arr2,bins=bins,histtype='step',color='red')
    plt.xlabel(xtitle,fontweight='bold')
    plt.ylabel("Pixels",fontweight='bold')
    plt.title(str(len(mapsas)) + " " + vendor +" MaPSAs",fontweight='bold')
    plt.legend(names,frameon=False)
    
    plt.figtext(.6,.7,"$\mu$="+str(round(mu1,2))+", $\sigma$="+str(round(sigma1,2)),size=18)
    plt.figtext(.6,.62,"$\mu$="+str(round(mu2,2))+", $\sigma$="+str(round(sigma2,2)),color='red',size=18)

    plt.tight_layout()

    fig1.savefig(outdir+"/overlay_"+var1+"_"+var2+".png",bbox_inches='tight')
    fig1.savefig(outdir+"/overlay_"+var1+"_"+var2+".pdf",bbox_inches='tight')

    plt.yscale('log')
    plt.ylim([0.1,50*npix])

    fig1.savefig(outdir+"/overlay_"+var1+"_"+var2+"_log.png",bbox_inches='tight')
    fig1.savefig(outdir+"/overlay_"+var1+"_"+var2+"_log.pdf",bbox_inches='tight')
    
def pixel_plot(var,xtitle,bins):
    print("Processing " + str(len(mapsas)) + " MaPSAs for pixel plots of "+var)

    arr1 = np.clip(allpix_bad[var],bins[0],bins[-1])
    arr2 = np.clip(allpix[var],bins[0],bins[-1])

    # Linear scale                                                                                                        
    fig1 = stacked_hist(arr1,arr2,bins,xtitle,"Pixels",logmax=0)
    fig1.savefig(outdir+"/"+var+".png",bbox_inches='tight')
    fig1.savefig(outdir+"/"+var+".pdf",bbox_inches='tight')
    plt.close()
    plt.clf()

    # Log scale                                                                   
    fig2 = stacked_hist(arr1,arr2,bins,xtitle,"Pixels",logmax = 50*npix)
    fig2.savefig(outdir+"/"+var+"_log.png",bbox_inches='tight')
    fig2.savefig(outdir+"/"+var+"_log.pdf",bbox_inches='tight')
    plt.close()
    plt.clf()

def pixel_map(var,ztitle):
    print("Processing " + str(len(mapsas)) + " MaPSAs for 2D "+var+" map")

    pixels = pd.DataFrame([0]*1888,columns=["all"])
    pixels["good"] = pixels["all"]

    for m in mapsas:
        for chip in m.mpa_chips:
            if "RMS" in var:
                pixels["all"] += chip.pixels[var]/(np.sqrt(2)*16.*len(mapsas))

            if var == "pa":
                pixels["all"][chip.pixels[var]<100] += 1
                pixels["all"][chip.pixels[var]>200] += 1
                if np.any(chip.pixels[var]<100):
                    print("inefficient",m.name)
                if np.any(chip.pixels[var]>200):
                    print("noisy",m.name)

            if var == "mask":
                pixels["all"][chip.pixels[var]>0] += 1
                if np.any(chip.pixels[var]>0):
                    print("unmaskable",m.name)
#                pixels["all"][abs(chip.pixels[var])<0] = 0

            if chip.mapsa_name+"-"+str(chip.index) not in badchips:
                if var == "pa":
                    pixels["good"][chip.pixels[var]<100] += 1
                    pixels["good"][chip.pixels[var]>200] += 1
                if var == "mask":
                    pixels["good"][chip.pixels[var]>0] += 1
#                    pixels["good"][abs(chip.pixels[var])<0] = 0

    x, y = np.meshgrid(np.linspace(0,117,118),np.linspace(0,15,16))

    xflat = x.reshape(-1)
    yflat = y.reshape(-1)

    fig, ax = plt.subplots(figsize=(8,10))
    arr1 = pixels["good"]
    plt.hist2d(xflat,yflat,bins=[118,16],weights=arr1)

    cbar = plt.colorbar()
    cbar.set_label(ztitle,fontweight='bold')
    ax.set_xlabel("column",fontweight='bold')
    ax.set_ylabel("row",fontweight='bold')
 
    plt.tight_layout()
    fig.savefig(outdir+"/"+var+"_2dmap_good.png",bbox_inches='tight')
    fig.savefig(outdir+"/"+var+"_2dmap_good.pdf",bbox_inches='tight')
    plt.close()

    fig, ax = plt.subplots(figsize=(8,10))
    arr2 = pixels["all"]
    plt.hist2d(xflat,yflat,bins=[118,16],weights=arr2)

    cbar = plt.colorbar()
    cbar.set_label(ztitle,fontweight='bold')
    ax.set_xlabel("column",fontweight='bold')
    ax.set_ylabel("row",fontweight='bold')

    plt.tight_layout()
    fig.savefig(outdir+"/"+var+"_2dmap_all.png",bbox_inches='tight')
    fig.savefig(outdir+"/"+var+"_2dmap_all.pdf",bbox_inches='tight')
    plt.close()

def main():

    global mapsa_names 
    global mapsas
    global vendor
    global outdir

    mapsa_names = []
    mapsas = []

    # Select vendor
    parser = argparse.ArgumentParser(description='MaPSA summary plots')
    parser.add_argument('-f','--file',nargs='+',help='vendor name')
    args = parser.parse_args()

    infile = args.file[0]
    name = infile.split('.txt')[0]
    outdir = name+"-plots"

    if name == "HPK":
        vendor = "Vendor 1"
    elif name == "QPT":
        vendor = "Vendor 2"     
    elif name == "AEM":
        vendor = "Vendor 3"
    elif "qpt" in name:
        vendor = "QPT"
    else:
        print("Invalid vendor name")

    # Load MaPSAs
    print('Reading MaPSA names from ' + infile)

    with open(infile) as f:
        reader = csv.reader(f,delimiter=' ')
        mapsa_info = [row for row in reader]
        mapsa_names = [row[1] for row in mapsa_info]

    for m in mapsa_names:
        fname = 'pickles/'+m+'.pkl'
        if os.path.isfile(fname):
            print("Loading MaPSA " + m)
            mapsa = cPickle.load(open(fname,'rb'))
        else: 
#            mapsa = MaPSA(m)
            print("Missing pickle for ", m)

        mapsas += [mapsa]

    # Make plots
    global badchips
    badchips = [""]
    badchips += ["HPK_35494_002R-6","HPK_35494_002R-16","HPK_35494_005R-13"]
    badchips += ["AEM_35494_002L-2","AEM_35494_002L-5","AEM_35494_002L-6","AEM_35494_002L-8","AEM_35494_002L-9","AEM_35494_002L-10"]
    global mycolors
    mycolors = ['silver','royalblue']

    IV_plot()
    current_plot()
#    memory_plot()
#    register_plot()

    # Pixel plots
    global allpix
    global allpix_bad
    global npix

    if os.path.isfile(outdir+"/allpix.csv"):
        allpix = pd.read_csv(outdir+"/allpix.csv")
        allpix_bad = pd.read_csv(outdir+"/allpix_bad.csv")
    else:
        print("Creating pixel array")

        allpix = pd.DataFrame([])
        allpix_bad = pd.DataFrame([])

        for m in mapsas:
            for chip in m.mpa_chips:
                thepixels = chip.pixels
                thepixels["mapsa"] = [chip.mapsa_name]*1888
                thepixels["mpa"] = [chip.index]*1888

                if chip.mapsa_name+"-"+str(chip.index) in badchips:
                    allpix_bad = allpix_bad.append(thepixels)
                else:
                    allpix = allpix.append(thepixels)
                
        if len(allpix_bad) == 0:
            allpix_bad = pd.DataFrame(columns=allpix.columns)

        noise_to_scale = ["CAL_RMS","CAL_RMS_pretrim","THR_RMS","THR_RMS_pretrim","Bump_RMS"]
        for x in noise_to_scale:
            allpix[x] = allpix[x]/np.sqrt(2)
            allpix_bad[x] = allpix_bad[x]/np.sqrt(2)
        mean_to_shift = ["CAL_Mean","CAL_Mean_pretrim","THR_Mean","THR_Mean_pretrim"]
        for x in mean_to_shift:
            allpix[x] = allpix[x]+1
            allpix_bad[x] = allpix_bad[x]+1

        allpix.to_csv(outdir+"/allpix.csv")
        allpix_bad.to_csv(outdir+"/allpix_bad.csv")

    npix = len(allpix["pa"])

    if 1: # stacked plots 

        pixel_plot("pa","Response to 100 pulses",np.linspace(-20,220,60))
        pixel_plot("mask","is unmaskable",np.linspace(-1.5,1.5,4))
#        pixel_plot("trimbits","Trim bits",np.linspace(-20,60,16))
    
        # Threshold and noise
        pixel_plot("CAL_Mean","CAL mean",np.linspace(-24,256,60))
        pixel_plot("CAL_RMS","CAL noise",np.linspace(-2,10,60))
        
        pixel_plot("THR_Mean","THR mean",np.linspace(-24,256,60))
        pixel_plot("THR_RMS","THR noise",np.linspace(-2,10,60))
        
        pixel_plot("CAL_Mean_pretrim","CAL mean (pretrim)",np.linspace(-24,256,60))
        pixel_plot("CAL_RMS_pretrim","CAL noise (pretrim)",np.linspace(-2,10,60))
        
        pixel_plot("THR_Mean_pretrim","THR mean (pretrim)",np.linspace(-24,256,60))
        pixel_plot("THR_RMS_pretrim","THR noise (pretrim)",np.linspace(-2,10,60))
        
        pixel_plot("Bump_RMS","Bump test noise at -2V",np.linspace(-2,10,60))
        
    if 1: # overlay plots

        pixel_overlay("CAL_Mean","CAL_Mean_pretrim","CAL Mean",["Post-trim","Pre-trim"],np.linspace(-24,256,60))
        pixel_overlay("THR_Mean","THR_Mean_pretrim","THR Mean",["Post-trim","Pre-trim"],np.linspace(-24,256,60))
        
        pixel_overlay("CAL_RMS","CAL_RMS_pretrim","CAL RMS",["Post-trim","Pre-trim"],np.linspace(-2,10,60))
        pixel_overlay("THR_RMS","THR_RMS_pretrim","THR RMS",["Post-trim","Pre-trim"],np.linspace(-2,10,60))
                
    pixel_map("pa","dead/inefficient/noisy pixels")
    pixel_map("mask","unmaskable pixels")
    pixel_map("CAL_RMS","Average noise (CAL)")
    pixel_map("THR_RMS","Average noise (THR)")  

if __name__ == "__main__":
    main()
