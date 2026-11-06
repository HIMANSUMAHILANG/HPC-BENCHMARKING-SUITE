site_configuration = {
    'systems': [
        {
            'name': 'mini-hpc',
            'descr': 'perform the basic benchmarking',
            'hostnames': ['.*'],
            'modules_system': 'lmod',
            'modules': ['gcc', 'mpi-5.0.10'],
            'partitions': [
                {
                    'name': 'master',
                    'descr': 'master node description',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['cluster-environment'],
                },
                {
                    'name': 'compute_node',
                    'descr': 'compute node description',
                    'scheduler': 'slurm',
                    'launcher': 'srun',
                    'access': ['--partition=High'],
                    'environs': ['cluster-environment'],
#                    'access' : ['partition=High','-n 4','-N 2','--ntasks-per-node=2','--cpus-per-task=1']
                },
                {
                    'name': 'compute_bulitin',
                    'descr': 'compute node system information',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['cluster-environment'],
                }
            ],
           'stagedir': '/mnt/shared/test35/hpc-reframe/stage',
           'outputdir': '/mnt/shared/test35/hpc-reframe/output',
           #'resourcesdir': [],
        }
    ],
    'environments': [
        {
            'name': 'cluster-environment',
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'modules': ['hpl', 'osu', 'stream', 'openblas', 'gcc/13.0', 'mpi-5.0.10']
#            'modules':[]
        }
    ]
}
