#!/usr/bin/python
import subprocess, re, json, socket, requests, os, datetime

def get_between(string_start, string_end):

    # Calls module avail and returns value between input strings.

    #source /etc/bashrc doesn't work on maui for some reason
    stdout = subprocess.check_output('module -t avail', stderr=subprocess.STDOUT, shell=True).decode("utf-8")

    #Split between start and end strings.
    stdout = stdout.split(string_start)[1].split(string_end)[0]

    #stdout = stdout.split('/opt/nesi/XC50_sles12_skl/modules/all:')[1].split('/opt/cray/ari/modulefiles:')[0]
    return stdout


def parse_remain(out_dictionary, cluster):

    #For each app in list get details.
    for key, value in out_dictionary.items():
        
        #Whatis it
        data=subprocess.check_output('module -t whatis ' + key, stderr=subprocess.STDOUT, shell=True).decode("utf-8")

        #Parse data appropriately(Sorry Peter)
        #regexShort = r"(?<=Description: ).*(?=" + re.escape(key) + r"/)"
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

        if len(matchesHomepage)>0:
            out_dictionary[key]['homepage'] = matchesHomepage[0] #.strip()
        
        out_dictionary[key][cluster] = True

        #print(key + ":")
        #print(out_dictionary[key])
        #print('\n')


    return out_dictionary

def get_mahuika(call_avail):

    try:
        with open('mahuikaApps.json') as json_file: 
                mahuikaData = json.load(json_file)
    except:
        print("Problem loading mahuikaApps.json, using empty dict")
        mahuikaData = {}
    
    if call_avail :
        print("Reading modules from Mahuika")
        #Check if running on mahuika01, and recheck modules
        if socket.gethostname()=='mahuika01' or socket.gethostname()=='mahuika02':

            print("Working...")
            #Call 
            stdout = get_between('/opt/nesi/CS400_centos7_bdw/modules/all:', '/opt/nesi/share/modules/all:')

            #Define empty dictionary
            mahuikaData={}
            lastApp=""

            #Get names of all apps
            for line in stdout.split('\n'):
                #check not nasty 'DefaultModules'
                if len(line)>0 and line!='DefaultModules' and line!='libpmi':
                    #Mahuika has seperate row for parent
                    if line.endswith('/'):
                        mahuikaData[line[:-1]]={'versions':{}}
                    else:
                        mahuikaData[line.split('/')[0]]['versions'][line]=['mahuika']
                        #out_dictionary[line[:-1]]['versions'].append(line)

            mahuikaData = parse_remain(mahuikaData, 'mahuika')

            f = open("mahuikaApps.json","w+")
            f.write(json.dumps(mahuikaData))
            f.close()

            print("Module avail complete")
        else:
            print('Must be run on Mahuika to update module list, using last run data.')
    else:
        print('Skipping Mahuika avail')

    return mahuikaData


def get_maui(call_avail):

    try:
        with open('mauiApps.json') as json_file: 
                mauiData = json.load(json_file)
    except:
        print("Problem loading mauiApps.json, using empty dict")
        mauiData = {}

    if call_avail :
        print("Reading modules from Maui")
        #Check if running
        if  socket.gethostname()=='maui01' or socket.gethostname()=='maui02':

            print("Working...")

            #Call 
            stdout = get_between('/opt/nesi/XC50_sles12_skl/modules/all:', '/opt/cray/ari/modulefiles:')

            #Define empty dictionary
            mauiData={}
            lastApp=""

            #Get names of all apps
            for line in stdout.split('\n'):
                #Check if this is the same app as last time.
                thisApp=line.split('/')[0]
                if len(thisApp)>0:
                    #If new app, add to dictionary.
                    if lastApp!=thisApp:
                        mauiData[thisApp]={'versions':{}}
                    #If add to versionlist
                    mauiData[thisApp]['versions'][line]=['maui']

            mauiData = parse_remain(mauiData, 'maui')

            f = open("mauiApps.json","w+")
            f.write(json.dumps(mauiData))
            f.close()

            print("Module avail complete")
        else:
            print('Must be run on Maui to update module list, using last run data.')
    else:
        print('Skipping Maui avail')

    return mauiData


def deep_merge(over, under):
#Deep merges dictionary
#If conflict over has pref
    for key, value in over.items():
        if isinstance(value, dict):
            # get node or create one
            node = under.setdefault(key, {})
            deep_merge(value, node)
        else:
            under[key] = value

    return under


# Start
if not os.path.exists('settings.json'):
    print("No 'settings.json' file")
    with open('settings.json', "w") as json_file: 
        json_file.write(json.dumps({"remote":"","token":"","update_maui":True,"update_mahuika":True}))
    print("Empty 'settings.json' file created")

with open('settings.json') as json_file: 
    settings=json.load(json_file)

# Update
print(settings)
# Whether to update.
mahuikaData = get_mahuika(settings["update_mahuika"])
mauiData = get_maui(settings["update_maui"])

#Merge cluster lists
mergedData=deep_merge(mauiData,mahuikaData)

#Apply Domain tags
with open('domainTags.json') as json_file: 
    domainTags = json.load(json_file)
    for key, domain in domainTags.items():
        for app in domain:
            if app in mergedData:
                mergedData[app]["cats"]=[key]
            else:
                print("Error! Domain tag '" + app + "' does not correspond to a application on the platform.")
 
#Apply Overwrites
with open('overwriteApps.json') as json_file: 
        mergedData=deep_merge(mergedData, json.load(json_file))

timestamp=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print("Updated as of " + timestamp) 

output_dict={"modules":mergedData,"date":timestamp}

with open('moduleList.json', "w") as json_file: 
    json_file.write(json.dumps(output_dict))

print("Done!")
