# XO Example1 

This program runs a set of text files in the `groups` directory and creates a knowledge graph with the use of Neo4j, specifying the type of models to run when creating the graph. 

## Setup 

This project requires some libraries that may need to be installed. Use the documentation from the libraries to install it properly and your device. The full Python setup of libraries is under `example1` directory called `setup.md`. 

### Other Software Requirements 

Make sure to also install Neo4j Desktop. This is needed to create the graph.  

## Running the Project 

This project has a file called `Groups.py` that utilizes the `xo_package` and is an example of running the following steps to utilize the package and create a graph in Neo4j in a distributed way. 

To run the project, go to the directory `example1/` and run the spacey_pipeline kernel in this directory. To activate it, run the following on the command line: ` source /path/to/spacey_pipeline/bin/activate`.  

### Prerequisites 

Open a Python script. We named ours `Groups.py`. Import our package called `xo_package` inside the python script by adding the following line: `import xo_package as XO`. To parallelize, make sure to also import `ray` and `glob` libraries. 

To parallelize some of the functions, initialize ray: `ray.init()` 

Create a variable for the device number the script will use. It is recommended to set the device number (``DEVICE``) to –1 if you want to use the CPU. Create a directory variable that gives the path to the text files used for the graph. 

Next, create a driver that will be used to create a session in Neo4j by calling our command `create_driver()`.  

To create triples for the graph, we need to transform the text files to json files with the package function `txt_to_json()`. This is where we first encounter a place to parallelize the work using `ray`.  Create a list of ray ids when calling remote. Here is an example: 

``` python 

txt_to_json_tasks = [XO.txt_to_json.remote(DIR)] # Create asynchronous tasks   

ray.get(txt_to_json_tasks) # Run the tasks 

``` 

After all the text files have been transformed into json files, get a list of those json files. `glob` has a function called `glob()` that can be used for this. 

### Creating Models 

Now that the prerequisites for creating a driver and transforming the data have been done, you must create two separate dictionary variables. One will be for the *coreference resolution model* (`cinfo`) and the other for the *relation extraction model* (`rinfo`). A ‘name’ key should have a model name. The model name should come from spaCy. Here is a link to the [English pipeline model](https://spacy.io/models/en) we used in one of our models. The other key value pair is ‘disable’ that contains a list of any components that should be excluded when loading. Below are the examples of our two model pipelines: 

```python 

cinfo = {'name': 'en_core_web_lg', 'disable':['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer']} 

rinfo = {'name': 'en_core_web_sm', 'disable': ['ner', 'lemmatizer', 'attribute_rules', 'tagger']} 

``` 

To run the model on one json file, call `store_content()` with the following variables in order: 

* driver 

* DEVICE 

* cinfo 

* rinfo 

* file 

Inside of ` store_content()`, the package is distributing the data using ray. 

Don’t forget to shutdown ray (`ray.shutdown()`) after running the above function on all files.  

**You are now able to query data inside Neo4j!** 
