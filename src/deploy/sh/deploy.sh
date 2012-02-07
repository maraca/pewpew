#!/bin/bash

# This follows the following instructions 
# 1) clone repo to /tmp
# 2) remove useless folders such as .git or dns zones.
# 3) run bootstrap.py as well as bin/buildout
# 4) tarball the package
# 5) upload to s3
# 6) identify the list of machines in production
# 7) ssh into each of them and have them pull the new deploy and link latest/ to the latest deploy
# 8) restart services like apache


# arg order : deploy.sh ~/deploy/path name_of_the_bucket ~/.path/to/pair.key /path/to/remote/config

REPO=$1
BUCKET=$2
KEY=$3
REMOTE_CMD=$4
echo $REMOTE_CMD
user='ubuntu'
path_to_clone='/tmp/deploy/'
cur_time=$(date +%Y%m%d-%H%M%S)
deploy_dir="${path_to_clone}${cur_time}"

echo $deploy_dir
mkdir $path_to_clone

#1 clone repo to /tmp
git clone $REPO $deploy_dir

# 2) remove useless folders such as .git and dns zones
cd $deploy_dir
rm -rf .git/
rm -rf zones/

# 3) run bootstrap.py as well as bin/buildout
python2.6 bootstrap.py
bin/buildout

# 4) tarball the package
tarball_pkg="${cur_time}.tar.gz"
cd ../ && tar -czf $tarball_pkg $cur_time
mv $tarball_pkg $cur_time && cd $cur_time

# 5) upload to s3
s3cmd put $tarball_pkg s3://$BUCKET

# 6) identify the list of machines in production
prod_machines=(`ec2-describe-instances| awk {'print $4'} | grep amazonaws.com`)

# 7-8) ssh into each of them and have them pull the new deploy 
for machine in "${prod_machines[@]}"
do
	echo "Deploying to: ${machine}"
	ssh ${user}@${machine} -i ${KEY} 'bash -s' < $REMOTE_CMD $BUCKET $tarball_pkg  $cur_time
done


