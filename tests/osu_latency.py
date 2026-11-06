import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import (
    run_before,
    sanity_function,
    performance_function
)


@rfm.simple_test
class OSULatencyBenchmark(rfm.RunOnlyRegressionTest):

    valid_systems = ['mini-hpc:compute_node']
    valid_prog_environs = ['cluster-environment']

    # Two nodes, one MPI rank per node
    num_nodes = 2
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

#    time_limit = '00:05:00'

#    modules = [
#        'gcc/13.0',
#        'mpi-5.0.10'
#    ]

    executable = 'osu_latency'

    env_vars = {
        'OMPI_MCA_btl_tcp_if_include': 'enp0s8'
    }

    @run_before('run')
    def configure_slurm_launcher(self):
        self.job.launcher.options = ['--mpi=pmix_v3']

    @sanity_function
    def validate_latency(self):
        return sn.assert_found(
            r'(?m)^\s*0\s+[\d.]+',
            self.stdout
        )

    @performance_function('us')
    def latency_zero_bytes(self):
        return sn.extractsingle(
            r'(?m)^\s*0\s+([\d.]+)\s*$',
            self.stdout,
            1,
            float
        )
