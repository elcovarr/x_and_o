#import xo_package.RebelComponent as RC
#import xo_package.GroupsHelper as GH
import xo_package as XO
import ray
import glob

def main():

    # Initialize ray
    ray.init()

    # DEVICE = -1 # Number of the GPU, -1 if want to use CPU
    DIR = "groups" # directory with files

    # Create Neo4j driver
    driver = XO.create_driver()
    
    # Change to json for driver to read & when creating triples
    txt_to_json_tasks = [XO.txt_to_json.remote(DIR)]
    ray.get(txt_to_json_tasks)

    # Get all json files
    # ???: ray it?
    files = glob.glob(DIR + '/*.json')

    # Store graph in Neo4j driver with info in creating coref and rel_ext models
    cinfo = {'name': 'en_core_web_lg', 'disable':['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer']}
    rinfo = {'name': 'en_core_web_sm', 'disable': ['ner', 'lemmatizer', 'attribute_rules', 'tagger']}
    store_content_tasks1 = []
    for file in files:
            print(f"Parsing {file}")
            store_content_tasks1.append(XO.store_content.remote(driver, cinfo, rinfo, file))
    ray.get(store_content_tasks1)


    # ------------------ ------------------ ------------------ ------------------ ------------------ #

    # Create second model
    # TODO: change parameters

    # Store graph in Neo4j driver with info in creating coref and rel_ext models
    cinfo2 = {'name': 'en_core_web_lg', 'disable':['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer']}
    rinfo2 = {'name': 'en_core_web_sm', 'disable': ['ner', 'lemmatizer', 'attribute_rules', 'tagger']}
    store_content_tasks1 = []
    for file in files:
            print(f"Parsing {file}")
            store_content_tasks1.append(XO.store_content.remote(driver, cinfo2, rinfo2, file))
    ray.get(store_content_tasks1)


    # Shutdown ray
    ray.shutdown()

    return

if __name__ == "__main__":
    main()