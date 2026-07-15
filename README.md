# Low-Level Linux Kernel Process Monitor (eBPF Instrumentation)

A high-performance, near-zero overhead system monitoring utility that hooks directly into the Linux kernel space using Extended Berkeley Packet Filter (eBPF) technology.

## 🚀 Architectural Overview
Rather than relying on resource-heavy user-space polling mechanisms (like repeatedly scraping `/proc`), this utility compiles a sandboxed C program on-the-fly via the BCC framework and injects it straight into the kernel's `sys_clone` layer. 

Whenever a new process or thread is spawned across the operating system:
1. The kernel-level kprobe catches the execution context.
2. Safe kernel helper functions (`bpf_get_current_comm`) pull execution data.
3. Metadata is transferred instantly to user-space via a highly optimized ring buffer (`BPF_PERF_OUTPUT`).

## 🛠️ Prerequisites
- Linux Kernel 5.x+ with BPF capabilities enabled (Or WSL2 running a modern kernel backend)
- BCC Development Framework (`bpfcc-tools`, `python3-bpfcc`)

## 💻 How to Run
Execute with administrative privileges to allow safe kernel instruction insertion:
```bash
sudo python3 kernel_monitor.py
```

