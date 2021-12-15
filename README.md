

# NLNDE at MEDOPROF
This repository holds the companion code for the system reported in the paper:

Boosting Transformers for Job Expression Extraction and Classification in a Low-Resource Setting by Lukas Lange, Heike Adel and Jannik Strötgen. In Proceedings of the Iberian Language Evaluation Forum (IberLEF) 2021.

The paper can be found [(here)](http://ceur-ws.org/Vol-2943/meddoprof_paper1.pdf). The code allows the users to reproduce and extend the results reported in the paper. 
Please cite the above paper when reporting, reproducing or extending the results.

    @inproceedings{lange-etal-2021-meddoprof,
          author    = {Lukas Lange and
                       Heike Adel and
                       Jannik Str{\"{o}}tgen},
          title     = {Boosting Transformers for Job Expression Extraction and Classification in a Low-Resource Setting},
          year={2021},
          booktitle= {{Proceedings of The Iberian Languages Evaluation Forum (IberLEF 2021)}},
          series = {{CEUR} Workshop Proceedings},
          url = {http://ceur-ws.org/Vol-2943/meddoprof_paper1.pdf},
    }

In case of questions, please contact the authors as listed on the paper.

## Purpose of the project
This software is a research prototype, solely developed for and published as part of the publication cited above. It will neither be maintained nor monitored in any way.

## Using the NLNDE Model
The following will describe our different scripts to reproduce the results. 
See each of the script files for detailed information on the input arguments. 
    
### Prepare the conda environment
The code requieres some python libraries to work: 

    conda create -n meddoprof python==3.8.5
    pip install flair==0.8 transformers==4.6.1 torch==1.8.1 scikit-learn==0.23.1 scipy==1.6.3 numpy==1.20.3 nltk tqdm seaborn matplotlib


### Get the data

Get the MEDDOPROF training and testing data and unzip the files to a directory called "data"
The directory should look like this:

    ├── data
    │   ├── meddoprof-test-GS.zip
    │   ├── meddoprof-training-set.zip
    │   ├── test
    │   │   ├── class
    │   │   ├── meddoprof-norm-test.tsv
    │   │   └── ner
    │   └── train
    │       ├── meddoprof-complementary-entities
    │       ├── meddoprof-norm-train.tsv
    │       ├── task1
    │       └── task2
    ├── README.md (this file)
    └── scripts
    
    
### Tokenize and split the data

    python step_1_tokenize_files.py
    python step_2_create_data_splits.py --train_files data/bio/train_task_1/ --method strategic --output_dir data/splits/train_task_1/
    python step_2_create_data_splits.py --train_files data/bio/train_task_1/ --method random --output_dir data/splits/train_task_1/
    python step_2_create_data_splits.py --train_files data/bio/train_task_2/ --method strategic --output_dir data/splits/train_task_2/
    python step_2_create_data_splits.py --train_files data/bio/train_task_2/ --method random --output_dir data/splits/train_task_2/

### Train the model (using strategic datasplits)
The following command trains on model on four splits (1,2,3,4) and uses the remaining split (5) for validation. For different split combinations adjust the list of --training_files and the --dev_file arguments accordingly. 
Replace "stategic" with "random" to use random splits instead. 

    python step_3_train_model.py --data_path data/splits/train_task_1/ --train_files strategic_split_1.txt,strategic_split_2.txt,strategic_split_3.txt,strategic_split_4.txt --dev_file strategic_split_5.txt --model xlm-roberta-large --name task1_dev5 --storage_path models
    
### Get ensemble predictions
For all models, get the predictions on the test set as following:

    python step_4_get_test_predictions.py --name models/task1_dev5 --conll_path data/bio/test_task_1/ --out_path predictions/task1_dev5/
    
Then, combine different models into one ensemble. Arguments: Output path + List of model predictions

    python step_5_create_ensemble_data.py predictions/ensemble1 predictions/task1_dev5/ predictions/task1_dev4/ ...
    
Finally, convert the predictions to BRAT format

    python step_6_convert_predictions_to_brat.py --input predictions/ensemble1 --test_files data/bio/test/ner/ --output predictions_brat/ensemble1
    
### Pretrained XLM-R Models
As part of this work, two XLM-R were adapted to the Spanish general (1) and clinical domain (2). 
The models can be found here: 
* Spanish clinical XLM-R [(link)](https://huggingface.co/llange/xlm-roberta-large-spanish)
* Spanish general XLM-R [(link)](https://huggingface.co/llange/xlm-roberta-large-spanish-clinical)
In addition, we trained an English clinical XLM-R [(link)](https://huggingface.co/llange/xlm-roberta-large-english-clinical). More information can be found [here](https://github.com/boschresearch/clin_x)
    
## License
The NLNDE MEDDOPROF code is open-sourced under the AGPL-3.0 license. See the
[LICENSE](LICENSE) file for details.

For a list of other open source components included in Joint-Anonymization-NER, see the
file [3rd-party-licenses.txt](3rd-party-licenses.txt).
