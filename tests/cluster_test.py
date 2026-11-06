import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import sanity_function

# define the first system check configuration of the system and cluster

@rfm.simple_test
class systeminformation(rfm.RunOnlyRegressionTest):
	descr = "check the systemc inforamation of the master and compute nodes"
	valid_systems = ['mini-hpc:master']
#	valid_prog_environs = ['builtin']
#	executable = 'bash'
	prerun_cmds = [
			'echo "Master=$(hostname -s)"'
			"cpu_count=$(lscpu -p=CPU | awk '!/^#/{count++} END {print count+0}')"
			"MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
			'MEM_MB=$((MEM_KB / 1024))'
			'echo "CPU_COUNT=$CPU_COUNT"'
			'echo "MEMORY_MB=$MEM_MB"'
			'test "$CPU_COUNT" -ge 2'
			'test "$MEM_MB" -ge 1500'
			'systemctl is-active --quiet munge'
			'echo "MUNGE_OK"'
			'systemctl is-active --quiet slurmctld'
			'echo "SLURMCTLD_OK"'
			'echo "MASTER_HEALTH_OK"'


]

	def set_sanity(self):
        # 2. Make sure the benchmark ran, but you can also validate sysinfo here
		self.sanity_patterns = sn.all([
		sn.assert_found(r'# OSU MPI Latency Test', self.stdout),
		sn.assert_found(r'=== CPU INFO ===', self.stdout) # Confirms sysinfo printed 
])
