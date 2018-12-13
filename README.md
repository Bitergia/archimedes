# Archimedes

Import and export Kibana dashboards, visualizations, searches and index patterns from command line.

## Requirements

- requests>=2.7.0
- grimoirelab-toolkit>=0.1.4


## Installation

Archimedes is being developed and tested mainly on GNU/Linux platforms. Thus it is very likely it will work out of 
the box on any Linux-like (or Unix-like) platform, upon providing the right version of Python.

```buildoutcfg
$> git clone https://github.com/Bitergia/archimedes
$> python3 setup.py build
$> python3 setup.py install
```

## How it works

Currently, Archimedes is able to perform the following operations

- **Import objects from file** 

  Import dashboards, index patterns, visualizations and searches from a JSON file to Kibana. The JSON file 
  should be either a list of objects or a dict having a key _objects_ with a list of objects 
  as value (e.g,, {'objects': [...]}.
  
  The operation can overwrite previous versions of existing objects.
  
- **Import dashboard**

  Import a dashboard from a JSON file and the related objects (i.e., visualizations, search and index pattern) located in different folders.
  
  The operation can overwrite previous versions of existing objects.
  
- **Export dashboard by ID or title**

  Locate a dashboard by its ID or title in Kibana and export it to a folder path. The exported data 
  can be saved in a single file or divided into several folders according 
  to the type of the objects exported (i.e., visualizations, searches and index patterns).

  The operation can overwrite previous versions of existing files.

## Examples

- **Import objects from file** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601 # Kibana URL (required)
--import-objects                  # action
--json-path ./dashboard_git.json  # path of the JSON file that include Kibana objects (required)
--no-dashboards'                  # do not import dashboard objects
--no-index-patterns'              # do not import index pattern objects
--no-visualizations               # do not import visualization objects
--no-searches                     # do not import searches objects
--force                           # overwrite any existing objects on ID conflict

```

- **Import dashboard**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601 # Kibana URL (required)
--import-dashboard                # action
--json-path ./dashboard_git.json  # path of the dashboard to import (required)
--visualizations-folder           # folder where visualization objects are stored
--searches_folder                 # folder where searches objects are stored
--index-patterns-folder           # folder where index pattern objects are stored
--force                           # overwrite any existing objects on ID conflict
```

- **Export dashboard by ID**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601 # Kibana URL (required)
--export-dashboard                # action
--dashboard-id                    # ID of the dashboard to export (required)
--folder-path                     # folder where to export the dashboard objects (default './')
--one-file                        # export the dashboard objects to a file
--force                           # overwrite an existing file on file name conflict
```

- **Export dashboard by title**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601 # Kibana URL (required)
--export-dashboard                # action
--dashboard-title                 # title of the dashboard to export (required)
--folder-path                     # folder where to export the dashboard objects (default './')
--one-file                        # export the dashboard objects to a file
--force                           # overwrite an existing file on file name conflict
```


## License

Licensed under GNU General Public License (GPL), version 3 or later.