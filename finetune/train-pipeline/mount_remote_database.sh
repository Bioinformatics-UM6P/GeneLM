# Install
#sudo apt install sshfs
#brew install sshfs

# Mounting remote dataset from toubkal to local machine
mkdir data
sshfs mahouzonssou.akoteno@toubkal.hpc.um6p.ma:/home/mahouzonssou.akoteno/GeneAnnotator/data /home/biolab-office-1/DATALAB/LLM_GeneAnnotator/data

# Unmounting
#fusermount -u /home/biolab-office-1/DATALAB/LLM_GeneAnnotator/data