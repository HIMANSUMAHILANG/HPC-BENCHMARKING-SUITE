
import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import sanity_function


# =========================================================
# TEST 1: MASTER NODE HEALTH
# =========================================================

@rfm.simple_test
class MasterNodeHealth(rfm.RunOnlyRegressionTest):

    descr = "Check master CPU, RAM, Munge and Slurm controller"

    valid_systems = ["rocky_hpc:management"]
    valid_prog_environs = ["builtin"]

    executable = "bash"
    executable_opts = [
        "-c",
        r"""
        set -eu

        echo "MASTER=$(hostname -s)"

        CPU_COUNT=$(lscpu -p=CPU |
            awk '!/^#/ {count++} END {print count+0}')

        MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
        MEM_MB=$((MEM_KB / 1024))

        echo "CPU_COUNT=$CPU_COUNT"
        echo "MEMORY_MB=$MEM_MB"

        test "$CPU_COUNT" -ge 2
        test "$MEM_MB" -ge 1500

        systemctl is-active --quiet munge
        echo "MUNGE_OK"

        systemctl is-active --quiet slurmctld
        echo "SLURMCTLD_OK"

        echo "MASTER_HEALTH_OK"
        """
    ]

    @sanity_function
    def validate(self):
        return sn.assert_found(
            r"MASTER_HEALTH_OK",
            self.stdout
        )


# =========================================================
# TEST 2: COMPUTE NODE HEALTH
# =========================================================

@rfm.simple_test
class ComputeNodeHealth(rfm.RunOnlyRegressionTest):

    descr = "Check CPU and RAM on both compute nodes"

    valid_systems = ["rocky_hpc:compute"]
    valid_prog_environs = ["builtin"]

    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    time_limit = "2m"

    executable = "bash"
    executable_opts = [
        "-c",
        r"""
        set -eu

        NODE=$(hostname -s)

        CPU_COUNT=$(lscpu -p=CPU |
            awk '!/^#/ {count++} END {print count+0}')

        MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
        MEM_MB=$((MEM_KB / 1024))

        echo "NODE=$NODE"
        echo "CPU_COUNT=$CPU_COUNT"
        echo "MEMORY_MB=$MEM_MB"

        case "$NODE" in
            compute1|compute2) ;;
            *)
                echo "UNEXPECTED_NODE=$NODE"
                exit 1
                ;;
        esac

        test "$CPU_COUNT" -ge 2
        test "$MEM_MB" -ge 1500

        echo "NODE_HEALTH_OK"
        """
    ]

    @sanity_function
    def validate(self):
        return sn.assert_eq(
            sn.count(sn.findall(r"NODE_HEALTH_OK", self.stdout)),
            2
        )


# =========================================================
# TEST 3: TWO-NODE SLURM JOB
# =========================================================

@rfm.simple_test
class SlurmTwoNodeTest(rfm.RunOnlyRegressionTest):

    descr = "Verify job execution on compute1 and compute2"

    valid_systems = ["rocky_hpc:compute"]
    valid_prog_environs = ["builtin"]

    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    time_limit = "2m"

    executable = "bash"
    executable_opts = [
        "-c",
        r"""
        set -eu

        echo "TASK_ID=$SLURM_PROCID"
        echo "NODE=$(hostname -s)"
        echo "JOB_ID=$SLURM_JOB_ID"

        case "$(hostname -s)" in
            compute1|compute2) ;;
            *)
                echo "UNEXPECTED_NODE"
                exit 1
                ;;
        esac

        echo "SLURM_TASK_OK"
        """
    ]

    @sanity_function
    def validate(self):
        return sn.assert_eq(
            sn.count(sn.findall(r"SLURM_TASK_OK", self.stdout)),
            2
        )


# =========================================================
# TEST 4: SHARED FILESYSTEM CROSS-NODE TEST
# =========================================================

@rfm.simple_test
class SharedFilesystemTest(rfm.RunOnlyRegressionTest):

    descr = "Verify cross-node shared filesystem visibility"

    valid_systems = ["rocky_hpc:compute"]
    valid_prog_environs = ["builtin"]

    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    time_limit = "3m"

    # Change this to your actual shared NFS mount.
    shared_path = "/mnt/shared"

    executable = "bash"
    executable_opts = [
        "-c",
        r"""
        set -eu

        SHARED_PATH="/home"
        JOB_ID="$SLURM_JOB_ID"
        TASK_ID="$SLURM_PROCID"

        FILE="$SHARED_PATH/.reframe_${JOB_ID}_${TASK_ID}"

        echo "NODE=$(hostname -s)"
        echo "SHARED_PATH=$SHARED_PATH"

        test -d "$SHARED_PATH"

        touch "$FILE"

        # Wait until both tasks' files are visible.
        FOUND=0

        for attempt in $(seq 1 20); do
            if [ -f "$SHARED_PATH/.reframe_${JOB_ID}_0" ] &&
               [ -f "$SHARED_PATH/.reframe_${JOB_ID}_1" ]; then
                FOUND=1
                break
            fi
            sleep 1
        done

        if [ "$FOUND" -ne 1 ]; then
            echo "SHARED_VISIBILITY_FAILED"
            exit 1
        fi

        rm -f "$FILE"

        echo "SHARED_FS_OK"
        """
    ]

    @sanity_function
    def validate(self):
        return sn.assert_eq(
            sn.count(sn.findall(r"SHARED_FS_OK", self.stdout)),
            2
        )

