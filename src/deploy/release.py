#!/usr/bin/python2.6
# Copyright (c) 2011, martincozzi.com.
"""Enter brief description here.

Enter more details here about this file.
"""

__author__ = 'contact@martincozzi.com'

import boto
import datetime
import git
import os 
import shutil
import tarfile

from boto.s3.key import Key


class Release:
    """Push a release to S3"""

    def __init__(self, bucket, source, cert):
        self.key = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        self.cert = cert
        self.source = source
        self.package_name = None
        self.s3connection = boto.connect_s3()
        self.ec2connection = boto.connect_ec2()
        self.bucket = self.s3connection.create_bucket(bucket)

    def upload(self):
        """Push the release to S3."""
        if self.package_name is None:
            return 'Please pack before deploying'
        
        s3_release = Key(self.bucket)
        s3_release.key = '%s.tar' % self.key
        s3_release.set_contents_from_filename(self.package_name)
        print '"%s" has been uploaded to s3 in bucket "%s"' % (
                self.package_name, self.bucket.name)
    
    def pack(self):
        """Pack a tar file to push to S3.
        Clones the Git repo into a temp folder,
        Remove the .git folder.
        Runs bootstrap
        Runs buildout
        Tarball the repo in /tmp/deploy/YY-MM-DD-HH-SS
        """
        destination = '/tmp/deploy/%s' % self.key
        # try to create the directory
        try:
            os.makedirs(destination)
        except OSError, error:
            pass
        # clone
        clone_destination ='%s/release-%s' % (destination, self.key)
        repo = git.Repo(self.source)
        clone = repo.clone(clone_destination)
        
        # remove .git
        shutil.rmtree('%s/.git/' % clone_destination)

        # go in to the new repo and run buildout
        os.chdir(clone_destination)
        os.system('python2.6 bootstrap.py')
        print 'Bootstrap [OK]'
        os.system('bin/buildout')
        print 'Buildout [OK]'
        # go up one folder
        os.chdir(os.path.dirname(os.getcwd()))
        self.package_name = '%s/%s.tar' % (destination, self.key)
        package = tarfile.open(name=self.package_name,  mode='w:gz')
        package.add('release-%s' % self.key)
        package.close()

    def _pull(self, instance='localhost'):
        """Once the Release pushed to S3, it needs to be pulled
        from the EC2 servers
        Build a SSH query and execute it remotely.
        This pulls the latest release from S3.
        """
        remote_destination = '/app/'
        s3_get_command = """'s3cmd get s3://%s/%s.tar %s &&
                            cd %s &&
                            tar -xf %s.tar &&
                            ln -sfn release-%s latest  &&
                            cd latest &&
                            bin/buildout -o '""" % (
	        self.bucket.name,
            self.key,
            remote_destination,
            remote_destination,
            self.key,
            self.key)

        ssh_command = 'ssh ubuntu@%s -i %s %s' % (
                instance,
                self.cert,
                s3_get_command)
        # execute the command 
        os.system(ssh_command)
        print '[Success] - %s ' % instance


    def distribute(self):
        """Distribute the S3 package to all EC2 instances."""
        reservations = self.ec2connection.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                print instance.public_dns_name
                self._pull(instance.public_dns_name)
