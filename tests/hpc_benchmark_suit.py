import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import (
    run_before,
    run_after,
    sanity_function,
    performance_function
)


# ============================================================
# PARENT CLASS: COMMON HPC CONFIGURATION
# ============================================================

class HPCBenchmarkBase(rfm.RunOnlyRegressionTest):

    """
    Common configuration inherited by all HPC benchmark tests.

    Responsibilities:
        - Common programming environment
        - Common software dependencies
        - MPI network configuration
        - Slurm PMIx configuration
        - Common job configuration
    """

    valid_prog_environs = ['cluster-environment']

    # Default dependencies for MPI benchmarks.
    # Child tests can override this list.

    # Default resource configuration.
   # time_limit = '00:10:00'

    # MPI communication network.
    env_vars = {
        'OMPI_MCA_btl_tcp_if_include': 'enp0s8'
    }

    # Common Slurm launcher configuration.
    @run_before('run')
    def configure_slurm_launcher(self):

        self.job.launcher.options = [
            '--mpi=pmix_v3'
        ]

    # Common job information.
    @run_before('run')
    def print_job_information(self):

        self.prerun_cmds += [
            'echo "========================================"',
            'echo "          HPC BENCHMARK START            "',
            'echo "========================================"',
            'echo "JOB ID: $SLURM_JOB_ID"',
            'echo "JOB NODELIST: $SLURM_JOB_NODELIST"',
            'echo "NUMBER OF NODES: $SLURM_JOB_NUM_NODES"',
            'echo "NUMBER OF TASKS: $SLURM_NTASKS"',
            'echo "TASKS PER NODE: $SLURM_TASKS_PER_NODE"',
            'echo "========================================"'
        ]

    # Common completion information.
    @run_after('run')
    def print_completion_information(self):

        self.postrun_cmds += [
            'echo "========================================"',
            'echo "       HPC BENCHMARK COMPLETED           "',
            'echo "========================================"',
            'echo "JOB ID: $SLURM_JOB_ID"',
            'date'
        ]


# ============================================================
# TEST 1: MASTER NODE SYSTEM INFORMATION
# ============================================================

@rfm.simple_test
class MasterNodeSysinfo(HPCBenchmarkBase):

    descr = 'Collect master node hardware and software information'

    valid_systems = ['mini-hpc:master']

    num_nodes = 1
    num_tasks = 1
    num_tasks_per_node = 1

    executable = 'hostname'

    prerun_cmds = [
        'echo "========== HOSTNAME AND KERNEL =========="',
        'hostname',
        'uname -a',

        'echo "========== CPU INFORMATION =========="',
        'lscpu | grep -E "Model name|Core\\(s\\) per socket|Socket\\(s\\)|Thread\\(s\\) per core"',

        'echo "========== MEMORY INFORMATION =========="',
        'free -h',

        'echo "========== NETWORK INFORMATION =========="',
        'ip -brief address',

        'echo "========== SOFTWARE ENVIRONMENT =========="',
        'module list 2>&1'
    ]

    @sanity_function
    def validate_master_information(self):

        return sn.all([
            sn.assert_found(r'Linux', self.stdout),
            sn.assert_found(r'Model name', self.stdout),
            sn.assert_found(r'Mem:', self.stdout),
            sn.assert_found(r'HOSTNAME AND KERNEL', self.stdout)
        ])


# ============================================================
# TEST 2: COMPUTE NODE SYSTEM INFORMATION
# ============================================================

@rfm.simple_test
class ComputeNodeSysinfo(HPCBenchmarkBase):

    descr = 'Collect compute node hardware and software information'

    valid_systems = ['mini-hpc:compute_node']

    num_nodes = 1
    num_tasks = 1
    num_tasks_per_node = 1

    executable = 'hostname'

    prerun_cmds = [
        'echo "========== COMPUTE NODE INFORMATION =========="',
        'hostname',
        'uname -a',

        'echo "========== CPU INFORMATION =========="',
        'lscpu | grep -E "Model name|Core\\(s\\) per socket|Socket\\(s\\)|Thread\\(s\\) per core"',

        'echo "========== MEMORY INFORMATION =========="',
        'free -h',

        'echo "========== NETWORK INFORMATION =========="',
        'ip -brief address',

        'echo "========== SOFTWARE ENVIRONMENT =========="',
        'module list 2>&1'
    ]

    @sanity_function
    def validate_compute_information(self):

        return sn.all([
            sn.assert_found(r'Linux', self.stdout),
            sn.assert_found(r'Model name', self.stdout),
            sn.assert_found(r'Mem:', self.stdout),
            sn.assert_found(r'COMPUTE NODE INFORMATION', self.stdout)
        ])


# ============================================================
# TEST 3: HPL BENCHMARK
# ============================================================

@rfm.simple_test
class HPLBenchmark(HPCBenchmarkBase):

    descr = 'HPL benchmark on a two-node Slurm cluster'

    valid_systems = ['mini-hpc:compute_node']

    num_nodes = 2
    num_tasks = 4
    num_tasks_per_node = 2
    num_cpus_per_task = 1

   # time_limit = '00:10:00'

    sourcesdir = '/mnt/shared/test35/hpc-reframe/input'

    executable = './xhpl'

    keep_files = ['HPL.out']

    @run_before('run')
    def prepare_hpl(self):

        self.prerun_cmds += [

            'echo "========== HPL SOFTWARE =========="',
            'module list 2>&1',
            'which xhpl',
            'ldd "$(which xhpl)"',

            'echo "========== HPL INPUT =========="',
            'test -r HPL.dat',
            'ls -lh HPL.dat',
            'cat HPL.dat',

            'echo "========== HPL NODE ALLOCATION =========="',
            'srun hostname',

            'echo "========== STARTING HPL =========="'
        ]

        self.executable_opts = []

    @run_after('run')
    def collect_hpl_output(self):

        self.postrun_cmds += [
            'echo "========== HPL OUTPUT FILE =========="',
            'if [ -f HPL.out ]; then cat HPL.out; else echo "HPL.out not generated"; fi'
        ]

    @sanity_function
    def validate_hpl(self):

        return sn.all([
            sn.assert_found(r'End of Tests.', self.stdout),
            sn.assert_found(r'PASSED', self.stdout)
        ])

    @performance_function('Gflop/s')
    def hpl_performance(self):

        return sn.extractsingle(
            r'WR\w+\s+\d+\s+\d+\s+\d+\s+\d+'
            r'\s+[\d.eE+-]+\s+([\d.eE+-]+)',
            self.stdout,
            1,
            float
        )


# ============================================================
# TEST 4: OSU LATENCY
# ============================================================

@rfm.simple_test
class OSULatency(HPCBenchmarkBase):

    descr = 'OSU MPI point-to-point latency benchmark'

    valid_systems = ['mini-hpc:compute_node']

    num_nodes = 2
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    executable = 'osu_latency'

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


# ============================================================
# TEST 5: OSU BANDWIDTH
# ============================================================

@rfm.simple_test
class OSUBandwidth(HPCBenchmarkBase):

    descr = 'OSU MPI point-to-point bandwidth benchmark'

    valid_systems = ['mini-hpc:compute_node']

    num_nodes = 2
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    executable = 'osu_bw'

    @sanity_function
    def validate_bandwidth(self):

        return sn.assert_found(
            r'(?m)^\s*1048576\s+[\d.]+',
            self.stdout
        )

    @performance_function('MB/s')
    def bandwidth_1mb(self):

        return sn.extractsingle(
            r'(?m)^\s*1048576\s+([\d.]+)',
            self.stdout,
            1,
            float
        )


# ============================================================
# TEST 6: OSU ALLREDUCE
# ============================================================

@rfm.simple_test
class OSUAllreduce(HPCBenchmarkBase):

    descr = 'OSU MPI collective Allreduce benchmark'

    valid_systems = ['mini-hpc:compute_node']

    num_nodes = 2
    num_tasks = 4
    num_tasks_per_node = 2
    num_cpus_per_task = 1

    executable = 'osu_allreduce'

    @sanity_function
    def validate_allreduce(self):

        return sn.assert_found(
            r'(?m)^\s*8\s+[\d.]+',
            self.stdout
        )

    @performance_function('us')
    def allreduce_latency_8bytes(self):

        return sn.extractsingle(
            r'(?m)^\s*8\s+([\d.]+)',
            self.stdout,
            1,
            float
        )


# ============================================================
# TEST 7: STREAM BENCHMARK
# ============================================================

@rfm.simple_test
class STREAMBenchmark(HPCBenchmarkBase):

    descr = 'STREAM memory bandwidth benchmark'

    valid_systems = ['mini-hpc:compute_node']

    # STREAM is an OpenMP benchmark, not an MPI benchmark.
    modules = [
        'gcc/13.0'
    ]

    # No MPI-specific environment required.
    env_vars = {}

    num_nodes = 2
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 2

    executable = './stream'

    prerun_cmds = [
        'export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}',
        'echo "STREAM THREADS: $OMP_NUM_THREADS"',
        'echo "STREAM NODE: $(hostname)"'
    ]

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
