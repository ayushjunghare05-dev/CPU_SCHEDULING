"""Pure scheduling algorithms and metric calculations."""
from __future__ import annotations
from typing import Any

def _normalise_processes(raw_processes: Any) -> list[dict[str, Any]]:
    """Validate and normalize process data; retain input order for tie-breaking."""
    if not isinstance(raw_processes, list) or not raw_processes:
        raise ValueError("Add at least one process before simulating.")
    if len(raw_processes) > 20:
        raise ValueError("Please use 20 or fewer processes for this simulator.")

    processes: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for index, item in enumerate(raw_processes):
        if not isinstance(item, dict):
            raise ValueError(f"Process row {index + 1} is invalid.")
        pid = str(item.get("pid", f"P{index + 1}")).strip()
        if not pid:
            pid = f"P{index + 1}"
        if len(pid) > 12:
            raise ValueError(f"Process ID '{pid}' is too long (max 12 characters).")
        if pid in used_ids:
            raise ValueError(f"Process ID '{pid}' is repeated. Use unique IDs.")
        used_ids.add(pid)

        try:
            arrival = int(item.get("arrival_time"))
            burst = int(item.get("burst_time"))
        except (TypeError, ValueError):
            raise ValueError(f"{pid}: arrival and burst times must be whole numbers.")
        if arrival < 0:
            raise ValueError(f"{pid}: arrival time cannot be negative.")
        if burst <= 0:
            raise ValueError(f"{pid}: burst time must be greater than zero.")
        if arrival > 10000 or burst > 10000:
            raise ValueError(f"{pid}: use values of 10,000 or less for this demo.")

        processes.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "order": index,
        })
    return processes


def _append_segment(timeline: list[dict[str, Any]], pid: str, start: int, end: int) -> None:
    """Append a Gantt segment and merge adjacent segments of the same process."""
    if end <= start:
        return
    if timeline and timeline[-1]["pid"] == pid and timeline[-1]["end"] == start:
        timeline[-1]["end"] = end
        timeline[-1]["duration"] += end - start
    else:
        timeline.append({"pid": pid, "start": start, "end": end, "duration": end - start})


def _finish_result(
    algorithm: str,
    processes: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
    completion: dict[str, int],
    first_start: dict[str, int],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total_waiting = total_turnaround = total_response = 0
    total_burst = sum(p["burst_time"] for p in processes)

    for p in processes:
        pid = p["pid"]
        ct = completion[pid]
        tat = ct - p["arrival_time"]
        wt = tat - p["burst_time"]
        rt = first_start[pid] - p["arrival_time"]
        rows.append({
            "pid": pid,
            "arrival_time": p["arrival_time"],
            "burst_time": p["burst_time"],
            "completion_time": ct,
            "turnaround_time": tat,
            "waiting_time": wt,
            "response_time": rt,
        })
        total_waiting += wt
        total_turnaround += tat
        total_response += rt

    finish_time = max(completion.values()) if completion else 0
    count = len(processes)
    return {
        "algorithm": algorithm,
        "timeline": timeline,
        "processes": rows,
        "metrics": {
            "average_waiting_time": round(total_waiting / count, 2),
            "average_turnaround_time": round(total_turnaround / count, 2),
            "average_response_time": round(total_response / count, 2),
            "cpu_utilization": round((total_burst / finish_time) * 100, 2) if finish_time else 0,
            "throughput": round(count / finish_time, 3) if finish_time else 0,
            "total_burst_time": total_burst,
            "finish_time": finish_time,
            "process_count": count,
        },
    }


def fcfs(processes: list[dict[str, Any]]) -> dict[str, Any]:
    """First Come First Served (non-preemptive)."""
    current = 0
    timeline: list[dict[str, Any]] = []
    completion: dict[str, int] = {}
    first_start: dict[str, int] = {}

    for p in sorted(processes, key=lambda x: (x["arrival_time"], x["order"])):
        if current < p["arrival_time"]:
            _append_segment(timeline, "IDLE", current, p["arrival_time"])
            current = p["arrival_time"]
        first_start[p["pid"]] = current
        end = current + p["burst_time"]
        _append_segment(timeline, p["pid"], current, end)
        current = end
        completion[p["pid"]] = current

    return _finish_result("FCFS", processes, timeline, completion, first_start)


def sjf_non_preemptive(processes: list[dict[str, Any]]) -> dict[str, Any]:
    """Shortest Job First (non-preemptive); ties use arrival time, then input order."""
    current = 0
    pending = {p["pid"]: p for p in processes}
    timeline: list[dict[str, Any]] = []
    completion: dict[str, int] = {}
    first_start: dict[str, int] = {}

    while pending:
        ready = [p for p in pending.values() if p["arrival_time"] <= current]
        if not ready:
            next_arrival = min(p["arrival_time"] for p in pending.values())
            _append_segment(timeline, "IDLE", current, next_arrival)
            current = next_arrival
            ready = [p for p in pending.values() if p["arrival_time"] <= current]

        chosen = min(ready, key=lambda x: (x["burst_time"], x["arrival_time"], x["order"]))
        pid = chosen["pid"]
        first_start[pid] = current
        end = current + chosen["burst_time"]
        _append_segment(timeline, pid, current, end)
        current = end
        completion[pid] = current
        del pending[pid]

    return _finish_result("SJF (Non-preemptive)", processes, timeline, completion, first_start)


def round_robin(processes: list[dict[str, Any]], quantum: int) -> dict[str, Any]:
    """Round Robin; arrivals during a slice enter the ready queue before the runner is requeued."""
    if quantum <= 0:
        raise ValueError("Time quantum must be a positive whole number.")
    if quantum > 10000:
        raise ValueError("Time quantum must be 10,000 or less.")

    ordered = sorted(processes, key=lambda x: (x["arrival_time"], x["order"]))
    remaining = {p["pid"]: p["burst_time"] for p in ordered}
    completion: dict[str, int] = {}
    first_start: dict[str, int] = {}
    timeline: list[dict[str, Any]] = []
    queue: list[dict[str, Any]] = []
    next_index = 0
    current = 0

    while len(completion) < len(ordered):
        while next_index < len(ordered) and ordered[next_index]["arrival_time"] <= current:
            queue.append(ordered[next_index])
            next_index += 1

        if not queue:
            next_arrival = ordered[next_index]["arrival_time"]
            _append_segment(timeline, "IDLE", current, next_arrival)
            current = next_arrival
            continue

        p = queue.pop(0)
        pid = p["pid"]
        if pid not in first_start:
            first_start[pid] = current

        run_for = min(quantum, remaining[pid])
        start = current
        current += run_for
        remaining[pid] -= run_for
        _append_segment(timeline, pid, start, current)

        # Enqueue processes that arrived during this time slice first.
        while next_index < len(ordered) and ordered[next_index]["arrival_time"] <= current:
            queue.append(ordered[next_index])
            next_index += 1

        if remaining[pid] == 0:
            completion[pid] = current
        else:
            queue.append(p)

    return _finish_result("Round Robin", processes, timeline, completion, first_start)


