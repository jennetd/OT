mapsa=$1

./html.sh $mapsa

scp -r $mapsa jdickins@lxplus.cern.ch:/eos/project/c/cmsweb/www/tracker-upgrade/MaPSA/preproduction/
