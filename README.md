# HPC-BENCHMARKING-SUITE
🚀 **HPC Cluster Benchmarking and Performance Engineering | HPL, OSU MPI & STREAM**

I’m excited to share a major milestone in my High-Performance Computing (HPC) engineering journey: building a two-node virtualized HPC cluster and implementing a benchmarking and performance evaluation framework using **Slurm, OpenMPI, and ReFrame**.

The objective was to go beyond infrastructure deployment and understand how computational performance, inter-node communication, and memory bandwidth affect HPC workloads.

### 🏗️ 1. HPC Infrastructure Overview

I configured a production-inspired virtual HPC environment using Oracle VirtualBox and Rocky Linux 9.8.

**Infrastructure specifications:**

- 1 Master node – cluster management and job scheduling.
- 2 Compute nodes – distributed workload execution.
- 2 vCPUs and 2 GB RAM per VM.
- VirtualBox Internal Network for inter-node communication.
- Slurm – workload scheduling and resource management.
- OpenMPI 5.0.10 – MPI communication.
- Lmod – software environment management.
- ReFrame 4.9.3 – benchmark orchestration, validation, and performance extraction.

The master node manages workload submission, while the two compute nodes execute distributed benchmark workloads.

### 📊 2. Benchmarking Results and Performance Analysis

I integrated three major HPC benchmarking workloads to evaluate different aspects of the cluster.

**A. HPL – High Performance Linpack**

HPL evaluates the floating-point computational capability of a system by solving a dense system of linear equations using distributed-memory parallelism.

The primary metric is GFLOPS (Giga Floating-Point Operations Per Second).

**Measured configuration:**
- Matrix size (N): 4,000
- Block size (NB): 128
- Process grid: 2 × 2
- MPI processes: 4
- Execution time: 14.96 seconds
- Performance: **2.8531 GFLOP/s**

What does this mean?

The cluster achieved approximately 2.85 billion floating-point operations per second during the HPL workload. This provides a baseline for evaluating computational throughput and the combined performance of CPU, BLAS, and MPI components.

**B. OSU MPI Micro-Benchmarks – Communication Performance**

OSU benchmarks evaluate MPI communication between distributed processes.

I implemented three workloads:

1. MPI Latency – measures communication delay in microseconds.
2. MPI Bandwidth – measures data-transfer throughput in MB/s.
3. MPI Allreduce – evaluates collective communication performance across MPI processes.

**Measured OSU results:**

| Metric | Measured result |
|---|---:|
| MPI Latency (1 byte) | 1,162.93 µs |
| MPI Latency (8 bytes) | 1,090.08 µs |
| MPI Bandwidth (1 MB) | 194.33 MB/s |
| MPI Allreduce (8 bytes) | 20,690.50 µs |

Interpretation:

- Latency indicates the time required for MPI communication.
- Bandwidth represents the data-transfer rate between MPI processes.
- Allreduce measures the cost of collective operations involving multiple processes.

The measurements provide insight into the communication overhead of the VirtualBox internal network and MPI execution environment.

The unusually high and variable latency and Allreduce measurements also highlight an area for further investigation, particularly MPI transport configuration, virtual network behavior, and process synchronization.

**C. STREAM – Memory Bandwidth Benchmark**

STREAM measures sustainable memory bandwidth through four operations:

- Copy – memory-to-memory data transfer.
- Scale – multiplication and memory transfer.
- Add – vector addition.
- Triad – combined multiplication and addition.

**Measured results:**

| Operation | Bandwidth |
|---|---:|
| Copy | 24,431.7 MB/s |
| Scale | 16,737.9 MB/s |
| Add | 16,511.7 MB/s |
| Triad | 33,094.4 MB/s |

The Triad result is particularly useful for evaluating memory bandwidth available to data-intensive scientific and HPC workloads.

These results represent the STREAM benchmark's reported best rates under the tested configuration.

### 🔍 3. What Do These Benchmarks Tell Us?

Each benchmark evaluates a different performance dimension:

- **HPL – Computational throughput:** How efficiently can the system perform floating-point calculations?
- **OSU Latency – Communication delay:** How quickly can MPI processes exchange messages?
- **OSU Bandwidth – Network throughput:** How efficiently can large messages be transferred?
- **OSU Allreduce – Collective communication:** How efficiently can multiple MPI processes coordinate and exchange results?
- **STREAM – Memory bandwidth:** How efficiently can the system move data between memory and the processor?

Together, these measurements provide a multidimensional view of HPC performance rather than relying on CPU specifications alone.

### ⚙️ 4. Benchmark Automation Using ReFrame

An important part of this project was automating the benchmarking workflow.

Instead of manually executing each benchmark, I integrated ReFrame with the Slurm scheduler.

The workflow:

1. Define benchmark test cases and resource requirements.
2. Load required software dependencies through Lmod.
3. Submit jobs through Slurm.
4. Execute workloads across allocated compute nodes.
5. Validate output using ReFrame sanity checks.
6. Extract performance metrics using performance functions.
7. Generate consolidated benchmark reports.

This creates a repeatable benchmarking workflow and provides a foundation for performance comparisons across different cluster configurations.

### 🎯 5. Key Engineering Learnings

This project helped me gain practical experience in:

- HPC cluster architecture and distributed computing.
- Slurm scheduling and resource allocation.
- MPI communication and process distribution.
- HPL, OSU MPI Micro-Benchmarks, and STREAM.
- ReFrame-based benchmarking automation.
- Understanding computational, communication, and memory bottlenecks.

**My next objective is to extend this framework with hardware discovery, automated resource selection, repeated-run performance analysis, and monitoring integration.**

The goal is to move beyond simply deploying an HPC infrastructure toward measuring, understanding, and engineering its performance.

