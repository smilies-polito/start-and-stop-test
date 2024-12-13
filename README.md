## Experimental setup

Follow these steps to setup for reproducing the experiments provided in ....
1) Install `Singularity` from https://docs.sylabs.io/guides/3.0/user-guide/installation.html:
	* Install `Singularity` release 3.10.2, with `Go` version 1.18.4
	* Suggestion: follow instructions provided in _Download and install singularity from a release_ section after installing `Go`
	* Install dependencies from: https://docs.sylabs.io/guides/main/admin-guide/installation.html

2) Clone the optimizing_physiboss repository in your home folder
```
git clone https://github.com/smilies-polito/optimizing_physiboss.git #change the link
```

3) Move to the optimizing_physiboss source subfolder, and build the optimizing_physiboss Singularity container with 
```bash
cd  optimizing_physiboss/source
sudo singularity build optimizing_physiboss.sif optimizing_physiboss.def
```
or using fake root privileges
```bash
cd  optimizing_physiboss/source
singularity build --fakeroot optimizing_physiboss.sif optimizing_physiboss.def
```

## Reproducing the analysis interactively within the optimizing_physiboss Singularity container

To run testing, manually launch the optimizing_physiboss Singularity container. Move to the `source` folder, and launch the scripts as follows.

First of all, launch the optimizing_physiboss Singularity container
```bash
cd optimizing_physiboss/source
singularity shell optimizing_physiboss.sif
```
This will run a shell within the container, and the following prompt should appear:
```bash
Singularity>
```

Now follow the steps below. 

#### Utility Test

The utility test demonstrates a practical use of the Start & Stop add-on by allowing the interruption and resumption of a simulation with updated parameters to convert an unsuccessful treatment into a successful one in real-time.

To run the utility test, navigate to the test folder and execute the utility_test.py script, specifying the folder where you want the test output to be saved and an image, as shown in the paper (DOI...).
```bash
Singularity> cd ../test
Singularity> python utility_test.py /path/to/yout/output/folder/
```

#### Quantitative Test

The quantitative test is performed to ensure that the Start & Stop add-on does not introduce biases into the simulator. To run the quantitative test, follow the same steps as for the utility test, but execute the quantitative_test.py script instead.
```bash
Singularity> cd ../test
Singularity>python quantitative_test.py /path/to/yout/output/folder/
```

## Reproducing the analysis running the optimizing_physiboss Singularity container

To reproduce the analysis from this paper, run the Singularity container optimizing_physiboss.sif, specifying the output folder where you want the images to be saved.

Move to the `source` folder and run the `optimizing_physiboss.sif` file
```bash
cd optimizing_physiboss/source
singularity run optimizing_physiboss.sif /path/to/yout/output/folder/
```
## Disclaimer

Although the images used in the paper were generated in this same way, they may slightly differ from those produced by running these commands due to the high degree of randomness inherent in the simulator.

