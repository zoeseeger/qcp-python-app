def giveUserInfo():
    lines = \
""" -------------------------------------
Processor for GAMESS, PSI4 & GAUSSIAN
-------------------------------------
-h, --help : will print help which shows optional arguments
-f, --file : allows the user to identify just one file
             for otherwise will use either all .xyz
             or all .log/.out in folder
-t, --task : user can specify the task performed and skip
             printing of menu
-j, --jobfile
           : user can specify a file to use as a template
             job file, otherwise if none is specified a
             pre-prepared template will be used or if
             job.template exists in the current directory
             that will be used
--info     : prints a summary of README
-----------------------------------------------------
Generate inp/job files from template-----------------
 - Generates input files for all xyz files in folder
 - Expects a file in folder called *.template which
   is a GAMESS, PSI4 or GAUSSIAN input file
 - Job file is found in order of:
     1. File provided by --jobfile or -j
     2. File names template.job in directory
     3. Stock job template
Pull energies----------------------------------------
 - Pulls energies from *log and *out files
 - Extracts MP2, HF, DFT and ZPVE if they are found
Check log files and sort-----------------------------
 - All files ending with '.out' or '.log' will be
   processed except those starting with 'f-'
 - New xyz files are generated for optimisation if
   they have completed at least one geometry step
Mass sed---------------------------------------------
 - For easily swapping out strings
 - Can swap more than one string by separating each
   one by the & symbol
Mass rename------------------------------------------
 - Swap any part of a name with another string
 - Can specify extention of those to change
Delete jobs from queue-------------------------------
 - Number - Removes the last N number of jobs
     defined by the user from the bottom of the queue
 - All - All jobs will be deleted
 - Name - Any part of the name visible by the queue
    that matches the string will be deleted
Counterpoise correction------------------------------
 - PSI4 and Gaussian
 - Use standard Gaussian or PSI4 input file and the
   counterpoise files will be created
Distance and angles----------------------------------
Submit all com/job in folder-------------------------
Inflate system---------------------------------------
 - The minimum distance of all inter-fragment
   distances is used to scale to find a scaler that
   increases the this distance to that desired. An
   atom of each fragment that has the minimum
   distance to a surrounding fragment is then scaled
   and the relative coordinated of the rest of the
   fragment are used to reconstruct the molecule
   around the scaled atom. If any atom of the
   fragment is scaled and not the one with the
   minimum interionic distance much larger
   intermolecular distances will be observed compared
   to that of the absolute minimum distance.
 - This algorithm works best if similar
   intermolecular distances are had by all fragments.
   For example, if distances between fragment 1 and 2
   have a  minimum intermolecular distance 2A larger
   than that of fragments 1 and 3 (which is the
   minimum intermolecular distance) then distance
   1-2 will become 2*(desired distance) while
   distance 1-3 will become the desired distance.
 - Multiple distances can be given with a space
   between values
 - Created xyz's have the form filename_newdistA.xyz
Quit-------------------------------------------------\n
"""
    print(lines)