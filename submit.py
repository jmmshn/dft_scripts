#!/usr/bin/env python
import socket
import re
import os

# USER DEFINED PARAMERTERS
# EDIT THESE BASED ON WHAT SYTEMS YOU ARE USING
vers='541_p5'

hostname=socket.gethostname()
print hostname

# get user prompt with a defult value
def ask(prompt, default):
    default_str="["+default+"]"
    prompt='{0:30} {1:14}   ? '.format(prompt,default_str)
    ans=raw_input(prompt)
    if(ans==''):
        return str(default)
    return str(ans)

# return the hostname of the system that you are working on
def chk_host(host_tags):
    hostname=socket.gethostname()
    for ihost in host_tags:
        host_match=re.search(ihost,hostname,re.IGNORECASE)
        if host_match != None:
            return ihost
    raise NameError('No matching machine')

# matching string list of availible systems --- also the tags for vasp versions
host_tags=[
    'guild','comet','stampede','cori','edison', 'optiplex','bridges'
]

sub_sys = {'guild': 'PBS',
           'comet': 'SLURM',
           'bridges': 'SLURM',
           'stampede': 'SLURM',
           'cori': 'SLURM',
           'edison': 'PBS',
           'optiplex': 'BS',
}

wall_time={'guild': '6:00',
           'comet': '6:00',
           'stampede': '2:00',
           'cori': '6:00',
           'edison': '6:00',
           'optiplex': '12:00',
}

def_que={  'guild': 'compute',
           'comet': 'compute',
           'stampede': 'developement',
           'cori': 'regular',
           'edison': 'regular',
           'optiplex': 'no',
}
vers_list=[
    '541_p3','541','535'
]


#################################################################
# optiplex
#################################################################
def ask_optiplex():
    global name,que,nnodes,tpn,np,time
    name =ask("What name do you want to give your job", "job")
    que =ask("Which que should you run on", "development")
    nnodes =ask("How many nodes to run on", "1")
    tpn =ask("How many taskts/node", "24")
    np =0
    time =ask("What is the desired walltime ", "12:00:00")

def prt_optiplex_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    print("""
#SBATCH -J {0}
#SBATCH -o job.o%j
#SBATCH -p {1}
#SBATCH --nodes={2}
#SBATCH --ntasks-per-node={3}
#SBATCH -t {4}
module swap mvapich2_ib openmpi_ib
cd $SLURM_SUBMIT_DIR
echo "****  submission time     TODAY"
echo "****  starting time       `date`"
ibrun $HOME/bin/vasp.{5}
echo "****  end time            `date`"
    """.format(name,que,nnodes,tpn,time,vasp_vers))

#################################################################
# Stampede
#################################################################
def ask_stampede():
    global name,que,nnodes,tpn,np,time
    name =ask("Give a name for your job", "job")
    que =ask("Which que", "development")
    tpn = 0
    np =ask("How many taskts", "24")
    time =ask("What is the desired walltime ", "2:00:00")

def prt_stampede_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    print("""
#!/bin/bash
#SBATCH -J {0}
#SBATCH -o job.o%j
#SBATCH -p {1}
#SBATCH -n {2}
#SBATCH -t {3}
module swap intel intel/14.0.1.106
module swap mvapich2 impi
MPIRUN=`which mpirun`
if [[ $MPIRUN != '/opt/apps/intel13/impi/4.1.3.049/intel64/bin/mpirun' ]]
then
   echo 'ERROR:  could not find the right MPI version'
   exit 1
fi
cd $SLURM_SUBMIT_DIR
echo "****  submission time     TODAY"
echo "****  starting time       `date`"
ibrun $HOME/bin/vasp.{4}
echo "****  end time            `date`"
    """.format(name,que,np,time,vasp_vers))

#################################################################
# Comet
#################################################################

def ask_comet():
    global name,que,nnodes,tpn,np,time
    name =ask("Give a name for your job", "job")
    que ="compute"
    nnodes =ask("How many nodes", "1")
    tpn =ask("How many taskts/node", "24")
    np = 0
    time =ask("What is the desired walltime ", "12:00:00")

def prt_comet_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    return """#!/bin/bash
#SBATCH -J {0}
#SBATCH -o job.o%j
#SBATCH -p {1}
#SBATCH --nodes={2}
#SBATCH --ntasks-per-node={3}
#SBATCH -t {4}
#SBATCH --mail-type=END
#SBATCH --mail-user=jmmshn@gmail.com

module swap mvapich2_ib openmpi_ib
cd $SLURM_SUBMIT_DIR
echo "****  submission time     TODAY"
echo "****  starting time       `date`"
ibrun $HOME/bin/VASP/vasp.{5}
echo "****  end time            `date`"
    """.format(name,que,nnodes,tpn,time,vasp_vers)

#################################################################
# Bridges
#################################################################

def ask_bridges():
    global name,que,nnodes,tpn,np,time
    name =ask("Give a name for your job", "job")
    que ="RM"
    nnodes =ask("How many nodes", "1")
    tpn =ask("How many taskts/node", "28")
    np = 0
    time =ask("What is the desired walltime ", "12:00:00")

def prt_bridges_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    return """#!/bin/bash
#SBATCH -J {0}
#SBATCH -o job.o%j
#SBATCH -p {1}
#SBATCH --nodes={2}
#SBATCH --ntasks-per-node={3}
#SBATCH -t {4}
#SBATCH --mail-type=END
#SBATCH --mail-user=jmmshn@gmail.com
set -x
cd $SLURM_SUBMIT_DIR
echo "****  submission time     TODAY" > vasp.out
echo "****  starting time       `date`" >> vasp.out
mpirun -n $SLURM_NTASKS $HOME/bin/VASP/vasp.{5} >> vasp.out
echo "****  end time            `date`" >> vasp.out
    """.format(name,que,nnodes,tpn,time,vasp_vers)

#################################################################
# Cori
#################################################################

def ask_cori():
    global name,que,nnodes,tpn,np,time
    name = ask("Give a name for your job", "job")
    que = ask("Which que", "regular")
    nnodes = ask("How many nodes", "1")
    tpn = ask("How many taskts/node", "32")
    np = int(nnodes)*int(tpn)
    time =ask("What is the desired walltime ", "12:00:00")

def prt_cori_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    return """#!/bin/bash
#SBATCH --job-name={0}
#SBATCH --output=job.o%j
#SBATCH --partition={1}
#SBATCH -C haswell
#SBATCH --nodes={2}
#SBATCH --mail-type=all
#SBATCH --mail-user=jmmshn@gmail.com
#SBATCH -L SCRATCH   #note: specify license need for the file 
#SBATCH --time={3}
#SBATCH --qos=premium

cd $SLURM_SUBMIT_DIR   # optional, since this is the default behavior

#always use the -c 2 if you want full nodes
srun -n {5} -c 2 ~/bin/VASP/vasp.{4}

    """.format(name,que,nnodes,time,vasp_vers,int(nnodes)*int(tpn))

#################################################################
# Guild
#################################################################

def ask_guild():
    global name,que,nnodes,tpn,np,time
    name =ask("Give a name for your job", "job")
    que = 'compute'
    nnodes =ask("How many nodes", "1")
    tpn =ask("How many taskts/node", "4")
    np =0
    time =ask("What is the desired walltime ", "48:00:00")

def prt_guild_sub(name,que,nnodes,tpn,np,time,vasp_vers):
    return """#!/bin/bash
#PBS -N {0}
#PBS -l nodes={1}:ppn={2}
#PBS -l walltime={3}
#PBS -j oe
#PBS -V

cd $PBS_O_WORKDIR
NCORES=`cat $PBS_NODEFILE | egrep -v '^#'\|'^$' | wc -l | awk '{{print $1}}'`
JOBID=`echo $PBS_JOBID | awk -F . '{{print $1}}'`
echo "+++  executing hostname  `hostname`" >>job.l$JOBID
echo "+++  $NCORES cores on" >>job.l$JOBID
uniq $PBS_NODEFILE >>job.l$JOBID
echo "+++  starting time       `date`" >>job.l$JOBID

source /usr/local/intel/composer_xe_2013.5.192/bin/compilervars.sh intel64
source /usr/local/intel/composer_xe_2013.5.192/mkl/bin/mklvars.sh intel64
export PATH=/usr/local/openmpi-1.6.4/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/openmpi-1.6.4/lib:$LD_LIBRARY_PATH

ulimit -s unlimited

/usr/local/openmpi-1.6.4/bin/mpirun -np $NCORES -machinefile $PBS_NODEFILE /home/vandewalle/codes/guild/VASP/vasp.{4}
    """.format(name,nnodes,tpn,time,vasp_vers)

    
####### Ask make dictionaries #######
ask_vals = {
        'optiplex' : ask_optiplex,
        'cori' : ask_cori,
        'comet' : ask_comet,
        'guild' : ask_guild,
        'bridges' : ask_bridges
        }
    
prt_script = {
        'optiplex' : prt_optiplex_sub,
        'cori' : prt_cori_sub,
        'comet' : prt_comet_sub,
        'guild' : prt_guild_sub,
        'bridges' : prt_bridges_sub
        }
####### Begin Main Program #######
    
hostname = chk_host(host_tags)
print "hostname: "+ hostname
vasp_vers=vers+'.'+hostname


print("""
---------------------------------------------------------------------------------------------
this creates a job script and submits it to the {0} on {1}
it does not change file locations or contents

* stampede has 16 cores per node
* the queues are development (2h) and (n)ormal (48h)
* using binary  $HOME/bin/vasp.{2}.{1}

""".format(sub_sys[hostname],hostname,vers))

f = open('submit.job', 'w')
ask_vals[hostname]()
jobscript=prt_script[hostname](name,que,nnodes,tpn,np,time,vasp_vers) 
#print prt_script[hostname](name,que,nnodes,tpn,np,time,vasp_vers) 
f.write(jobscript)
f.close()
dummy = ask('READY to submit','C-C to cancel')

if sub_sys[hostname] == 'SLURM':
  os.system ( "sbatch submit.job" )
if sub_sys[hostname] == 'PBS':
  os.system ( "qsub submit.job" )
