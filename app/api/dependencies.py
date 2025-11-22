from fastapi import BackgroundTasks, Depends

class TaskRunner:
    """
    Dependency to abstract away the execution of background tasks.
    This allows for synchronous execution during tests.
    """
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def run(self, func, *args, **kwargs):
        self.background_tasks.add_task(func, *args, **kwargs)

def get_task_runner(background_tasks: BackgroundTasks):
    return TaskRunner(background_tasks)