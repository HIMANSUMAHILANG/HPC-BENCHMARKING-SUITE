import reframe as rfm
import reframe.utility.sanity as sn

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
#    @sanity_function
    #def set_sanity(self):
        # 2. Make sure the benchmark ran, but you can also validate sysinfo here
     #   self.sanity_patterns = sn.all([
            #sn.assert_found(r'=== CPU INFO ===', self.stdout)
      #      sn.assert_found(self.stderr) # Confirms sysinfo printed
      #  ])
#        return sn.assert_found(r'== CPU INFO===',self.stdout)
 #   @sanity_function
#    def set_sanity(self):
        # Must return the pattern directly when using @sanity_function
  #      return sn.assert_found(r'=== CPU INFO ===', self.stdout)

#    @rfm.run_before('sanity')
#    @sanity_function
#    def set_sanity(self):
        # Assign to self.sanity_patterns, do not use return statement
#        self.sanity_patterns = sn.assert_found(r'=== CPU INFO ===', self.stdout)

#class osu(rfm.RunOnlyRegressionTest):
#	def __init__(self):
#        self.valid_systems = ['mini-hpc:compute:compute_node']
#	self.valid_prog_environs = ['cluster-environment']
#	self.modules = ['gcc','mpi-5.0.10']


#import reframe as rfm
#import reframe.utility.sanity as sn

#@rfm.simple_test
#class ComputeSysinfoAndBenchmark(rfm.RunOnlyRegressionTest):
 #   def __init__(self):
 #       self.valid_systems = ['mini-hpc:compute_node']
  #      self.valid_prog_environs = ['cluster-environment']
   #     self.modules = ['gcc','mpi-5.0.10']
#        self.executable = 'bash'
        # 1. Inject commands to dump system info into the job's stdout
        #self.prerun_cmds = [
            #'echo "=== HOSTNAME & KERNEL ==="',
            #'hostname && uname -a',
            #'echo "=== CPU INFO ==="',
            #'lscpu | grep -E "Model name|Core\(s\) per socket|Socket\(s\)|Thread\(s\) per core"',
           # 'echo "=== MEMORY INFO ==="',
          #  'free -h',
       # #    'echo "=== PROG ENVIRONMENT ==="',
        #    'module list'
      #  ]
     #   self.executable = 'echo "main code" '
    #@sanity_function
    #def validate_diagnostics(self):
        # 1. Define a list of deferred patterns to look for in stdout
        #checks = [
           # sn.assert_found(r'=== HOSTNAME & KERNEL ===', self.stdout),
            #sn.assert_found(r'Linux', self.stdout),  # Validates uname output format

         #   sn.assert_found(r'=== CPU INFO ===', self.stdout),
          #  sn.assert_found(r'Model name:', self.stdout),  # Validates lscpu output

        #    sn.assert_found(r'=== MEMORY INFO ===', self.stdout),
       #     sn.assert_found(r'Mem:', self.stdout),  # Validates free -h table header

      #      sn.assert_found(r'=== PROG ENVIRONMENT ===', self.stdout),
            # Note: "module list" output format varies by module system (Lmod vs Tcl environment modules).
            # If your module tool prints to stderr instead of stdout, look for it there.
#            sn.assert_found(r'Main test workload execution complete\.', self.stdout)
    #       sn.assert_found(r'Currently Loaded Modules:', self.stdout),
     #      sn.assert_found(r'main code',self.stdout)

   #     ]
  #      lmod_pattern = r'(Currently Loaded Modules|No modules loaded)'
 #       lmod_check = sn.assert_found(lmod_pattern, self.stderr)

        # 3. Combine stdout list assertions and append the single stderr assertion
#        all_checks = checks + [lmod_check]
        # 2. Combine all deferred assertions into a single deferred logical AND
#        return sn.all(all_checks)
#
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

