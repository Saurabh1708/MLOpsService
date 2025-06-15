from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import threading
import time
from queue import PriorityQueue
import logging
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.cluster import Cluster
from app.core.enums import DeploymentStatus, DeploymentPriority
from app.db.base import SessionLocal

logger = logging.getLogger(__name__)

@dataclass
class SchedulingTask:
    deployment_id: str
    priority: int
    created_at: datetime
    required_resources: Dict[str, float]
    
    def __lt__(self, other):
        # Higher priority first, then older tasks first
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.created_at < other.created_at

class ResourceScheduler:
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.running = False
        self.scheduler_thread = None
        
    def add_deployment(self, deployment: Deployment):
        """Add a deployment to the scheduling queue"""
        task = SchedulingTask(
            deployment_id=deployment.id,
            priority=deployment.priority.value,
            created_at=deployment.created_at,
            required_resources={
                'ram': deployment.required_ram_gb,
                'cpu': deployment.required_cpu_cores,
                'gpu': deployment.required_gpu_count
            }
        )
        self.task_queue.put(task)
        logger.info(f"Added deployment {deployment.id} to scheduling queue")
        
    def can_schedule(self, cluster: Cluster, required_resources: Dict[str, float]) -> bool:
        """Check if a cluster has enough resources for a deployment"""
        return (
            cluster.available_ram_gb >= required_resources['ram'] and
            cluster.available_cpu_cores >= required_resources['cpu'] and
            cluster.available_gpu_count >= required_resources['gpu']
        )
        
    def find_preemptable_deployments(self, cluster: Cluster, required_resources: Dict[str, float], 
                                   min_priority: int, db: Session) -> List[Deployment]:
        """Find deployments that can be preempted to make room for higher priority deployment"""
        running_deployments = db.query(Deployment).filter(
            Deployment.cluster_id == cluster.id,
            Deployment.status == DeploymentStatus.RUNNING,
            Deployment.priority.value < min_priority
        ).order_by(Deployment.priority.value.asc()).all()
        
        preemptable = []
        freed_resources = {'ram': 0, 'cpu': 0, 'gpu': 0}
        
        for deployment in running_deployments:
            preemptable.append(deployment)
            freed_resources['ram'] += deployment.required_ram_gb
            freed_resources['cpu'] += deployment.required_cpu_cores
            freed_resources['gpu'] += deployment.required_gpu_count
            
            if (cluster.available_ram_gb + freed_resources['ram'] >= required_resources['ram'] and
                cluster.available_cpu_cores + freed_resources['cpu'] >= required_resources['cpu'] and
                cluster.available_gpu_count + freed_resources['gpu'] >= required_resources['gpu']):
                break
                
        return preemptable
        
    def schedule_deployment(self, deployment_id: str, db: Session) -> bool:
        """Attempt to schedule a single deployment"""
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment or deployment.status != DeploymentStatus.PENDING:
            return False
            
        cluster = db.query(Cluster).filter(Cluster.id == deployment.cluster_id).first()
        if not cluster:
            return False
            
        required_resources = {
            'ram': deployment.required_ram_gb,
            'cpu': deployment.required_cpu_cores,
            'gpu': deployment.required_gpu_count
        }
        
        # Try direct scheduling first
        if self.can_schedule(cluster, required_resources):
            return self._allocate_resources(deployment, cluster, db)
            
        # Try preemption for high priority deployments
        if deployment.priority.value >= DeploymentPriority.HIGH.value:
            preemptable = self.find_preemptable_deployments(
                cluster, required_resources, deployment.priority.value, db
            )
            
            if preemptable:
                # Preempt lower priority deployments
                for preempted_deployment in preemptable:
                    self._deallocate_resources(preempted_deployment, cluster, db)
                    preempted_deployment.status = DeploymentStatus.PREEMPTED
                    preempted_deployment.completed_at = datetime.now()
                    logger.info(f"Preempted deployment {preempted_deployment.id}")
                
                # Schedule the high priority deployment
                return self._allocate_resources(deployment, cluster, db)
                
        return False
        
    def _allocate_resources(self, deployment: Deployment, cluster: Cluster, db: Session) -> bool:
        """Allocate cluster resources to a deployment"""
        cluster.available_ram_gb -= deployment.required_ram_gb
        cluster.available_cpu_cores -= deployment.required_cpu_cores
        cluster.available_gpu_count -= deployment.required_gpu_count
        
        deployment.status = DeploymentStatus.RUNNING
        deployment.scheduled_at = datetime.now()
        deployment.started_at = datetime.now()
        
        db.commit()
        logger.info(f"Allocated resources for deployment {deployment.id}")
        return True
        
    def _deallocate_resources(self, deployment: Deployment, cluster: Cluster, db: Session):
        """Deallocate cluster resources from a deployment"""
        cluster.available_ram_gb += deployment.required_ram_gb
        cluster.available_cpu_cores += deployment.required_cpu_cores
        cluster.available_gpu_count += deployment.required_gpu_count
        
    def start_scheduler(self):
        """Start the background scheduler thread"""
        if self.running:
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Resource scheduler started")
        
    def stop_scheduler(self):
        """Stop the background scheduler thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Resource scheduler stopped")
        
    def _scheduler_loop(self):
        """Main scheduler loop that processes the queue"""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task = self.task_queue.get(timeout=1)
                    db = SessionLocal()
                    try:
                        success = self.schedule_deployment(task.deployment_id, db)
                        if not success:
                            # Re-queue the task if it couldn't be scheduled
                            self.task_queue.put(task)
                    finally:
                        db.close()
                else:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(1)

# Create a global scheduler instance
scheduler = ResourceScheduler() 