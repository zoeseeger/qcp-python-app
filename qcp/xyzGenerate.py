
def separate_mols(path, File, sysData):

    from write import write_xyz

    # NAME FOR WRITING FILE, DIRS
    name = File.replace('.xyz','').split('_')[0]

    # UNPACK sysData
    fragList, atmList, totChrg, totMult = sysData

    # FOR EACH FRAGMENT
    for frag in fragList:
        ifrag = []
        for atm in atmList:
            if atm['id'] in frag['ids']:
                ifrag.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])

        # WRITE XYZ
        write_xyz(path, name + '-' + frag["name"], ifrag)


def get_center_of_mass(atmList):
    """Returns center of mass from list of atoms."""
    x, y, z, mass = 0, 0, 0, 0

    # com = X0 * M0 + X1 * M1 + Xn * Mn /  (M0 + M1 + Mn)
    for i in atmList:
        x    += i["x"] * i["mas"]
        y    += i["y"] * i["mas"]
        z    += i["z"] * i["mas"]
        mass += i["mas"]

    return [x/mass, y/mass, z/mass]


def xyzShell(path, File, sysData, dist, returnList=False):
    """Uses a distance to create a shell of molecules
       around each fragment."""
    import math
    from write import write_xyz

    fragList, atmList, totChrg, totMult = sysData

    # FOR EACH FRAGMENT
    for val, frag in enumerate(fragList):


        # GET ATOMS IN THE FRAGMENT
        mol = []

        # FOR EACH ATOM
        for atm in atmList:

            # IF ATOM IN THIS FRAG ADD TO mol
            if atm["id"] in frag["ids"]:
                mol.append(atm)

        # GET CENTER OF MASS OF FRAGMENT
        fragList[val]["com"] = get_center_of_mass(mol)

    # FOR EACH FRAG
    xyzs = []
    for frag in fragList:

        # ADD ORIGIN FRAG TO coordList
        firstMol = []
        otherMol = []
        for atm in atmList:
            if atm["id"] in frag["ids"]:
                firstMol.append(atm)

        # PAIR WITH SECOND FRAG
        for frag2 in fragList:
            if frag != frag2:

                # GET DISTANCE BETWEEN REFERENCE FRAG AND EACH FRAG
                s = (frag["com"][0] - frag2["com"][0]) ** 2 + \
                    (frag["com"][1] - frag2["com"][1]) ** 2 + \
                    (frag["com"][2] - frag2["com"][2]) ** 2
                s = math.sqrt(s)

                # CHECK IF CENTER OF MASS IS WITHIN DIST
                if s < float(dist):
                    # ADD TO coordList
                    for atm in atmList:
                        if atm["id"] in frag2["ids"]:
                            otherMol.append(atm)

                xyzs.append([frag, firstMol, otherMol])

        # PRINT NUMBER OF ATOMS INCLUDED FOR EACH CALCULATION
        print(frag["name"], ':', len(firstMol + otherMol))


    # RETURN LIST
    if returnList:
        return xyzs

    # ADD MOLECULE TOGETHER AND WRITE TO FILE
    for xyz_parts in xyzs:
        xyz = []
        for atm in xyz_parts[1]:
            xyz.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])
        for atm in xyz_parts[2]:
            xyz.append([atm['sym'], atm['nu'], atm["x"], atm["y"], atm["z"]])

        # WRITE FRAGS WITHIN DIST TO XYZ IF NOT returnList
        name = File.replace('.xyz', '') + '-' + xyz_parts[0]["name"] + '-' + dist

        # WRITE
        write_xyz(path, name, xyz)




def get_min_interionic_dist(atmList):
    import math

    # PUT IN relxyz
    mindist = 10000
    for i in atmList:
        for j in atmList:
            if i["id"] < j["id"] and i["grp"] != j["grp"]:
                s = (i["x"] - j["x"]) ** 2 + (i["y"] - j["y"]) ** 2 + (i["z"] - j["z"]) ** 2
                s = math.sqrt(s)
                if s < mindist:
                    mindist = s

    return mindist


def rearrange_list(atmList, fragList):
    from geometry import dist_between

    # ALL INTERIONIC DISTANCES
    for frag in fragList:
        for val, atm1 in enumerate(atmList):
            if atm1['grp'] == frag['grp']:
                for val2, atm2 in enumerate(atmList):
                    # SECOND ATOM FRAG FROM FRAG GREATER THAN FIRST
                    if atm2['grp'] > frag['grp']:
                            x = dist_between(atm1, atm2)

                            if not atm1.get("dist"):
                                atm1["dist"] = x

                            elif x < atm1.get("dist"):
                                atm1["dist"] = x

                            if not atm2.get("dist"):
                                atm2["dist"] = x
                            elif x < atm2.get("dist"):
                                atm2["dist"] = x

    # ATOM LIST SORTED WITH SMALLER DISTS AT START OF DICT
    # CAN NO LONGER USE ID TO IDENTIFY COORD
    atmList = sorted(atmList, key=lambda k: (k['grp'], k['dist']))

    for frag in fragList:
        frag["ids_by_int_dist"] = []
        for atm in atmList:
            if atm["id"] in frag["ids"]:
                frag["ids_by_int_dist"].append(atm["id"])

    return atmList, fragList



def get_relative_coords(atmList, fragList):
    import numpy as np

    # HOLD FIRST ELEM OF EACH FRAG
    coords = np.zeros(shape=(len(atmList), 3))

    # ALL ATOMS RELATIVE TO FIRST ATOM
    relxyz = np.zeros(shape=(len(atmList), 3))

    # PUT IN ACTUAL COORDS
    # ATOM LIST SORTED WITH SMALLER DISTS AT START OF DICT
    # USE ORDER IN FRAGLIST TO ORGANISE COORDS
    i = 0

    for frag in fragList:
        for atm in atmList:
            if atm["id"] in frag['ids_by_int_dist']:
                # FIRST ATOM OF FRAG
                if atm["id"] == frag['ids_by_int_dist'][0]:
                    atm_dic = atm

                # RELXYZ AND COORDS IN ORDER OF APPEARANCE IN FRAGLIST
                coords[i, 0], coords[i, 1], coords[i, 2] = atm_dic["x"], atm_dic["y"], atm_dic["z"]
                relxyz[i, 0] = atm["x"] - atm_dic["x"]
                relxyz[i, 1] = atm["y"] - atm_dic["y"]
                relxyz[i, 2] = atm["z"] - atm_dic["z"]

                i += 1

    return relxyz, coords


def expand(path, File, sysData, dists):
    from write import write_xyz
    import numpy as np

    fragList, atmList, totChrg, totMult = sysData

    # GET SMALLEST INTERIONIC DISTANCE
    # a, b ARE INDEX OF SMALLEST DIST ATOMS
    dmin = get_min_interionic_dist(atmList)

    atmList, fragList = rearrange_list(atmList, fragList)

    relxyz, coords = get_relative_coords(atmList, fragList)

    # FIND NEW ORIGIN // MEAN OF ALL POINTS
    d_origin = np.mean(coords, axis=0)

    # REDEFINE POINTS W.R.T NEW ORIGIN
    coords = coords - d_origin

    # FOR EACH DISTANCE
    for dist in dists:
        scale = dist / dmin
        # SCALE
        coords_new = scale * coords

        # PLUS POSITION OF EACH TO ALL RELATIVE POSITIONS TO GET NEW XYZ
        coords_new = coords_new + relxyz

        # RELXYZ AND COORDS IN ORDER OF APPEARANCE IN FRAGLIST
        i = 0
        newxyz = []
        for frag in fragList:
            for atm in atmList:
                if atm["id"] in frag['ids_by_int_dist']:
                    newxyz.append([atm["sym"], coords_new[i][0], coords_new[i][1], coords_new[i][2]])
                    i += 1

        name = File.replace('.xyz', '_' + str(dist) + 'A')
        write_xyz(path, name, newxyz)
