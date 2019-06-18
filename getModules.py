#!/usr/bin/python
import subprocess, re, json, socket, requests, os, datetime, math, html

#Read file at {path}. If not exist make one with {default} value
def readmake_json(path,default):
    if not os.path.exists(path):
            print(f"No '{path}' file")
            with open(path, "w") as json_file: 
                json_file.write(json.dumps(default))
            print(f"Empty '{path}' file created")

    with open(path) as json_file: 
        return json.load(json_file)
# Calls  returns value between input strings.
def get_between(string_full, string_start, string_end):

    #Split between start and end strings.
    stdout = string_full.split(string_start)[1].split(string_end)[0]

    return stdout
 
def parse_remain(out_dictionary, cluster, module_path):

    #For each app in list get details.
    for key, value in out_dictionary.items():
        
        #Whatis it this is DUMB DO IT BETTER
        data=subprocess.check_output("MODULEPATH=" + module_path + "; module -t whatis " + key, stderr=subprocess.STDOUT, shell=True).decode("utf-8")

        #Escape
        
        #data = re.escape(data)

        regexHomepage=r"(?<=Homepage: )\S*"
        matchesHomepage = re.findall(regexHomepage, data)
        
        if len(data.split("Description: ")) > 1:
            short=data.split("Description: ")[1]
        elif len(data.split(": "))>1:
            short=(data.split(": "))[1]
        else:
            short=data

        short=short.split(key + "/")[0]

        out_dictionary[key]['short'] = short
        out_dictionary[key]['cats'] = []


        if len(matchesHomepage)>0:
            out_dictionary[key]['homepage'] = matchesHomepage[0] #.strip()
        
        out_dictionary[key][cluster] = True

    return out_dictionary

def get_mahuika(call_avail):

    if call_avail :
        print("Reading modules from Mahuika")
        #Check if running on mahuika01, and recheck modules
        #source /etc/bashrc doesn't work on maui for some reason
        
        print("Working... Takes about 100 sec... for some reason")

        module_path="/opt/cray/pe/craype/default/modulefiles:/opt/cray/pe/modulefiles:/opt/cray/modulefiles:/opt/modulefiles:/opt/nesi/modulefiles:/opt/nesi/CS400_centos7_bdw/modules/all:/opt/nesi/share/modules/all:/cm/local/modulefiles:/cm/shared/modulefiles:/etc/modulefiles"
        #print("MODULEPATH=" + module_path + "; module -t avail")

        stdout_full = subprocess.check_output(("MODULEPATH=" + module_path + "; module -t avail"), stderr=subprocess.STDOUT, shell=True).decode("utf-8")
        #Call 
        stdout_trim = get_between(stdout_full,'/opt/nesi/CS400_centos7_bdw/modules/all:', '/opt/nesi/share/modules/all:')

        #Define empty dictionary
        mahuikaData={}
        lastApp=""

        #Get names of all apps
        for line in stdout_trim.split('\n'):
            #check not nasty 'DefaultModules'
            if len(line)>0 and line!='DefaultModules' and line!='libpmi':
                #Mahuika has seperate row for parent
                if line.endswith('/'):
                    mahuikaData[line[:-1]]={'versions':{}}
                else:
                    mahuikaData[line.split('/')[0]]['versions'][line]=['mahuika']
                    #out_dictionary[line[:-1]]['versions'].append(line)

        mahuikaData = parse_remain(mahuikaData, 'mahuika',module_path)

        print("Module avail complete")
        
    else:
        print('Skipping Mahuika avail')

    return mahuikaData

def get_maui(call_avail):
    try:
        with open('cache/mauiApps.json') as json_file: 
                mauiData = json.load(json_file)
    except:
        print("Problem loading mauiApps.json, using empty dict")
        mauiData = {}

    if call_avail :
        print("Reading modules from Maui")
        #Check if running
        print("Working...")

        #Maui module path
        module_path="/opt/cray/pe/perftools/7.0.2/modulefiles:/opt/cray/pe/craype/2.5.15/modulefiles:/opt/cray/pe/modulefiles:/opt/cray/modulefiles:/opt/modulefiles:/opt/nesi/modulefiles:/opt/nesi/XC50_sles12_skl/modules/all:/opt/nesi/share/modules/all:/opt/cray/ari/modulefiles"
        #print("MODULEPATH=" + module_path + "; module -t avail")

        stdout_full = subprocess.check_output(("MODULEPATH=" + module_path + "; module -t avail"), stderr=subprocess.STDOUT, shell=True).decode("utf-8")
        #print(stdout_full)
        #Call 
        stdout_trim = get_between(stdout_full,'/opt/nesi/XC50_sles12_skl/modules/all:', '/opt/cray/ari/modulefiles:')

        #Define empty dictionary
        mauiData={}
        lastApp=""

        #Get names of all apps
        for line in stdout_trim.split('\n'):
            #Check if this is the same app as last time.
            thisApp=line.split('/')[0]
            if len(thisApp)>0:
                #If new app, add to dictionary.
                if lastApp!=thisApp:
                    mauiData[thisApp]={'versions':{}}
                #If add to versionlist
                mauiData[thisApp]['versions'][line]=['maui']

        mauiData = parse_remain(mauiData, 'maui',module_path)

        f = open("cache/mauiApps.json","w+")
        f.write(json.dumps(mauiData))
        f.close()

        print("Module avail complete")
    else:
        print('Skipping Maui avail')

    return mauiData

def deep_merge(over, under):
    #Deep merges dictionary
    #If conflict 'over' has right of way
    for key, value in over.items():
        #If element is dict, call self.
        if isinstance(value, dict):
            node = under.setdefault(key, {})
            deep_merge(value, node)
        #If element is list (and non unique) append
        elif isinstance(value, list) and key in under:
            #For each member of list
            for thing in value:
                #Not duplicate
                if not thing in under[key]:
                    under[key].append(thing)

        #If element is other, replace.      
        else:
            under[key] = value
    return under

def get_licences():
    string_data=subprocess.check_output("sacctmgr -pns show resource", stderr=subprocess.STDOUT, shell=True).decode("utf-8").strip()

    lic_array=[]

    for lic_string in string_data.split('\n'):
        lic_string_array=lic_string.split('|')
        lic_obj={}
        lic_obj['software']=lic_string_array[0]
        lic_obj['owner']=lic_string_array[1]
        lic_obj['number']=math.floor(int(lic_string_array[3])/2)
        lic_obj['server_type']=lic_string_array[5]

        lic_array.append(lic_obj)

    return lic_array

def main():
    # Start
    settings=readmake_json('settings.json',{"remote":"","token":"","update_maui":True,"update_mahuika":True})

    #Previous run of module show
    maui_cache=readmake_json('cache/maui_cache.json',{})
    mahuika_cache=readmake_json('cache/mahuika_cache.json',{})

    #Last output file, for diffing.
    full_cache=readmake_json('cache/full_cache.json',{})

    # Update
    print(settings)

    #check if on Mahuika
    if not (socket.gethostname()=='mahuika01' or socket.gethostname()=='mahuika02'):
        print("Currently must be run from Mahuika. Because I am lazy.")
        return 1

    # Whether to update. If setting=true runs mod avail. If not merge only.
    mauiData = get_maui(settings["update_maui"])
    mahuikaData = get_mahuika(settings["update_mahuika"])

    #Merge cluster lists
    mergedData=deep_merge(mauiData,mahuikaData)

    #Apply Domain tags
    with open('domainTags.json') as json_file: 
        domainTags = json.load(json_file)

        for key, domain in domainTags.items():

            domain = list(dict.fromkeys(domain))

            for app in domain:
                if app in mergedData:

                    mergedData[app]["cats"].append(key)
                    mergedData[app]["cats"].sort()

                else:
                    print("Error! Domain tag '" + app + "' does not correspond to a application on the platform.")
    
    #Apply Overwrites
    with open('overwriteApps.json') as json_file: 
            mergedData=deep_merge(mergedData, json.load(json_file))

    timestamp=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("Updated as of " + timestamp) 

    output_dict={"modules":mergedData,"date":timestamp}

    with open('cache/mahuika_cache.json', "w+") as json_file: 
        json_file.write(json.dumps(mahuikaData))

    with open('cache/maui_cache.json', "w+") as json_file: 
        json_file.write(json.dumps(mauiData))

    with open('cache/full_cache.json', "w+") as json_file: 
        json_file.write(json.dumps(mahuikaData))

    with open('moduleList.json', "w") as json_file: 
        json_file.write(json.dumps(output_dict))

    print("Done!")

main()