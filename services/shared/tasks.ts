export function trimTasks<T extends { state: string }>(tasks: Map<string, T>, maxTasks: number) {
  if (tasks.size < maxTasks) {
    return;
  }

  for (const [taskId, task] of tasks) {
    if (task.state !== "running") {
      tasks.delete(taskId);
      if (tasks.size < maxTasks) {
        return;
      }
    }
  }

  const oldestTaskId = tasks.keys().next().value;
  if (oldestTaskId) {
    tasks.delete(oldestTaskId);
  }
}
