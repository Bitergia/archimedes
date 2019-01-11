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

- **Import objects from disk** 
    
  Locate an object based on its type and ID or title on disk and import it to Kibana. If 
  `find` is set to true, it also loads the related objects (i.e., visualizations, 
  search and index pattern).
  
  The operation can overwrite previous versions of existing objects.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--obj-type ...                    # Type of the object to import (required)
--obj-id/title ...                # ID/title of the object to import (required)
--find                            # find and import also the objects referenced in the input object
--force                           # overwrite any existing objects on ID conflict
```
  
- **Export objects to disk**

  Locate an object by its ID or title in Kibana and export it to a folder path. The exported data 
  is divided into several folders according to the type of the objects exported 
  (i.e., visualizations, searches and index patterns).

  The operation can overwrite previous versions of existing files.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--export                          # action (required)
--obj-type ...                    # Type of the object to export (required)
--obj-id/title ...                # ID/title of the object to export (required)
--force                           # overwrite an existing file on file name conflict
--index-pattern                   # export the index pattern related to the target object
```

## Examples

- **Import a dashboard by ID, forcing the overwriting** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--import
--obj-type dashboard
--obj-id git
--force
```

- **Import a visualization by ID** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--import
--obj-type visualization
--obj-id git_main_numbers
```

- **Import a dashboard by content title and related objects**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--import
--obj-type dashboard
--obj-title Git
--find
--force
```

- **Import a visualization by ID and related objects**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--import
--obj-type visualization
--obj-id git_main_numbers
```

- **Export a dashboard by ID**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--export
--obj-type dashboard
--obj-id Git
--force
```

- **Export a visualization by ID and its index pattern**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--export
--obj-type visualization
--obj-id git_commits_organizations
--force
--index-pattern
```


## License

Licensed under GNU General Public License (GPL), version 3 or later.