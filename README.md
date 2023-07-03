Jennet Dickinson

October 28, 2020

Code for analyzing MaPSA test results (forked from Hannsjoerg's repo at https://github.com/haweber/OT/)

Note:
All code assumes that test results for MaPSA $mapsaname are stored in ../Results_MPATesting/$mapsaname. 

Plot test results of single MaPSA:

python MakeModulePlots_old.py $mapsaname

This draws 2D plots showing noise mean and RMS (THR and CAL), bad bump tests, 
pixel alive, and masking test as a function of pixel position on the MaPSA. 
Results are saved in ../Results_MPATesting/$mapsaname

Plot summary of many MaPSAs:
First create directory pickles to hold pickled objects

python CollectMaPSAs.py -n $outputdir -f $inputfile

where $inputfile contains the list of MaPSAs to run over. 

The first part of this script reads the test results for each MaPSA and save them in a pickled object. If the pickled object for a MaPSA already exists, it is read in rather than recreated to save time.

The second part of this script creates summary plots for the MaPSAs in $inputfile. Results are saved in $outputdir


