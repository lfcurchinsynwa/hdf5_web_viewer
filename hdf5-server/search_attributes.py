import h5py
import os
from collections import OrderedDict
from flask import Flask, url_for, request, json, jsonify
import pandas as pd
import time
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)

# context.use_privatekey_file('yourserver.key')
# context.use_certificate_file('yourserver.crt')

app = Flask(__name__)

data_dir = [r"C:\wamp64\www\sfb805\hdf5-files", r"C:\wamp64\www\sfb805\hdf5-files-alt"]

# return hdf5 files from the root folder
@app.route('/getFiles', methods=['POST'])
def get_files():
  files = []
  for i in data_dir:
    for filename in os.listdir(i):
      if filename.endswith(".h5"):
        files.append(filename)
  return(jsonify({"files": files }))

# get the child of each group and subgroup
@app.route('/getKeys', methods=['POST'])
def api_getKeys():
  filename = request.form['filename']
  for i in data_dir:
    try:
      f = h5py.File(os.path.join(i, filename), "r")
      if(request.form['path']):
        path = request.form['path']
        if isinstance(f[path], h5py.Dataset):
          return(path)
        else:
          data = []
          for key in f[path].keys():
            obj = {
              'id' : key,
              'path': path + '/' + key,
              'type': 'group'
            }
            data.append(obj)
          return(jsonify(data))
      else:
        data = []
        for key in f.keys():
          obj = {
            'id' : key,
            'path': '/' + key
          }
          data.append(obj)
        return(jsonify(data))
    except:
      pass

# get the paths of searched attributes
@app.route('/getpath', methods=['POST'])
def api_gethdf():
  tmp_attr = request.form['attributes']
  search_type = request.form['searchType']
  filepath = []
  if not tmp_attr:
    raise Exception("Search value empty")
  
  attributes = OrderedDict()
  incoming_data =json.loads(tmp_attr)
  for index in sorted(incoming_data.keys()):
    attributes[incoming_data[index]['key']] = incoming_data[index]['value']
  paths = []
  connectedPaths = []
  def get_path(name, object):
    if search_type == 'OR':
      for attribute,value in attributes.items():
        if attribute in object.attrs and object.attrs[attribute] == value:
          paths.append(("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:])) + '/' + name)
          filepath.append("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:]))
    elif search_type == 'AND':
      allmatch = True
      for attribute, value in attributes.items():
        if attribute in object.attrs and object.attrs[attribute] == value:
          continue
        else:
          allmatch = False
          break
      if allmatch:
        paths.append(("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:])) + '/' + name)
        filepath.append("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:]))
    else :
      first_attr_name = attributes.keys()[0]
      first_attr_value = attributes[first_attr_name]
      if first_attr_name in object.attrs and object.attrs[first_attr_name] == first_attr_value:
        paths.append(("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:])) + '/' + name)
        filepath.append("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:]))
      for attr_name in attributes.keys()[1:]: 
        attr_value = attributes[attr_name]
        if attr_name in object.attrs and object.attrs[attr_name] == attr_value:
          for path in paths:
            totpath = ("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:]) + '/' + name)
            if path in totpath:
              connectedPaths.append(("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:])) + '/' + name)
              break
          paths.append(("/".join(os.path.normpath(object.file.filename).split(os.sep)[-1:])) + '/' + name)




      # for i, (attribute, value) in  enumerate (attributes.items()):
      #   if attribute in object.attrs and object.attrs[attribute] == value:
      #     paths.append(name)
      #     print(paths)
      #     if (len(paths) > 1 and paths[i] in name):
      #       print("name:"+name)
      #       connectedPaths.append(name)


  for i in data_dir:
    for filename in os.listdir(i):
      if filename.endswith(".h5"):
        f = h5py.File(os.path.join(i, filename), "r")
        f.visititems(get_path)
  result = jsonify({"filePath": list(set(filepath)), "paths": paths, "connectedPaths": connectedPaths, "searchType": search_type})
  return result

# get attributes while clicked on js tree
@app.route('/getattribute', methods=['POST'])
def api_getattr():
  attrs = ''
  tmp_path = request.form['path']
  fileName = request.form['fileName']
  for i in data_dir:
    for filename in os.listdir(i):
      if filename == fileName:
        f = h5py.File(os.path.join(i, filename), "r")
        try:
          attrs = list(f[tmp_path].attrs.items())
        except:
          print("nothing found")
  return jsonify(attrs)

# get the contents of dataframe
@app.route('/fileContents', methods=['POST'])
def api_getContent():
  fileName = request.form['filename']
  path = request.form['path']
  for i in data_dir:
    for filename in os.listdir(i):
      if fileName == filename:
        f = h5py.File(os.path.join(i, filename), "r")
  dset = f[path]
  data = dset[()]
  dataframe = pd.DataFrame(data)
  return dataframe.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
  # return 'OK'

if __name__ == '__main__':
  # app.run(debug=True, port=5050, ssl_context='adhoc')
	app.run(debug=True, port=5050)