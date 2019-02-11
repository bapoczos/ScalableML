# A script that can be used to clean an AMI to avoid
# issues when Flintrock tries to launch a cluster from
# this AMI.  This should be executed before creating
# an AMI of this machine.

#remove id_rsa
rm -f $HOME/.ssh/id_rsa

#remove anything related to spark
rm -rf $HOME/spark

cd /usr/local/bin
rm -f *


