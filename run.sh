module load Python
cd /nesi/project/nesi99999/Callum/moduleThing

#Below files should only ever be pulled. Never pushed. Inverse for remainder
git fetch origin
git checkout FETCH_HEAD -- domainTags.json
git checkout FETCH_HEAD -- aliases.json
git checkout FETCH_HEAD -- overwrites.json


python getModules.py
