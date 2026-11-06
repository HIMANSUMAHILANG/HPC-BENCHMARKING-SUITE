
site_configuration = {
    "systems": [
        {
            "name": "rocky_hpc",
            "descr": "Rocky Linux 9.8 virtual HPC cluster",

            # ReFrame is launched from the master node.
            "hostnames": [".*"],

            "partitions": [

                # Local tests executed on the master.
                {
                    "name": "management",
                    "descr": "Master node local testing",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["builtin"],
                    "max_jobs": 1
                },

                # Slurm tests executed on compute nodes.
                {
                    "name": "compute",
                    "descr": "Two-node Slurm partition",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--partition=High"
                    ],
                    "environs": ["builtin"],
                    "max_jobs": 1
                }
            ]
        }
    ],

    "environments": [
        {
            "name": "builtin",
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran"
        }
    ]
}

