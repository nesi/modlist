import subprocess, re
def get_between(string_start, string_end):

    #source /etc/bashrc doesn't work on maui for some reason
    stdout = subprocess.check_output('module -t avail', stderr=subprocess.STDOUT, shell=True).decode("utf-8")

    #Split between start and end strings.
    stdout = stdout.split(string_start)[1].split(string_end)[0]

    #stdout = stdout.split('/opt/nesi/XC50_sles12_skl/modules/all:')[1].split('/opt/cray/ari/modulefiles:')[0]
    return stdout


def parse_maui(stdout):
 
    #Define empty dictionary
    out_dictionary={}

    lastApp=""

    #Get names of all apps
    for line in stdout.split('\n'):
        #Check if this is the same app as last time.
        thisApp=line.split('/')[0]
        if len(thisApp)>0:
            #If new app, add to dictionary.
            if lastApp!=thisApp:
                out_dictionary[thisApp]={'versions':{}}
            #If add to versionlist
            out_dictionary[thisApp]['versions'][line]=['maui']

    return out_dictionary

def parse_mahuika(stdout):
 
    #Define empty dictionary
    out_dictionary={}

    lastApp=""

    #Get names of all apps
    for line in stdout.split('\n'):
        #check not nasty 'DefaultModules'
        if len(line)>0 and line!='DefaultModules' and line!='libpmi':
            #Mahuika has seperate row for parent
            if line.endswith('/'):
                out_dictionary[line[:-1]]={'versions':{}}
            else:
                out_dictionary[line.split('/')[0]]['versions'][line]=['mahuika']
                #out_dictionary[line[:-1]]['versions'].append(line)

            
    return out_dictionary

def parse_remain(out_dictionary, cluster):

    #For each app
    for key, value in out_dictionary.items():
        
        #Whatis it
        data=subprocess.check_output('module -t whatis ' + key, stderr=subprocess.STDOUT, shell=True).decode("utf-8")
        print(data)
        print(key)

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

        print(key + ":")
        print(out_dictionary[key])
        print('\n')


    return out_dictionary

