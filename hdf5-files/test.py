import h5py
import os
from flask import Flask, url_for, request, json, jsonify
import pandas as pd

app = Flask(__name__)

data_dir = r"C:\wamp64\www\sfb805\hdf5-files"

@app.route('/getFiles', methods=['POST'])
def get_files():
  files = []
  for filename in os.listdir(data_dir):
    if filename.endswith(".h5"):
      files.append(filename)
  return(jsonify({"files": files }))

@app.route('/getKeys', methods=['POST'])
def api_getKeys():
  filename = request.form['filename']
  f = h5py.File(os.path.join(data_dir, filename), "r")
  if(request.form['path']):
    path = request.form['path']
    data = []
    for key in f[path].keys():
      obj = {
        'id' : key,
        'path': path + '/' + key
      }
      data.append(obj)
    return(jsonify(data))
  else:
    data = []
    print("items:", f.items())
    for key in f.keys():
      obj = {
        'id' : key,
        'path': '/' + key
      }
      data.append(obj)
    return(jsonify(data)) 
  

@app.route('/fileContents', methods=['POST'])
def api_getContent():
  def visitor_func(name, node):
    if isinstance(node, h5py.Dataset):
      print(node)
      data = node[()]
      dataframe = pd.DataFrame({'0': data[:,0]})
      return (dataframe.to_html())

  with h5py.File("examplefile_fst_TUD.h5", "r") as f:
    df = f.visititems(visitor_func)
  
  return df

@app.route('/gethdf', methods=['POST'])
def api_gethdf():
  hdfobj = pd.read_hdf('examplefile_fst_TUD.h5', key="/calib_run_01/parameters/magnetic_bearing/current_bias")
  print(hdfobj)
  return hdfobj

if __name__ == '__main__':
	app.run(debug=True, port=5000)
