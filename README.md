# Quantifying the Benefits of Object-Oriented Languages with Higher Order Domains 

We introduce a novel language-agnostic framework for analyzing the structure of software when only one source file is provided. We employ combinatorial complexes, a recently
introduced higher order domain, to accomplish this goal. Our technique is not only able to draw the same conclusions asexisting full code-base methods, but also provides novel insights about the benefits of OO languages.

## Here is the link to our paper :

Required python packages: re (regex), numpy, tqdm, and datasets (from hugging face). Tested and developed with python 3.12.3

Instructions for use: 
There are three scripts: DownloadData, Parser, and Analysis. They are intended to be run in that order. First, open up DownloadData in your favorite editor, and modify the attributes at the top to your liking. 
I suggest NOT downloading 30000 samples like we did in the paper, because it can be very time consuming. Set N = 100 for a simpler test. The download script will save .txt files containing the samples to a CodeExamples/{Language} directory structure.

Next, open up Analysis and modify the value of N on line 211 in correspondance with the first step. Then, when the analysis script is run, it will generate the combinatorial complexes, save them to disk, and display some of the figures used in the paper. 
Feel free to change the idxY argument in the function call on line 211 to see different figures. Note that assuming you've followed along with N = 100, the figures will be different from the paper due to the reduced sampling size. 
