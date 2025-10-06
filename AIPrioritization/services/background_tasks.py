"""
Background Task Management for AI Prioritization Engine
"""
import asyncio
import logging
from typing import Dict, Set
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks with proper lifecycle handling"""
    
    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running_tasks: Set[str] = set()
        self._shutdown_event = asyncio.Event()
    
    async def start_task(self, name: str, coro, restart_on_failure: bool = True):
        """Start a background task with optional restart on failure"""
        if name in self._running_tasks:
            logger.warning(f"Task '{name}' is already running")
            return
        
        self._running_tasks.add(name)
        task = asyncio.create_task(self._run_task_with_restart(name, coro, restart_on_failure))
        self._tasks[name] = task
        logger.info(f"✅ Started background task: {name}")
    
    async def _run_task_with_restart(self, name: str, coro, restart_on_failure: bool):
        """Run a task with automatic restart on failure"""
        while not self._shutdown_event.is_set():
            try:
                await coro()
            except asyncio.CancelledError:
                logger.info(f"🛑 Task '{name}' cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Task '{name}' failed: {e}")
                
                if not restart_on_failure or self._shutdown_event.is_set():
                    break
                    
                # Wait before restart
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(), 
                        timeout=10.0
                    )
                    break  # Shutdown requested during wait
                except asyncio.TimeoutError:
                    logger.info(f"🔄 Restarting task: {name}")
                    continue
        
        self._running_tasks.discard(name)
        logger.info(f"🏁 Task '{name}' finished")
    
    async def stop_task(self, name: str):
        """Stop a specific background task"""
        if name not in self._tasks:
            logger.warning(f"Task '{name}' not found")
            return
        
        task = self._tasks[name]
        task.cancel()
        
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(f"Task '{name}' did not stop gracefully")
        except asyncio.CancelledError:
            pass
        
        del self._tasks[name]
        self._running_tasks.discard(name)
        logger.info(f"🛑 Stopped background task: {name}")
    
    async def stop_all_tasks(self):
        """Stop all background tasks"""
        logger.info("🛑 Stopping all background tasks...")
        self._shutdown_event.set()
        
        # Cancel all tasks
        for task in self._tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks.values(), return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some tasks did not stop gracefully")
        
        self._tasks.clear()
        self._running_tasks.clear()
        logger.info("✅ All background tasks stopped")
    
    def get_task_status(self) -> Dict[str, str]:
        """Get status of all background tasks"""
        status = {}
        for name, task in self._tasks.items():
            if task.done():
                if task.cancelled():
                    status[name] = "cancelled"
                elif task.exception():
                    status[name] = f"failed: {task.exception()}"
                else:
                    status[name] = "completed"
            else:
                status[name] = "running"
        return status
    
    @property
    def running_tasks(self) -> Set[str]:
        """Get set of currently running task names"""
        return self._running_tasks.copy()

# Global task manager instance
task_manager = BackgroundTaskManager()

@asynccontextmanager
async def managed_background_tasks():
    """Context manager for background tasks lifecycle"""
    try:
        yield task_manager
    finally:
        await task_manager.stop_all_tasks()
