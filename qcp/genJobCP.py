### NEW DIR FOR JOB // PSI4 AND GAMESS
def newDirCP(path, File, template):
    import os
    from shutil  import copyfile
    from genJob import numTemp

    temp = numTemp(path)

    # INCASE I APPENDED TO END OF FILE
    trFile = File.split('_')[0].replace('.xyz','')

    # MAKE DIRECTORY FOR NEW JOB/INP

    if temp > 1:
        name = trFile.replace('.xyz','') + '-' +\
        template.replace('.template', '')
        if not os.path.isdir(path + 'CP-' + name):
            os.mkdir(path + 'CP-' + name)
        npath = path + 'CP-' + name + '/'
        copyfile(path + File, npath + trFile + '.xyz')

    else:
        name = trFile.replace('.xyz','')
        if not os.path.isdir(path + 'CP-' + name):
            os.mkdir(path + 'CP-' + name)
        npath = path + 'CP-' + name + '/'
        copyfile(path + File, npath + trFile + '.xyz')

    return npath


# COUNTERPOISE -----------------------------------

### COUNTERPOISE PSI4
def psi_cpoise(path, File, template, sysData, jobTemp, dist):
    import os, re
    from supercomp  import host
    from genJob     import xyzTemp
    from genJob     import job_replace
    from templates  import psi_rjnJob
    from templates  import psi_gaiJob
    from templates  import psi_masJob
    from write      import write_inp
    from write      import write_job

    name = File.replace('.xyz', '').split('_')[0]

    # MAKE NEW DIR AND NEW PATH
    npath = newDirCP(path, File, template)

    # UNPACK sysData
    fragList, atmList, totChrg, totMult = sysData

    # CREATE xyzData
    xyzData = []
    for frag in fragList:
        for atm in atmList:
            if atm['id'] in frag['ids']:
                xyzData.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])

    # PUT XYZ IN TEMPLATE
    input = xyzTemp(path, template, xyzData)

    # IF bsse_type='cp' PSI4 ONLY ONE CALC
    cp_type = False
    for line in input:
        if "bsse_type=" in line and "'cp'" in line:
                cp_type = True

    # IF bsse_type='cp' PSI4 ONLY ONE CALC
    if cp_type:
        # REMOVE EXTRA '--' AND CHARGE MULTIPLICITY
        cp_input = []
        for line in input:
            if type(line) != list:
                if '--' in line:
                    pass
                elif re.search('\s*-?[0-9]\s*[0-9]\s*', line):
                    pass
                else:
                    cp_input.append(line)
            else:
                cp_input.append(line)

        # COUNT WHICH ATOM UP TO
        count = 0
        input = []
        for i in range(len(cp_input)):
            # IF ATOM LINE
            if type(cp_input[i]) is list:
                # FOR EACH FRAG
                put = False
                for frag in fragList:
                    # IF ATOM NUMBER LAST ATOMS OF FRAG
                    if count == frag['ids'][0]:
                        # IF NOT FIRST FRAG
                        if not count == fragList[0]['ids'][0]:
                            input.append('--\n')
                        input.append(str(frag['chrg'])+' '+str(frag['mult'])+'\n')
                        input.append(cp_input[i])
                        put = True
                if not put:
                    input.append(cp_input[i])
                count += 1

            else:
                input.append(cp_input[i])


        # WRITE INP
        write_inp(npath, name, input)

        # WRITE JOB
        lines = False

        if jobTemp:
            lines = job_replace(name, jobTemp)
        else:
            hw = host()
            if hw == 'rjn':
                lines = psi_rjnJob(name)
            elif hw == 'gai':
                lines = psi_gaiJob(name)
            elif hw == 'mas':
                lines = psi_masJob(name)

        if lines:
            write_job(npath, name, lines)


    # NORMAL INPUT -------------------------
    else:
        # IF NOT RADIAL CUTOFF FOR MOLS INCLUDED DO ALL
        if not dist:
            for i in range(len(input)):
                if type(input[i]) != list:
                    # CHANGE MEMORY to 64
                    #if 'memory' in input[i]:
                    #    line = input[i].split()
                    #    memory = line[1]
                    #    input[i] = input[i].replace(memory, '64')
                        # CHANGE CHRG AND MULT
                    if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                        # IF CHRG = MULT COULD BE TRICKY
                        input[i] = ' ' + str(totChrg) + ' ' + str(totMult) + '\n'

            # WRITE INP
            write_inp(npath, name, input)

            # WRITE JOB
            lines = False
            if jobTemp:
                lines = job_replace(name, jobTemp)
            else:
                hw = host()
                if hw == 'rjn':
                    lines = psi_rjnJob(name)
                elif hw == 'gai':
                    lines = psi_gaiJob(name)
                elif hw == 'mas':
                    lines = psi_masJob(name)

            if lines:
                write_job(npath, name, lines)

            # FOR EACH FRAGMENT
            for frag in fragList:
                ifrag = []
                for atm in atmList:
                    if atm['id'] in frag['ids']:
                        ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
                    else:
                        # MAKE OTHER FRAGS GHOST
                        ifrag.append(['@' + atm['sym']] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

                # MAKE FOLDERS
                if not os.path.isdir(npath + frag["name"]):
                    os.mkdir(npath + frag["name"])

                # PUT XYZ IN TEMP FOR EACH FRAG
                input = xyzTemp(path, template, ifrag)

                # CHANGE CHARGE AND MULTIPLICITY/MEMORY
                # MEMORY OF INPUT NEEDS TO BE >>> MEM JOB
                for i in range(len(input)):
                    if type(input[i]) != list:
                        # CHANGE CHRG AND MULT
                        if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                            # IF CHRG = MULT COULD BE TRICKY
                            input[i] = ' ' + str(frag['chrg']) + ' ' + str(totMult) + '\n'
                # WRITE INPUT FILE FOR EACH FRAG
                write_inp(npath + frag["name"] + '/', frag["name"], input)

                # WRITE JOB
                lines = False
                if jobTemp:
                    lines = job_replace(frag["name"], jobTemp)
                else:
                    hw = host()
                    if hw == 'rjn':
                        lines = psi_rjnJob(frag["name"])
                    elif hw == 'gai':
                        lines = psi_gaiJob(frag["name"])
                    elif hw == 'mas':
                        lines = psi_masJob(frag["name"])

                if lines:
                    write_job(npath + frag["name"] + '/', frag["name"], lines)

        # IF RADIAL CUTOFF FOR MOLS INCLUDED IN EACH FILE
        else:
            from xyzGenerate import xyzShell

            # GET < DIST SEPARATED FRAGS
            # xyzList = [frag, mol, ghost atoms]
            xyzList = xyzShell(path, File, sysData, dist, returnList=True)

            # FOR EACH FRAGMENT CENTER
            for frag, firstMol, otherMol in xyzList:
                ifrag = []
                for atm in firstMol:
                    ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
                for atm in otherMol:
                    ifrag.append(['@' + atm['sym']] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

                # MAKE FOLDERS
                if not os.path.isdir(npath + frag["name"]):
                    os.mkdir(npath + frag["name"])

                # PUT XYZ IN TEMP FOR EACH FRAG
                input = xyzTemp(path, template, ifrag)

                # CHANGE CHARGE AND MULTIPLICITY/MEMORY
                # MEMORY OF INPUT NEEDS TO BE >>> MEM JOB
                for i in range(len(input)):
                    if type(input[i]) != list:
                        # CHANGE CHRG AND MULT
                        if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                            # IF CHRG = MULT COULD BE TRICKY
                            input[i] = ' ' + str(frag['chrg']) + ' ' + str(totMult) + '\n'
                        # CHANGE MEMORY
                        if re.search('memory', input[i]):
                            line = re.split(' |G|g', input[i])
                            for bit in line:
                                if re.search('[0-9]', bit):
                                    input[i] = input[i].replace(bit, '64')
                                    break
                # WRITE INPUT FILE FOR EACH FRAG
                write_inp(npath + frag["name"] + '/', frag["name"], input)

                # WRITE JOB
                lines = False
                if jobTemp:
                    lines = job_replace(frag["name"], jobTemp)
                else:
                    hw = host()
                    if hw == 'rjn':
                        lines = psi_rjnJob(frag["name"])
                    elif hw == 'gai':
                        lines = psi_gaiJob(frag["name"])
                    elif hw == 'mas':
                        lines = psi_masJob(frag["name"])

                if lines:
                    write_job(npath + frag["name"] + '/', frag["name"], lines)


def g09_cpoise(path, File, template, sysData, dist):
    # CREATES JOB FILE FROM TEMPLATE AND .xyz
    import re
    from genJob    import xyzTemp
    from write      import write_job

    # NAME AFTER COUNTERPOISE
    name = File.replace('.xyz', '').split('_')[0]

    # MAKE NEW DIR AND NEW PATH
    npath = newDirCP(path, File, template)

    # UNPACK sysData
    fragList, atmList, totChrg, totMult = sysData
    nfrags = len(fragList)

    if not dist:

        # CREATE xyzData
        xyzData = []
        for frag in fragList:
            for atm in atmList:
                if atm['id'] in frag['ids']:
                    xyzData.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])

        # PUT XYZ IN TEMPLATE
        input    = xyzTemp(path, template, xyzData)
        input_cp = input[:]

        # CHANGE INPUT LINES
        for i in range(len(input)):
            if type(input[i]) != list:
                # CHANGE CHRG AND MULT
                if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                    # IF CHRG = MULT COULD BE TRICKY
                    input[i] = ' ' + str(totChrg) + ' ' + str(totMult) + '\n'
                # CHANGE OUTPUT NAME
                if re.search('\.log', input[i]) \
                or re.search('\.out', input[i]):
                    # KEEP LINE TO REPLACE
                    chng = input[i].split()
                    for val, bit in enumerate(chng):
                        if '.log' in bit:
                            n = val
                    # chng[n] = a1b3d2.log
                    input[i] = input[i].replace(chng[n], name + '.log')

        # WRITE JOB FOR TOTAL CALC
        write_job(npath, name, input)

        # WRITE JOB FOR CPOISE CORRECTION
        # MAKE SURE INTO INPUT
        inInput = False
        # COUNT PLACE IN COORDS
        t = 0
        for i in range(len(input_cp)):
            if "module load" in input_cp[i]:
                inInput = True
            if inInput and type(input_cp[i]) != list:
                if "#" in input_cp[i]:
                    if 'counterpoise' in input_cp[i]:
                        input_cp[i] = input_cp[i].replace("counterpoise=*",'')
                    else:
                        input_cp[i] = input_cp[i].\
                        replace('\n'," counterpoise=" + str(nfrags) + '\n')
                elif re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input_cp[i]):
                    # IF CHRG = MULT COULD BE TRICKY
                    input_cp[i] = str(totChrg) + ',' + str(totMult)
                    for frag in fragList:
                        input_cp[i] += ' ' + str(frag['chrg']) + ',' + str(frag['mult'])
                    input_cp[i] = input_cp[i] + '\n'
                # CHANGE OUTPUT NAME
                if re.search('\.log', input_cp[i]) or re.search('\.out', input_cp[i]):
                    # KEEP LINE TO REPLACE
                    chng = input_cp[i].split()
                    for val, bit in enumerate(chng):
                        if '.log' in bit:
                            n = val
                    # chng[n]   = blahblah.log
                    input_cp[i] = input_cp[i].replace(chng[n], 'cp-' + name + '.log')
            # FIND WHICH FRAG ATOM PART OF
            elif inInput and type(input_cp[i]) == list:

                atm = atmList[t]
                input_cp[i] = [atm['sym'], atm["x"], atm["y"], atm["z"], str(int(atm["grp"]) + 1)]

                # NUMBER ATOM
                t += 1

        # WRITE COUNTERPOISE JOB
        write_job(npath, 'CP-'+ name, input_cp, cp = True)

        # FOR EACH FRAGMENT
        for frag in fragList:
            ifrag = []
            for atm in atmList:
                if atm['id'] in frag['ids']:
                    ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
                else:
                    # MAKE OTHER FRAGS GHOST
                    ifrag.append([atm['sym']+ '-Bq'] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

            # PUT XYZ IN TEMP FOR EACH FRAG
            input = xyzTemp(path, template, ifrag)
            # CHANGE CHARGE AND MULTIPLICITY/MEMORY
            # MEMORY OF INPUT NEEDS TO BE >>> MEM JOB
            for i in range(len(input)):
                if type(input[i]) != list:
                    # CHANGE CHRG AND MULT
                    if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                        # IF CHRG = MULT COULD BE TRICKY
                        input[i] = ' ' + str(frag['chrg']) + ' ' + str(totMult) + '\n'
                    # CHANGE MEMORY
                    elif re.search(' mem', input[i]):
                        line = re.split('=|G|g', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '16')
                                break
                    elif re.search('%mem', input[i]):
                        line = re.split('=|G|g', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '14')
                                break
                    elif re.search('ncpus', input[i]):
                        line = re.split('=', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '8\n')
                                break
                    elif re.search('nprocshared', input[i]):
                        line = re.split('=', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '8\n')
                                break
            # WRITE INPUT FILE FOR EACH FRAG
            write_job(npath, frag["name"], input)

    # DIST RADIUS TO EXCLUDE MOLS FROM CP CORRECTION
    else:
        from xyzGenerate import xyzShell

        # GET < DIST SEPARATED FRAGS
        # xyzList = [frag, mol, ghost atoms]
        xyzList = xyzShell(path, File, sysData, dist)

        # FOR EACH FRAGMENT CENTER
        for frag, firstMol, otherMol in xyzList:
            ifrag = []
            for atm in firstMol:
                ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
            for atm in otherMol:
                ifrag.append([atm['sym'] + '-Bq'] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

            # PUT XYZ IN TEMP FOR EACH FRAG
            input = xyzTemp(path, template, ifrag)

            # CHANGE CHARGE AND MULTIPLICITY/MEMORY
            # MEMORY OF INPUT NEEDS TO BE >>> MEM JOB
            for i in range(len(input)):
                if type(input[i]) != list:
                    # CHANGE CHRG AND MULT
                    if re.search('^\s*-?[0-9]\s*-?[0-9]\s*$', input[i]):
                        # IF CHRG = MULT COULD BE TRICKY
                        input[i] = ' ' + str(frag['chrg']) + ' ' + str(totMult) + '\n'
                    # CHANGE MEMORY
                    elif re.search(' mem', input[i]):
                        line = re.split('=|G|g', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '16')
                                break
                    elif re.search('%mem', input[i]):
                        line = re.split('=|G|g', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '14')
                                break
                    elif re.search('ncpus', input[i]):
                        line = re.split('=', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '8\n')
                                break
                    elif re.search('nprocshared', input[i]):
                        line = re.split('=', input[i])
                        for bit in line:
                            if re.search('[0-9]', bit):
                                input[i] = input[i].replace(bit, '8\n')
                                break

            # WRITE INPUT FILE FOR EACH FRAG
            write_job(npath, frag["name"], input)


### COUNTERPOISE PSI4
def orc_cpoise(path, File, template, sysData, jobTemp, dist):
    import os, re
    from supercomp  import host
    from genJob     import xyzTemp
    from genJob     import job_replace
    from templates  import orc_rjnJob
    from write      import write_inp
    from write      import write_xyz
    from write      import write_job

    name = File.replace('.xyz', '').split('_')[0]

    # MAKE NEW DIR AND NEW PATH
    npath = newDirCP(path, File, template)

    # UNPACK sysData
    fragList, atmList, totChrg, totMult = sysData

    # IF NOT RADIAL CUTOFF FOR MOLS INCLUDED DO ALL
    if not dist:

        # FOR EACH FRAGMENT
        for frag in fragList:
            ifrag = []
            for atm in atmList:
                if atm['id'] in frag['ids']:
                    ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
                else:
                    # MAKE OTHER FRAGS GHOST
                    ifrag.append([atm['sym'] + ':'] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

            # MAKE FOLDERS
            if not os.path.isdir(npath + frag["name"]):
                os.mkdir(npath + frag["name"])

            # PUT XYZ IN TEMP FOR EACH FRAG
            input = xyzTemp(path, template, ifrag)

            # CHANGE CHARGE AND MULTIPLICITY/MEMORY
            for i in range(len(input)):
                if type(input[i]) != list:

                    # CHANGE CHRG AND MULT
                    if re.search('^\*xyzfile\s*-?[0-9]\s*-?[0-9]\s*', input[i]):
                        if totChrg == '?':
                            print("Cannot determine chrg/mult, using template values")
                        # IF CHRG = MULT COULD BE TRICKY
                        else:
                            line = input[i].split()
                            if '.xyz' in line[-1]:
                                input[i] = '*xyz ' + str(frag["chrg"]) + ' ' + str(frag["mult"]) + '\n'

                                # ADD XYZ AS GHOST ATOMS
                                for atm in ifrag:
                                    i += 1
                                    input.insert(i, atm)

                                # END XYZ
                                input.insert(i+1, '*')

                                # WILL CHANGE NUMBER OF LINES - DO NOT CONTINUE THIS LOOP
                                break

            # WRITE INPUT FILE FOR EACH FRAG
            write_inp(npath + frag["name"] + '/', name +'-'+ frag["name"], input)

            # WRITE JOB
            lines = False
            if jobTemp:
                lines = job_replace(name +'-'+ frag["name"], jobTemp)
            else:
                hw = host()
                if hw == 'rjn':
                    lines = orc_rjnJob(name +'-'+ frag["name"])

            if lines:
                write_job(npath + frag["name"] + '/', name +'-'+ frag["name"], lines)

    # IF RADIAL CUTOFF FOR MOLS INCLUDED IN EACH FILE
    else:
        from xyzGenerate import xyzShell

        # GET < DIST SEPARATED FRAGS
        # xyzList = [frag, mol, ghost atoms]
        xyzList = xyzShell(path, File, sysData, dist, returnList=True)

        # FOR EACH FRAGMENT CENTER
        for frag, firstMol, otherMol in xyzList:
            ifrag = []
            for atm in firstMol:
                ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
            for atm in otherMol:
                ifrag.append([atm['sym'] + ":"] + [atm['nu'], atm["x"], atm["y"], atm["z"]])

            # MAKE FOLDERS
            if not os.path.isdir(npath + frag["name"]):
                os.mkdir(npath + frag["name"])

            # PUT XYZ IN TEMP FOR EACH FRAG
            input = xyzTemp(path, template, ifrag)

            # CHANGE CHARGE AND MULTIPLICITY/MEMORY
            # MEMORY OF INPUT NEEDS TO BE >>> MEM JOB
            for i in range(len(input)):
                if type(input[i]) != list:
                    # CHANGE CHRG AND MULT
                    if re.search('^\*xyzfile\s*-?[0-9]\s*-?[0-9]\s*', input[i]):
                        if totChrg == '?':
                            print("Cannot determine chrg/mult, using template values")
                        # IF CHRG = MULT COULD BE TRICKY
                        else:
                            line = input[i].split()
                            if '.xyz' in line[-1]:
                                input[i] = '*xyzfile ' + str(totChrg) + ' ' + str(totMult) + ' ' +line[-1]

                if re.search('.xyz', input[i]):
                    line     = input[i].strip()
                    line     = line.rsplit(' ', 1)[0]
                    input[i] = line+' '+name+'-ghost.xyz\n'

            # WRITE GHOST FILE XYZ
            write_xyz(npath + frag["name"] + '/', frag["name"] + "-ghost", ifrag)

            # WRITE INPUT FILE FOR EACH FRAG
            write_inp(npath + frag["name"] + '/', frag["name"], input)

            # WRITE JOB
            lines = False
            if jobTemp:
                lines = job_replace(frag["name"], jobTemp)
            else:
                hw = host()
                if hw == 'rjn':
                    lines = orc_rjnJob(frag["name"])

            if lines:
                write_job(npath + frag["name"] + '/', frag["name"], lines)
