
import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HPLBenchmark(rfm.RunOnlyRegressionTest):

    # Target cluster and programming environment
    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    # HPL execution configuration
    descr = 'HPL distributed-memory benchmark using OpenMPI'

    num_nodes = 2
    num_tasks = 4
    num_tasks_per_node = 2
    num_cpus_per_task = 1
    launcher_options = [
            '--mca oob_tcp_if_include enp0s8',
            '--mca btl_tcp_if_include enp0s8'
        ]
    # HPL executable provided by Lmod
    executable = 'xhpl'

    # Shared HPL configuration file
    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'
#    readonly_files = ['HPL.dat']
    hpl_dat = '/mnt/shared/test35/hpc-reframe/input/HPL.dat'

    # Benchmark parameters
#    time_limit = '00:10:00'

    @run_before('run')
    def prepare_hpl(self):

        # Make shared HPL.dat available in the job working directory
        self.prerun_cmds = [
            f'ln -sf {self.hpl_dat} HPL.dat'
        ]

        # Set MPI execution environment
        self.env_vars['OMP_NUM_THREADS'] = '1'

    @sanity_function
    def validate_hpl(self):

        # HPL must complete successfully
        sn.assert_found(r'PASSED', self.stdout)

        return sn.assert_found(
            r'Finished',
            self.stdout
        )

    @performance_function('GFlop/s')
    def hpl_performance(self):

        # Extract the final GFLOPS value from the HPL result row
        return sn.extractsingle(
            r'(?m)^\s*\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+[\d.]+\s+([\d.]+)\s*$',
            self.stdout,
            1,
            float
        )
