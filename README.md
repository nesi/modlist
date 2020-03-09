# modlist

Anything starting with "tags" is inside out for convenience. e.g. 

tags_domains.json
{
  "engineering": ["ANSYS", "OpenFOAM", "COMSOL"]
}

evaluates as

{
  "ANSYS":{
    "domains":["engineering"]
  },
  "OpenFOAM":{
    "domains":["engineering"]
  },
  "COMSOL":{
    "domains":["engineering"]
  }
}

**tags_domains.json** - List of what domain tags to apply. Please add.

**tags_licence_type.json** - Type of licence

**overwrites.json** - Overwrites.

**aliases.json** - Nice names.


***How to update (NeSI staff)***

* Relax - It's automatic now.
