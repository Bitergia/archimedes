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
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
--import                          # action (required)
--json-path ...                   # path of the JSON file that include Kibana objects (required)
--find                            # find and import also the objects referenced in the input file
--visualizations-folder ...       # folder where visualization objects are stored
--searches_folder ...             # folder where searches objects are stored
--index-patterns-folder ...       # folder where index pattern objects are stored
--force                           # overwrite any existing objects on ID conflict
```
  
- **Export object by ID or title**

  Locate an object by its ID or title in Kibana and export it to a folder path. The exported data 
  can be saved in a single file or divided into several folders according 
  to the type of the objects exported (i.e., visualizations, searches and index patterns).

  The operation can overwrite previous versions of existing files.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
--export                          # action (required)
--obj-type ...                    # Type of the object to export (required)
--obj-id/title ...                # ID/title of the object to export (required)
--folder-path  ...                # folder where to export the dashboard objects (default './')
--one-file                        # export the objects to a file (only for dashboards)
--force                           # overwrite an existing file on file name conflict
--index-pattern                   # export the index pattern related to the target object
```

## Examples

- **Import a dashboard** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--import
--json-path ./dashboard_git.json
--force
```

- **Import a visualization** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--import
--json-path ./visualizations/visualization_git_main_numbers.json
--force
```

- **Import a dashboard and related objects**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--import
--json-path ./dashboard_git.json
--find
--force
--visualizations-folder ./visualizations
--index-patterns-folder ./index-patterns
--searches-folder ./searches
```

- **Import a visualization and related objects**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--import
--json-path ./visualizations/visualization_git_main_numbers.json
--find
--force
--visualizations-folder ./visualizations
--index-patterns-folder ./index-patterns
--searches-folder ./searches
```

- **Export a dashboard by ID**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--export
--obj-type dashboard
--obj-id Git
--force
```

- **Export a visualization by ID and its index pattern**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
--export
--obj-type visualization
--obj-id git_commits_organizations
--force
--index-pattern
```


## License

Licensed under GNU General Public License (GPL), version 3 or later.