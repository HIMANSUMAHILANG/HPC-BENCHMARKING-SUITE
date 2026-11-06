import reframe as rfm
import reframe.utility.sanity as sn
import os
@rfm.simple_test
class SysinfoAndBenchmark(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['mini-hpc:master']
        self.valid_prog_environs = ['cluster-environment']
        self.modules = ['gcc','mpi-5.0.10']
#        self.executable = 'bash'
        # 1. Inject commands to dump system info into the job's stdout
        self.prerun_cmds = [
            'echo "=== HOSTNAME & KERNEL ==="',
            'hostname && uname -a',
            'echo "=== CPU INFO ==="',
            'lscpu | grep -E "Model name|Core\(s\) per socket|Socket\(s\)|Thread\(s\) per core"',
            'echo "=== MEMORY INFO ==="',
            'free -h',
            'echo "=== PROG ENVIRONMENT ==="',
            'module list'
        ]
        self.executable = 'echo "main code" '
    @sanity_function
    def validate_diagnostics(self):
        # 1. Define a list of deferred patterns to look for in stdout
        checks = [
            sn.assert_found(r'=== HOSTNAME & KERNEL ===', self.stdout),
            sn.assert_found(r'Linux', self.stdout),  # Validates uname output format
            
            sn.assert_found(r'=== CPU INFO ===', self.stdout),
            sn.assert_found(r'Model name:', self.stdout),  # Validates lscpu output
            
            sn.assert_found(r'=== MEMORY INFO ===', self.stdout),
            sn.assert_found(r'Mem:', self.stdout),  # Validates free -h table header
            
            sn.assert_found(r'=== PROG ENVIRONMENT ===', self.stdout),
            # Note: "module list" output format varies by module system (Lmod vs Tcl environment modules).
            # If your module tool prints to stderr instead of stdout, look for it there.
#            sn.assert_found(r'Main test workload execution complete\.', self.stdout)
           #sn.assert_found(r'Currently Loaded Modules:', self.stdout),
           #sn.assert_found(r'main code',self.stdout)

        ]
#        lmod_pattern = r'(Currently Loaded Modules|No modules loaded)'
#        lmod_check = sn.assert_found(lmod_pattern, self.stdout)

        # 3. Combine stdout list assertions and append the single stderr assertion
        all_checks = checks
        # 2. Combine all deferred assertions into a single deferred logical AND

        return sn.all(all_checks)

#this are the compute node details

@rfm.simple_test
class DirectComputeNodeTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        # 1. Target the local scheduler partition
        self.valid_systems = ['mini-hpc:compute_bulitin']
        self.valid_prog_environs = ['cluster-environment']
        
        # Define the target compute node hostname
        compute_node = 'compute1' 
        
        # 2. Set the executable to bash, and pass the command via SSH
        self.executable = 'ssh'
        self.executable_opts = [
            compute_node, 
            '"hostname && lscpu | grep \'Model name\' && free -h"'
        ]

    @sanity_function
    def set_sanity(self):
        # 3. Confirm the output contains data from the compute node
        return sn.all([
            sn.assert_found(r'Model name', self.stdout),
            sn.assert_found(r'Mem:', self.stdout)
        ])

@rfm.simple_test
class HPLBenchmark(rfm.RunOnlyRegressionTest):
    def __init__(self):
        #self.valid_systems = ['mini-hpc:compute_node']
        #self.valid_prog_environs = ['cluster-environment']
        self.valid_systems = ['*']
        self.valid_prog_environs=['*']
#=====slurm configuration
        self.scheduler = 'slurm'
        self.launcher = 'srun'
#        self.sourcesdir = '/apps/packages/hpl/hpl-2.3/bin/Linux_Rocky9'
#        self.binaries = fixture(binary_path,scope='environment')
        self.num_nodes = 2
        self.num_cpus_per_task = 1
        self.num_tasks = 4
        self.num_tasks_per_node = 2
        self.launcher_options = [
            '--ntasks-per-node=2',
            '--ntasks=2',
            '--cpu-bind=cores'
        ]
#        self.time_limit = '1hr'
        self.modules = ['gcc/13.0','openblas','mpi-5.0.10','hpl']
        self.readonly = ['HPL.dat']
        #self.executable = f'{sourcesdir}/xhpl'
 #       self.executable = ['xhpl']
        shared_mount_path = '/apps/packages/hpl/hpl-2.3/bin/Linux_Rocky9'
        
        # Point sourcesdir to the shared folder. ReFrame will use this as its run directory.
        self.sourcesdir = shared_mount_path
        
        # Because sourcesdir is set to the shared path, ReFrame drops into this folder.
        # If 'xhpl' is in the exact same folder, just write './xhpl'. 
        # If it is inside a 'bin' folder there, write './bin/xhpl'.
        self.executable = './xhpl'
        self.sanity_patterns = sn.all([
            sn.assert_found(r'End of Tests.', self.stdout),
            sn.assert_found(r'passed', self.stdout)
        ])

        # 6. Performance Extraction (Grabs GFLOPS from HPL output table)
        self.perf_patterns = {
            'gflops': sn.extractsingle(
                r'WR\w+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\.\d+\s+(?P<gflops>\d+\.\d+e?[+-]?\d*)',
                self.stdout, 'gflops', float
            )
        }
        
        # Reference metric (adjust baseline values based on your CPU specs)
        self.reference = {
            '*': {
                'gflops': (0.0, None, None, 'GFLOPS')
            }
        }
