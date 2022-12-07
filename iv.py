import argparse
from plotter import *

def main():

    mapsas = ['AEM77L','AEM78L','AEM79L']
    fig, ax = plt.subplots(1,1)

    for m in mapsas:

        filename = '../Results_MPATesting/'+m+'/IVScan_'+m+'.csv'
        df = pd.read_csv(filename, index_col=0)

        plt.plot(df, label=m)

    ax.set_ylabel('Current [uA]')
    ax.set_xlabel('Voltage [V]')

    plt.legend(frameon=False)
    plt.suptitle('IV scan')
    plt.savefig('plots/iv.png',bbox_inches='tight')
    plt.savefig('plots/iv.png',bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
