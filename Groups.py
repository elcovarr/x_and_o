import RebelComponent as RC
import GroupsHelper as GH
import ray

def main():
    ray.init()

    DEVICE = -1 # Number of the GPU, -1 if want to use CPU
    DIR = "groups" # directory with files

    # Add coreference resolution model
    # NOTE: model is defined as 'en_core_web_lg'
    coref = RC.spacy.load('en_core_web_lg', disable=['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    coref.add_pipe(
        "xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": DEVICE})

    # Define rel extraction model
    rel_ext = RC.spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])
    rel_ext.add_pipe("rebel", config={
        'device':DEVICE, # Number of the GPU, -1 if want to use CPU
        'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
        )
    
    # Create Neo4j driver
    driver = GH.create_driver()
    
    # Change to json for driver to read & when creating triples
    txt_to_json_tasks = [GH.txt_to_json.remote(DIR)]
    ray.get(txt_to_json_tasks)

    # Get all json files
    # ???: ray it?
    files = GH.glob.glob(DIR + '/*.json')

    # Store graph in Neo4j driver made using coref and rel_ext
    store_content_tasks = []
    for file in files:
            print(f"Parsing {file}")
            store_content_tasks.append(GH.store_content.remote(driver, coref, rel_ext, file))
    ray.get(store_content_tasks)



    ray.shutdown()

if __name__ == "__main__":
    main()