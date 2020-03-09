# modlist

  Where standard format is:
  
   module_list.json
   ```
   {
     module1:{
         property1:[value1, value2]
     },
     module2:{
         property1:[value1, value2]
     }
   }
  ```
   I'm defining a 'tag' as an attribute defined in the inverted format:
   
  property1_tags.json
  ```
   {
     value1:[module1, module2],
     value2:[module1, module2]
   }
   ```
  This makes it easier for people to assign optional tags


**tags_domains.json** - List of what domain tags to apply. Please add.

**tags_licence_type.json** - Type of licence

**overwrites.json** - Overwrites.

**aliases.json** - Nice names.


***How to update (NeSI staff)***

* Relax - It's automatic now.
