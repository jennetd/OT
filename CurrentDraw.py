import numpy as np
import sys, os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.backends.backend_pdf as pltpdf
import csv
import math
import re

def one_mapsa(m, c):

    values = np.array([])

    for i in range(1,17):
        cmd = 'ls ../Results_MPATesting/'+m+'/log*_Chip'+str(i)+'_*.log'
        files = os.popen(cmd).read().split()
        
        if(len(files) > 1):
#            print("Many files for " + m + " Chip " + str(i))
            maxnbr = 0
            maxidx = -1
            for j, f in enumerate(files):
                numbers_from_string = filter(str.isdigit, f)                                                          
                if numbers_from_string > maxnbr:                                                                      
                    maxnbr = numbers_from_string                                                                      
                    maxidx = j
                    
            files = [files[j]]
        
        if len(files) == 1:
        
            cmd = "grep "+ c + " " +files[0]
            
            x = os.popen(cmd).read()                                                                                            
            x = x.replace('I= ', 'CUT')                                                                                         
            x = x.replace(' mA', 'CUT')                                                                                         
            y = x.split('CUT')                                                                                                 
            
            values = np.append(values,[float(y[1])])    
        else:
            print("Wrong number of log files: " + str(len(files)))

    return values

def main():

    mapsas = ['HPK28_1','HPK32_2','HPK34_1','HPK37_2','HPK28_2','HPK34_2','HPK38_1','HPK29_2','HPK35_1','HPK38_2','QuikPak_PS-p-P2','HPK30_1','HPK33_1','HPK35_2','QuikPak_PS-p-P1','QuikPak_PS-p-P2_4','HPK30_2','HPK36_1','QuikPak_PS-p-P1_4','HPK31_1','HPK36_2','HPK31_2','HPK33_2','HPK37_1']

    current_strings = ['P_dig','P_ana','P_pad','Total:']
    current_names = ['I_dig','I_ana','I_pad','I_tot']

    for i,c in enumerate(current_strings):
        values = np.array([])
        for m in mapsas:
            values = np.append(values,one_mapsa(m,c))

        print("Plotting "+current_names[i])
        plt.clf()
        plt.hist(values)

        plot_xlabel = current_names[i] + " [mA]"
        plot_ylabel = "MPA chips"
        plt.title(current_names[i])
        plt.xlabel(plot_xlabel)
        plt.ylabel(plot_ylabel)

#        plt.show()

        fig1 = plt.gcf()
        fig1.show()
        fig1.savefig(current_names[i]+"_histogram.png")

if __name__ == "__main__":
    main()
