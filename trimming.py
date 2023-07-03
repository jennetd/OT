import argparse
from plotter import *

def main():
    
    parser = argparse.ArgumentParser(description='MaPSA trimming plots')
    parser.add_argument('-n','--name',nargs='+',help='name of MaPSA')
    args = parser.parse_args()

    mapsaid = args.name[0]
    print(mapsaid)

    df_pretrim = pd.DataFrame()
    df_posttrim = pd.DataFrame()

    for stype in ['THR','CAL']:

        fig, ax = plt.subplots(4,4, sharex=True, sharey=True)
        for i in range(1,17):
            print(i)

            chipid = str(i)

            cmd = 'ls ../Results_MPATesting/'+ mapsaid + '/mpa_test_'+mapsaid+'_' + chipid + '_*_PostTrim_'+stype+'_'+stype+'_Mean.csv'
            filename = get_recent(cmd)

            df = pd.read_csv(filename, index_col=0)
            df_posttrim = pd.concat([df_posttrim,df])
            values = df.to_numpy()

            if 'THR' in stype:
                ax[int((i-1)/4),int((i-1)%4)].hist(values,bins=np.linspace(50,150,50),histtype='step')
            else:
                ax[int((i-1)/4),int((i-1)%4)].hist(values,bins=np.linspace(0,50,50),histtype='step')

            cmd = 'ls ../Results_MPATesting/'+ mapsaid + '/mpa_test_'+mapsaid+'_' + chipid + '_*_PreTrim_'+stype+'_'+stype+'_Mean.csv'
            filename = get_recent(cmd)

            df = pd.read_csv(filename, index_col=0)
            df_pretrim = pd.concat([df_pretrim,df])
            values = df.to_numpy()

            if 'THR' in stype:
                ax[int((i-1)/4),int((i-1)%4)].hist(values,bins=np.linspace(50,150,50),histtype='step')
            else:
                ax[int((i-1)/4),int((i-1)%4)].hist(values,bins=np.linspace(0,50,50),histtype='step')

        plt.suptitle(mapsaid + ' ' + stype + ' mean')
        plt.savefig('trim-plots/'+mapsaid+'_'+stype+'.png',bbox_inches='tight')
        plt.savefig('trim-plots/'+mapsaid+'_'+stype+'.png',bbox_inches='tight')
        plt.show()

        fig, ax = plt.subplots(1,1)
        if 'THR' in stype:
            ax.hist(df_pretrim,bins=np.linspace(50,150,50),histtype='step',label='pre-trim',color='red')
            ax.hist(df_posttrim,bins=np.linspace(50,150,50),histtype='step',label='post-trim',color='blue')
        else:
            ax.hist(df_pretrim,bins=np.linspace(0,50,50),histtype='step',label='pre-trim',color='red')
            ax.hist(df_posttrim,bins=np.linspace(0,50,50),histtype='step',label='post-trim',color='blue')

        ax.set_xlabel(stype+' DAC units')
        ax.set_ylabel('Pixels')

        pretrim_mean = np.mean(df_pretrim.to_numpy())
        pretrim_rms = np.std(df_pretrim.to_numpy())
        posttrim_mean = np.mean(df_posttrim.to_numpy())
        posttrim_rms = np.std(df_posttrim.to_numpy())

        ax.text(0.1,0.8,f"Mean: {np.round(pretrim_mean,2)}",transform = ax.transAxes, color='red')
        ax.text(0.1,0.75,f"RMS: {np.round(pretrim_rms,2)}",transform = ax.transAxes, color='red')
        ax.text(0.1,0.65,f"Mean: {np.round(posttrim_mean,2)}",transform = ax.transAxes, color='blue')
        ax.text(0.1,0.6,f"RMS: {np.round(posttrim_rms,2)}",transform = ax.transAxes, color='blue')

        plt.legend(frameon=False)
        plt.suptitle(mapsaid + ' ' + stype + ' threshold')
        plt.savefig('trim-plots/'+mapsaid+'_'+stype+'_total.png',bbox_inches='tight')
        plt.savefig('trim-plots/'+mapsaid+'_'+stype+'_total.png',bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    main()
