import os
import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import (
    fixture,
    sanity_function,
    performance_function,
    run_before,
    run_after
)


# ---------------------------------------------------------
# 1. STREAM compilation test
# ---------------------------------------------------------
'''
class build_stream(rfm.CompileOnlyRegressionTest):

    descr = 'Compile STREAM with OpenMP support'

    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    build_system = 'SingleSource'
    sourcesdir = '/home/himan/hpc-reframe/input'
    sourcepath = 'stream.c'
    executable = './stream.x'

    modules = ['gcc','mpi-5.0.10']

    @run_before('compile')
    def prepare_build(self):

        omp_flag = self.current_environ.extras.get(
            'omp_flag', '-fopenmp'
        )

        self.build_system.cflags = [
            '-O3',
            omp_flag
        ]
'''

# ---------------------------------------------------------
# 2. STREAM execution test using Slurm
# ---------------------------------------------------------

@rfm.simple_test
class stream_test(rfm.RunOnlyRegressionTest):

    descr = 'STREAM memory bandwidth benchmark using Slurm'

    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']
    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'
    sourcepath = 'stream'
    executable = './stream'
    # Reuse the compiled STREAM executable
#    stream_binary = fixture(
#        sourcepath,
#        scope='environment'
 #   )

    # Slurm resource allocation
    num_nodes = 1
    num_tasks = 1
    num_tasks_per_node = 2
    num_cpus_per_task = 1
#    num_nodelist=compute2
#    time_limit = '00:05:00'

    # OpenMP configuration
    env_vars = {
        'OMP_NUM_THREADS': '2',
        'OMP_PROC_BIND': 'close',
        'OMP_PLACES': 'cores'
    }

    @run_after('setup')
    def set_executable(self):

        self.executable = os.path.join(
            self.sourcesdir,
            'stream'
        )

    # -----------------------------------------------------
    # Sanity validation
    # -----------------------------------------------------

    @sanity_function
    def validate(self):

        return sn.assert_found(
            r'Solution Validates',
            self.stdout
        )

    # -----------------------------------------------------
    # Performance evaluation
    # -----------------------------------------------------

    @performance_function('MB/s')
    def copy_bw(self):

        return sn.extractsingle(
            r'Copy:\s+(\S+)',
            self.stdout,
            1,
            float
        )

    @performance_function('MB/s')
    def scale_bw(self):

        return sn.extractsingle(
            r'Scale:\s+(\S+)',
            self.stdout,
            1,
            float
        )

    @performance_function('MB/s')
    def add_bw(self):

        return sn.extractsingle(
            r'Add:\s+(\S+)',
            self.stdout,
            1,
            float
        )

    @performance_function('MB/s')
    def triad_bw(self):

        return sn.extractsingle(
            r'Triad:\s+(\S+)',
            self.stdout,
            1,
            float
        )
