import reframe as rfm
import reframe.utility.sanity as sn
import os
from reframe.core.builtins import sanity_function
from reframe.core.builtins import (
    run_before,
    run_after,
    sanity_function,
    performance_function
)


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

    # -------------------------------------------------
    # 1. BASIC CONFIGURATION
    # -------------------------------------------------

    descr = 'HPL benchmark on two-node Slurm cluster'

    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    maintainers = ['test35']

    # -------------------------------------------------
    # 2. BENCHMARK CONFIGURATION
    # -------------------------------------------------

    executable = 'xhpl'

    num_nodes = 2
    num_tasks = 4
    num_tasks_per_node = 2
    num_cpus_per_task = 1

#    time_limit = '00:10:00'

    # HPL input configuration
    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'
    readonly_files = ['HPL.dat']
    env_vars = {
        'OMPI_MCA_btl_tcp_if_include': 'enp0s8'
    }
    keep_files = ['HPL.out']


    # -------------------------------------------------
    # 3. ENVIRONMENT PREPARATION
    # -------------------------------------------------

    @run_before('run')
    def prepare_environment(self):

        self.prerun_cmds = [
            'echo "======================================"',
            'echo "        HPL BENCHMARK START           "',
            'echo "======================================"',

            'echo "===== SLURM JOB INFORMATION ====="',
            'echo "JOB ID: $SLURM_JOB_ID"',
            'echo "JOB NODELIST: $SLURM_JOB_NODELIST"',
            'echo "NUMBER OF NODES: $SLURM_JOB_NUM_NODES"',
            'echo "NUMBER OF TASKS: $SLURM_NTASKS"',
            'echo "TASKS PER NODE: $SLURM_TASKS_PER_NODE"',

            'echo "===== NODE INFORMATION ====="',
            'srun hostname',

            'echo "===== SOFTWARE ENVIRONMENT ====="',
            'module list 2>&1',
            'which xhpl',
            'ldd "$(which xhpl)"',

            'echo "===== HPL INPUT CONFIGURATION ====="',
            'test -r HPL.dat',
            'ls -lh HPL.dat',
            'cat HPL.dat',

            'echo "===== STARTING HPL EXECUTION ====="'
        ]

    # -------------------------------------------------
    # 4. EXECUTION CONFIGURATION
    # -------------------------------------------------

    @run_before('run')
    def configure_execution(self):
        self.job.launcher.options = ['--mpi=pmix_v3']
        self.executable_opts = []

#        self.job.options += [
#            '--distribution=block:block',
#            '--cpu-bind=cores'
#        ]

    # -------------------------------------------------
    # 5. POST-RUN OUTPUT COLLECTION
    # -------------------------------------------------

    @run_after('run')
    def collect_hpl_output(self):

        self.postrun_cmds += [
            'echo "===== HPL OUTPUT FILE ====="',
            'if [ -f HPL.out ]; then cat HPL.out; else echo "HPL.out not generated"; fi',

            'echo "===== HPL EXECUTION FINISHED ====="',
            'echo "JOB ID: $SLURM_JOB_ID"',
            'date'
        ]

    # -------------------------------------------------
    # 6. SANITY VALIDATION
    # -------------------------------------------------

    @sanity_function
    def validate_hpl(self):

        return sn.all([

            sn.assert_found(
                r'End of Tests.',
                self.stdout
            ),

            sn.assert_found(
                r'PASSED',
                self.stdout
            )
        ])

    # -------------------------------------------------
    # 7. PERFORMANCE EXTRACTION
    # -------------------------------------------------

    @performance_function('Gflop/s')
    def gflops(self):

        return sn.extractsingle(
            r'WR\w+\s+\d+\s+\d+\s+\d+\s+\d+'
            r'\s+[\d.eE+-]+\s+([\d.eE+-]+)',
            self.stdout,
            1,
            float
        )




