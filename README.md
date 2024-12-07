# Quantifying the Benefits of Object-Oriented Languages with Higher Order Domains 

#### Nick Cooper, Neelima Prasad, Srikrishna B.R.

We introduce a novel language-agnostic framework for analyzing the structure of software when only one source file is provided. We employ combinatorial complexes, a recently
introduced higher order domain, to accomplish this goal. Our technique is not only able to draw the same conclusions asexisting full code-base methods, but also provides novel insights about the benefits of OO languages.

#### Here is the link to our paper: 

## Requirements

Required python packages: regex, numpy, tqdm, and datasets (from hugging face). You can install them with the following command:
```
python3 -m pip install regex numpy tqdm datasets
```
Tested and developed with python 3.12.3 on a Ubuntu 24.04 system.

## Overview and Instructions

There are three different folders in this repository : Code Examples, Plots, and Scripts <br>
Code examples contains 100 examples (text files) for C++, Java, and Rust. <br>
Plots contains all the figures that are detailed in the paper. <br>
Scripts contains four scripts and one config file.

### Instructions for use: 
There are four scripts: DownloadData, Parser, Analysis, and Validation. For most use cases, you should only ever have to run DownloadData and Analysis. <br>
First, open up the Config.json file in your favorite editor, and modify the attributes at the top to your liking. 
In the paper, we downloaded 30,000 samples for evaluation. However for the purpose of testing, we suggest setting N = 100. <br>
Now, run DownloadData.py, it will save .txt files containing the samples to a CodeExamples/{Language} directory structure. <br>

Next, run Analysis.py. It will generate the combinatorial complexes, save them to disk, and display some of the figures used in the paper. 
There are two command line arguments one may pass to Analysis.py. Use ```--Y {1, 2, 3, 4}``` to plot the different scalar valued metrics discussed in the paper.
Use ```--D``` to also plot the distributional data. Note that assuming you've followed along with N = 100, the figures will be different from the paper due to the reduced sampling size. <br>

For testing, run the Validation script. It will parse the three example pieces of code provided in the Scripts/Tests directory, and check that the combinatorial complexes extracted therefrom are correct. 
