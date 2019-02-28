#!/usr/bin/python
import json, getModulesFunc, socket, requests

def main():
    if socket.gethostname()!='mahuika01':
        print('Must be run on mahuika')
        return 1


    stdout = getModulesFunc.get_between('/opt/nesi/CS400_centos7_bdw/modules/all:', '/opt/nesi/share/modules/all:')

    out_dictionary = getModulesFunc.parse_mahuika(stdout)

    out_dictionary = getModulesFunc.parse_remain(out_dictionary, 'mahuika')

    outfile = open("mahuikaApps.json","w+")
    outfile.write(json.dumps(out_dictionary))
    outfile.close()
    print("done!")


    #Do curl stuff here.

    return 0

main()