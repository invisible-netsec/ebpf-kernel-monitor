#!/usr/bin/env python3
from bcc import BPF
import ctypes
import requests

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
print("🚀 LIVE ENTERPRISE KERNEL MONITOR RUNNING")
print("=" * 50)
print(f"{'PARENT PID':<12}{'CHILD PID':<12}{'COMMAND':<25}")
print("-" * 50)

bpf = BPF(text=bpf_code)

def print_event(cpu, data, size):
    event = ctypes.cast(data, ctypes.POINTER(ProcData)).contents
    process_name = event.comm.decode('utf-8', errors='replace')
    log_message = f"⚠️ ALERT: New Process Spawned -> PID: {event.pid} | Parent: {event.ppid} | Command: {process_name}"
    print(f"{event.ppid:<12}{event.pid:<12}{process_name:<25}")
    
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
    if "ssh" in process_name or "bash" in process_name or "sh" in process_name:
        try:
            requests.post(webhook_url, json={"content": log_message})
        except:
            pass

bpf["events"].open_perf_buffer(print_event)
while True:
    try:
        bpf.perf_buffer_poll()
    except KeyboardInterrupt:
        print("\nExiting Safely...")
        exit()

