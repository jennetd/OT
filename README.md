Jennet Dickinson

October 28, 2020

Code for analyzing MaPSA test results (forked from Hannsjoerg's repo at https://github.com/haweber/OT/)

Note:
All code assumes that test results for MaPSA $mapsaname are stored in ../Results_MPATesting/$mapsaname. 

Plot summary of many MaPSAs:
First create directories plots/ and pickles/

Put the MaPSAs you want to draw plots for in a text file with two columns. The first column should contain the name corresponding to the input data in ../Results_MPATesting/$mapsaname, and the second should contain the name you would like printed on the plots. 

```
python CollectMaPSAs.py -f $inputfile
```

This creates the 2D pixel maps for each MaPSA and saves them in plots/$mapsaname/

To draw the plots summarizing the performance of all MaPSAs in $inputfile, do

```
python SummaryAllMaPSA.py -n $inputfile
```


