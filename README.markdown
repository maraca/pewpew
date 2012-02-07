pewpew - quick way of deploying your source code to an ec2 cluster.
===================================================================

Introduction
------------
I needed a way of deploying code to a bunch of EC2 instances and execute bash commands after the code shipped. I started writing this out in python but quickly realized that bash made much more sense.
Because some people who must remain unnamed would argue that it's okay to use python for this kind of things, I've left both the python and the bash code so they can judge for themselves.

Overall I guess this is a good example of why using bash often makes more sense than using python when you endup with lots of system calls in your python code :)

Deploy
------

You need to pass 4 arguments to this script:
- The path to the repo you want to deploy.

- The S3 bucket to deploy the code to.

- The path to the EC2 keypair

- The path to the bash file you want to execute in prod.

	$ ./deploy.sh /path/to/repo s3_bucket ~/.amazon/ec2-keypair.pem /path/to/file/to/execute/in/prod.sh 

It requires the ec2-api-tools to be installed.

How this works ?
----------------

It basically grabs your hg repo, clones it, removes the .hg/ folder, make a tarball of your code and ship it to a S3 bucket.
Then it sends a signal to all your EC2 instances to grab that code and to execute a bash file (which could reload apache or supervisor or whatever you want it to do.)
