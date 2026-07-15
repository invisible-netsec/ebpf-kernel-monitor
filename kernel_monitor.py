#!/usr/bin/env python3
from bcc import BPF
import ctypes

bpf_code = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
struct proc_data {
    u32 pid;
    u32 ppid;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);
int kprobe__sys_clone(struct pt_regs *ctx) {
    struct proc_data data = {};
    struct task_struct *task;
    data.pid = bpf_get_current_pid_tgid() >> 32;
    task = (struct task_struct *)bpf_get_current_task();
    data.ppid = task->real_parent->tgid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

class ProcData(ctypes.Structure):
    _fields_ = [("pid", ctypes.c_uint32), ("ppid", ctypes.c_uint32), ("comm", ctypes.c_char * 16)]

print("=" * 50)
print("🚀 LIVE KERNEL MONITOR RUNNING")
print("=" * 50)
print(f"{'PARENT PID':<12}{'CHILD PID':<12}{'COMMAND':<25}")
print("-" * 50)

bpf = BPF(text=bpf_code)

def print_event(cpu, data, size):
    event = ctypes.cast(data, ctypes.POINTER(ProcData)).contents
    print(f"{event.ppid:<12}{event.pid:<12}{event.comm.decode('utf-8', errors='replace'):<25}")

bpf["events"].open_perf_buffer(print_event)
while True:
    try:
        bpf.perf_buffer_poll()
    except KeyboardInterrupt:
        print("\nExiting Safely...")
        exit()
