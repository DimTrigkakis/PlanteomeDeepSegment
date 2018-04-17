rm -rf ./penv
virtualenv ./penv
source ./penv/bin/activate

pip install --upgrade pip
pip install --upgrade setuptools
pip install http://download.pytorch.org/whl/cu90/torch-0.3.0.post4-cp27-cp27mu-linux_x86_64.whl 
pip install torchvision 
pip install numpy 
pip install -r ./DeepBuild/deep_requirements.txt

deactivate
