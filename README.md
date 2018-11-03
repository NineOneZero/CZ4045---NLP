# CZ4045---NLP
Project assignment for NTU CZ4045 Natural Language Processing

## Version information
- Python 3.6


## Contents
- [Placing dataset files](#placing-dataset-files)
- [Project Installation Guide](#project-installation-guide)
- [Usage guide](#usage-guide)


## Placing dataset files
The review dataset file are omitted to save space in project directory. Please place your `CellPhoneReview.json` dataset file in the `dataset/` folder.

## Project Installation Guide
Project setup is as simple as the following 2 steps 
#### Install package requirements
The following command will install the required python packages.
```
$ pip install -r requirements.txt
```

In addition, the following NLTK models need to be downloaded to run some of the features provided by `NLTK` such as `pos tagging`. Run the following codes on a python interpreter.
```
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('averaged_perceptron_tagger')
>>> nltk.download('wordnet')
```

## Usage guide
This section describes the steps or commands needed for running the code that solves the problems listed in the project assignment.

#### 1. Dataset Analysis
Execute the following command in `command prompt` to start Dataset Analysis. A trace simple is available [here](results/Dataset%20Analysis/trace.txt)
```
$ python main.py analysis
``` 

#### 2. Noun Phrase Summarizer

#### 3. Sentiment Word Detection
Once the `CellPhoneReview.json` has been placed in the `dataset/` folder, execute the following command in `command prompt` to start generating the top 20 positive and negative words.
```
$ python main.py sentiment
``` 

#### 4. Application
