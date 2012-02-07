#!/usr/bin/python2.6
"""Enter brief description here.

Enter more details here about this file.
"""

__author__ = 'contact@martincozzi.com'


import gflags as flags
import sys

from deploy.release import Release

flags.DEFINE_string('bucket', None, 'Name of S3 bucket to release')
flags.DEFINE_string('pair_key', None, 'path to AWS Pair Key')
flags.DEFINE_string('repo', None, 'Repo to deploy.')

flags.MarkFlagAsRequired('bucket')
flags.MarkFlagAsRequired('pair_key')
flags.MarkFlagAsRequired('repo')

FLAGS = flags.FLAGS


def deploy(argv=sys.argv):
    """Deploys to S3"""

    try:
        argv = FLAGS(argv)
    except flags.FlagsError, error:
        print '%s\\nUsage: %s ARGS\\n%s' % (error, sys.argv[0], FLAGS)
        sys.exit(1)

    release = Release(FLAGS.bucket, FLAGS.repo, FLAGS.pair_key)
    release.pack()
    release.upload()
    release.distribute()
