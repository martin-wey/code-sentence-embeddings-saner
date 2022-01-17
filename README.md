# Code Sentence Embedding - https://arxiv.org/abs/2008.03731
Code Sentence Embedding (CSE) repository for the paper _Combining Code Embedding and Static Analysis for Function-Call Completion_ submitted at IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER 21).

This repository contains all the necessary artifacts and instructions to replicate the experiments of the paper.

## **Dataset**
---
Our dataset is based on _Allamanis et al.'s_ 2013 GitHub Java Corpus (http://groups.inf.ed.ac.uk/cup/javaGithub/). We used Eclipse JDT Core to parse the ASTs of all .java files contained within this dataset in order to retrieve function-call sequences. We limited the scope of the sequences to method declarations. Each sequence contains the method declaration name following by the function calls in the method body.

* The dataset used to train our models is available [here](https://zenodo.org/record/4266099#.X6puvWhKgaa).
* The dataset used to test our models is available [here](https://zenodo.org/record/4053151#.X6pHA2hKgaY).

## **Experiment 1 - Naturalness of function calls**
---
We used [SLP-Core](https://github.com/SLP-team/SLP-Core) to compute the cross-entropy of our test projects for various order of _n_-gram JM models. The code is in the following Java project : https://github.com/mweyssow/cse-saner/tree/master/cse-slp.

The code requires slp-core.jar file to be added as external jar. Then, it can be ran within an IDE.

The file `cse/JavaEntropyRunner.java` can be run with the path to the training set as first program argument and the path to the test set as second program argument. Consider using _*_sequences.txt_ files to compute the cross-entropy of a specific test project.
* the variable `cutOffValues` can be altered to allow more cut-off values to be tested.
* the variable `modelOrderValues` can be altered to consider other order values (_in the paper, we choose the model orders with n=1..10_).

## **Experiment 2 - Function-call completion with PV model**
---
We used [Gensim](https://radimrehurek.com/gensim/) to train and evaluate paragraph vector models (_i.e.,_ doc2vec). All the code is implemented in Python 3 in the following project : https://github.com/mweyssow/cse-saner/tree/master/cse.

The only required dependency is Gensim. The code uses _argparse_ so that it can be called from the terminal.

The file `cse/d2v_train.py` is used to train the model. `python d2v_train.py --help` can be called from the terminal to show all the available arguments. The training logs will be saved in a _.log_ file and the model will be saved in a _.bin_ file.
Here is an example of usage:

* `python d2v_train.py --train_set='./data/plain_method_data.txt' --dm=1 --vector_dim=300 --window=8 --min_count=10 --epochs=20 --hs=1 --negative=5 --ns_exponent=0.75 --dbow_words=0`

Once the model trained, you can run the evaluation with the file `cse/d2v_eval_eclipse.py`. The script takes as argument the path to the model _.bin_ file, the path to the training set (_json format_) and the path to the test project (_json format_) to be evaluated. 

* the variable `topk_range` can be altered to evaluate the model for several suggestion lists of size k.
* the script returns the Recall@k and MRR@k metrics.


## **Experiment 3 - Function-call completion with _n_-gram model**
---
For this last experiment, we extend SLP-Core library to allow the completion to be performed with the static analysis.

The file `cse/JavaFunctionPredictionRunner.java` evaluate a _n_-gram model for function-call completion. You can chose one of the smoothing available in SLP-Core library (_here we use JM_), change the vocabulary cut-off or change the order of the _n_-gram model.

The file can be executed within an IDE (_as for the first experiment_). 
* the first program argument is the path to the training set.
* the second program argument is the path to the test sequences (*_sequences.txt in the test dataset_).
* the third program argument is the path to the static analysis proposals (_*_proposals.txt in the test dataset_).

As for the second experiment, the script returns the Recall@k and MRR@k for project under test.
