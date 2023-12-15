import xo_package.RebelComponent as RC

import pandas as pd
from neo4j import GraphDatabase

import glob
import json
import ray


# Define Neo4j connection 
def create_driver():
    host = 'bolt://127.0.0.1:7687'
    user = 'neo4j'
    password = '12345678'
    return GraphDatabase.driver(host,auth=(user, password))


# Change txt files to json files
# call ray
@ray.remote
def txt_to_json(DIR):
    for file in glob.glob("../" + DIR+"/*.txt"):
        record = {}
        record['title'] = file.split("/")[-1]
        content = open(file).read()
        record['text'] = content
        open(file+".json","w").write(json.dumps(record))



# Create query to run and save into Neo4j driver

import_query = """
UNWIND $data AS row
MERGE (h:Entity {id: CASE WHEN NOT row.head_span.id = 'id-less' THEN row.head_span.id ELSE row.head_span.text END})
ON CREATE SET h.text = row.head_span.text
MERGE (t:Entity {id: CASE WHEN NOT row.tail_span.id = 'id-less' THEN row.tail_span.id ELSE row.tail_span.text END})
ON CREATE SET t.text = row.tail_span.text
WITH row, h, t
CALL apoc.merge.relationship(h, toUpper(replace(row.relation,' ', '_')),
  {file_id: row.file_id},
  {},
  t,
  {}
)
YIELD rel
RETURN distinct 'done' AS result;
"""

# ???: create driver session for each process? ; so create driver session for each ray_id?
def run_query(driver, query, params={}):
    with driver.session() as session:
        result = session.run(query, params)
        return pd.DataFrame([r.values() for r in result], columns=result.keys())

# @ray.remote
def store_content(driver, DEVICE, cinfo, rinfo,  file):
    #try:
    file_id = file.split("/")[-1].split(".")[0]
    f = open(file)
    doc = json.load(f)
    
    # Add coreference resolution model
    coref = RC.spacy.load(cinfo['name'], disable=cinfo['disable'])
    coref.add_pipe(
        "xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": DEVICE})
    
    # Define rel extraction model
    rel_ext = RC.spacy.load(rinfo['name'], disable=rinfo['disable'])
    rel_ext.add_pipe("rebel", config={
        'device':DEVICE, # Number of the GPU, -1 if want to use CPU
        'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
        )
    
    # call ray
    for input_text in doc["text"].split("\n\n"):
        print(input_text[:100])
        coref_text = coref(input_text)._.resolved_text
        try:
            doc = rel_ext(coref_text)
            params = [rel_dict for value, rel_dict in doc._.rel.items()]
            for p in params:
                p['file_id']=file_id
            run_query(driver, import_query, {'data': params})
        except:
            print("Failed")
    #except Exception as e:
    #  print(f"Couldn't parse text for {page} due to {e}")
