import reframe as rfm
import reframe.utility.sanity as sn
import os
from reframe.core.builtins import sanity_function
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
            #sn.assert_found(r'Model name', self.stdout),
            sn.assert_found(r'Mem:', self.stdout)
        ])

@rfm.simple_test
class HPLBenchmark(rfm.RunOnlyRegressionTest):

    descr = 'Fixed Multi-Node MPI HPL Test'

    # System and programming environment
    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    # Slurm resource allocation
   # num_nodes = 2
    num_tasks = 2
    num_tasks_per_node = 2
    num_cpus_per_task = 1
    num_nodes = 2
#    stdout = 'hpl_output.log'
 #   stderr = 'hpl_error.log'
    # HPL application
   # sourcesdir = '/apps/packages/hpl/hpl-2.3/bin/Linux_Rocky9'
    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'
    executable = 'xhpl'

    # Stage HPL input file
    readonly_files = ['HPL.dat']

    # Prevent CPU oversubscription
    env_vars = {
        'OMP_NUM_THREADS': '1',
        'OPENBLAS_NUM_THREADS': '1',
        'MKL_NUM_THREADS': '1'
    }

    # Validate HPL execution
    @run_before('run')
    def prepare_hpl(self):

        self.executable_opts = []

        self.job.options += [
            '--distribution=block:block',
            '--cpu-bind=cores'
        ]

    @sanity_function
    def validate_hpl(self):

        return sn.all([
            sn.assert_found(r'PASSED', self.stdout),
            sn.assert_not_found(r'HPL ERROR', self.stdout)
        ])
