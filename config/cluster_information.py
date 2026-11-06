site_configuratio={
	'systems':[
		{
			'name' : 'mini-hpc',
			'descr' : 'perform the basic benchmarking',
			'hostname': ['*'],
			'modules_system':'lmod',
			'modules':['gcc','mpi-5.0.10'],
			'partitions':[
				{
					'name' : 'master',
					'descr' : 'master node description',
					'scheduler' : 'local',
					'launcher' : 'local',
				},
				{
					'name' : 'compute_node',
					'descr' : ' compute node description',
					'scheduler' : 'slurm',
					'launcher' : 'srun',
					'access' : [ '--partition=High'],
					'environs': ['builtin'],

				},
				{
					'name' : 'compute_bulitin',
					'descr' : 'compute node system information',
					'scheduler': 'local',
					'launcher': 'local',
				}


			]


		}



	],
'environments':[
	{
		'name': 'builtin',
		'cc' : 'gcc',
		'cxx' : 'g++',
		'ftn' : 'gfortan',
		'modules':['hpl','osu','stream','openblas','gcc/13.0','mpi-5.0.10']
	}
	]
#''
}
