import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import (
    run_before,
    sanity_function,
    performance_function
)


@rfm.simple_test
class HPLBenchmark(rfm.RunOnlyRegressionTest):

    # ReFrame system and programming environment
    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    # Slurm resource requirements
    num_nodes = 2
    num_tasks = 4
    num_tasks_per_node = 2
    num_cpus_per_task = 1

  #  time_limit = '00:10:00'
    exclusive_access = True

    # Software stack
 #   modules = [
 #       'gcc/13.0',
 #       'mpi-5.0.10',
 #       'openblas',
 #       'hpl'
  #  ]

    # ReFrame stages these input files into the test directory.
    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'

    # HPL executable
    executable = './xhpl'

    # OpenMPI TCP interface configuration
    env_vars = {
        'OMPI_MCA_btl_tcp_if_include': 'enp0s8'
    }

    # Keep HPL output file after test completion
    keep_files = ['HPL.out']

    @run_before('run')
    def configure_slurm_launcher(self):
        # ReFrame already creates the srun command.
        # Add the PMIx plugin option to that command.
        self.job.launcher.options = ['--mpi=pmix_v3']

    @sanity_function
    def validate_hpl(self):
        return sn.assert_found(
            r'End of Tests.',
            self.stdout
        )

    @performance_function('GFlop/s')
    def hpl_performance(self):
        return sn.extractsingle(
            r'(?m)^\s*WR\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+'
            r'[\d.Ee+-]+\s+([\d.Ee+-]+)\s*$',
            self.stdout,
            1,
            float
        )
