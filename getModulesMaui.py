#!/usr/bin/python
import subprocess, json, re, getModulesFunc, socket

def main():
    if socket.gethostname()!='maui01':
        print('Must be run on maui')
        return 1


    stdout = getModulesFunc.get_between('/opt/nesi/XC50_sles12_skl/modules/all:', '/opt/cray/ari/modulefiles:')

    out_dictionary = getModulesFunc.parse_maui(stdout)

    out_dictionary = getModulesFunc.parse_remain(out_dictionary, 'maui')

    outfile = open("mauiApps.json","w+")
    outfile.write(json.dumps(out_dictionary))
    outfile.close()
    print("done!")

main()