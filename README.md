# Archimedes [![Build Status](https://travis-ci.org/Bitergia/archimedes.svg?branch=master)](https://travis-ci.org/Bitergia/archimedes) [![Coverage Status](https://coveralls.io/repos/github/Bitergia/archimedes/badge.svg?branch=master)](https://coveralls.io/github/Bitergia/archimedes?branch=master)

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
    
  Locate an object based on its alias or its type and ID or title on disk and import it to Kibana. If 
  `find` is set to true, it also loads the related objects (i.e., visualizations, 
  search and index pattern).
  
  The operation can overwrite previous versions of existing objects.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--obj-type ...                    # type of the object to import
--obj-id/title/alias ...          # ID/title/alias of the object to import
--find                            # find and import also the objects referenced in the input object
--force                           # overwrite any existing objects on ID conflict
```
  
- **Export objects to disk**

  Locate an object by its ID, alias or title in Kibana and export it to a folder path. The exported data 
  is divided into several folders according to the type of the objects exported 
  (i.e., visualizations, searches and index patterns).

  The operation can overwrite previous versions of existing files.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--export                          # action (required)
--obj-type ...                    # type of the object to export
--obj-id/title/alias ...          # ID/title/alias of the object to export
--force                           # overwrite an existing file on file name conflict
--index-pattern                   # export the index pattern related to the target object
```

- **Inspect objects handled by Archimedes**
  
  List the objects stored in Kibana or in the Archimedes folder.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--inspect                         # action (required)
--local                           # inspect objects in the Archimedes folder 
--remote                          # inspect objects in Kibana
```

- **Populate the Archimedes registry**
  
  Populate the registry file based on the objects stored in Kibana. The registry will include a
  list of entries which contain the metadata of the Kibana objects and the associated aliases.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--registry                        # action (required)
--populate                        # action (required)
--force                           # overwrite an existing object on ID conflict
```

- **Show the Archimedes registry**
  
  Show the content of the registry. If `alias` and `obj_type` are null, it returns the
  content of all the registry. Otherwise, it returns the information related to the single `alias` or
  the aliases associated with the given `obj_type`.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--registry                        # action (required)
--show                            # action (required)
--alias ...                       # the name of the target alias
--obj-type ...                    # type of the objects to list
```

- **Delete the Archimedes registry**
  
  Delete the content of the registry. If `alias` is not null, it deletes only the information
  corresponding to that alias.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--registry                        # action (required)
--delete                          # action (required)
--alias ...                       # the name of the target alias
```

- **Update the Archimedes registry**
  
  Change a given alias saved in the registry with a new alias.
  
```buildoutcfg
archimedes
http://...                        # Kibana URL (required)
...                               # Archimedes folder (required)
--registry                        # action (required)
--update                          # action (required)
--alias ...                       # the name of the target alias
--new-alias ...                   # the name of the new alias
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

- **Import a visualization by alias** 
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--import
--obj-alias 1
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

- **Export a dashboard by alias**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--export
--obj-alias 1
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

- **Inspect the objects stored in Kibana**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--inspect 
--remote
```

- **Inspect the objects stored on disk**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--inspect 
--local
```

- **Populate the registry, forcing the overwriting**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--populate 
--force
```

- **Show the full registry**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--show
```

- **Show the information of a single alias in the registry**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--show
--alias x
```

- **Show the information of aliases of a given type**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--show
--obj-type dashboard
```

- **Clear the registry content**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--clear
```

- **Delete a given alias from the registry**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--delete
--alias x
```

- **Update an existing alias in the registry**
```buildoutcfg
archimedes
http://admin:admin@localhost:5601
/home
--registry 
--update
--alias x
--new-alias y
```


## License

Licensed under GNU General Public License (GPL), version 3 or later.