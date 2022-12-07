import argparse
from plotter import *

def main():
    
    parser = argparse.ArgumentParser(description='MaPSA trimming plots')
    parser.add_argument('-n','--name',nargs='+',help='name of MaPSA')
    args = parser.parse_args()

    mapsaid = args.name[0]
    print(mapsaid)

    df_edges = pd.DataFrame()
    df_bulk = pd.DataFrame()

    for stype in ['THR','CAL']:

        fig, ax = plt.subplots(4,4, sharex=True, sharey=True)
        for i in range(1,17):
            print(i)

            chipid = str(i)

            cmd = 'ls ../Results_MPATesting/'+ mapsaid + '/mpa_test_'+mapsaid+'_' + chipid + '_*_PostTrim_'+stype+'_'+stype+'_RMS.csv'
            filename = get_recent(cmd)

            df = pd.read_csv(filename, index_col=0)

            is_edge = [(i%118 == 0) or (i%118 == 117) for i in range(0,1888)]
            is_bulk = np.invert(is_edge)

            df_edges = pd.concat([df_edges,df.iloc[is_edge]])
            edges = df.iloc[is_edge].to_numpy()
            ax[int((i-1)/4),int((i-1)%4)].hist(edges,bins=np.linspace(0,5,50),histtype='step',label='edges',color='red',density=True)

            df_bulk = pd.concat([df_bulk,df.iloc[is_bulk]])
            bulk = df.iloc[is_bulk].to_numpy()
            ax[int((i-1)/4),int((i-1)%4)].hist(bulk,bins=np.linspace(0,5,50),histtype='step',label='bulk',color='blue',density=True)

        plt.suptitle(mapsaid + ' ' + stype + ' noise')
        plt.savefig('edge-plots/'+mapsaid+'_'+stype+'.png',bbox_inches='tight')
        plt.savefig('edge-plots/'+mapsaid+'_'+stype+'.png',bbox_inches='tight')
        plt.show()

        fig, ax = plt.subplots(1,1)
        ax.hist(df_edges,bins=np.linspace(0,5,50),histtype='step',label='edges',color='red')
        ax.hist(df_bulk,bins=np.linspace(0,5,50),histtype='step',label='bulk',color='blue')
        ax.set_xlabel(stype+' DAC units')
        ax.set_ylabel('Pixels')

        bulk_mean = np.mean(df_bulk.to_numpy())
        bulk_rms = np.std(df_bulk.to_numpy())
        edge_mean = np.mean(df_edges.to_numpy())
        edge_rms = np.std(df_edges.to_numpy())

        ax.text(0.1,0.8,f"Mean: {np.round(bulk_mean,2)}",transform = ax.transAxes, color='blue')
        ax.text(0.1,0.75,f"RMS: {np.round(bulk_rms,2)}",transform = ax.transAxes, color='blue')
        ax.text(0.1,0.65,f"Mean: {np.round(edge_mean,2)}",transform = ax.transAxes, color='red')
        ax.text(0.1,0.6,f"RMS: {np.round(edge_rms,2)}",transform = ax.transAxes, color='red')

        plt.legend(frameon=False)
        plt.suptitle(mapsaid + ' ' + stype + ' noise')
        plt.savefig('edge-plots/'+mapsaid+'_'+stype+'_total.png',bbox_inches='tight')
        plt.savefig('edge-plots/'+mapsaid+'_'+stype+'_total.png',bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    main()
