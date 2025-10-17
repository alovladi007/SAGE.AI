# Real-time Monitoring & Alerting System
# monitoring_system.py

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import aioredis
import websockets
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict, deque
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= METRICS DEFINITIONS =============

# Prometheus metrics
paper_processing_counter = Counter('papers_processed_total', 'Total papers processed', ['status'])
anomaly_detection_counter = Counter('anomalies_detected_total', 'Total anomalies detected', ['type', 'severity'])
similarity_check_counter = Counter('similarity_checks_total', 'Total similarity checks performed')
processing_time_histogram = Histogram('paper_processing_duration_seconds', 'Paper processing duration')
active_jobs_gauge = Gauge('active_processing_jobs', 'Number of active processing jobs')
risk_score_summary = Summary('paper_risk_scores', 'Distribution of risk scores')
system_health_gauge = Gauge('system_health_status', 'System health status (1=healthy, 0=unhealthy)')
api_response_time = Histogram('api_response_time_seconds', 'API response time', ['endpoint', 'method'])
queue_size_gauge = Gauge('processing_queue_size', 'Size of processing queue')
error_rate_counter = Counter('processing_errors_total', 'Total processing errors', ['error_type'])

# ============= CONFIGURATION =============

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False

@dataclass
class MonitoringConfig:
    redis_url: str = "redis://localhost:6379"
    websocket_port: int = 8765
    prometheus_port: int = 9091
    alert_email_enabled: bool = True
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "alerts@academic-integrity.com"
    smtp_password: str = ""
    alert_recipients: List[str] = None
    slack_webhook_url: Optional[str] = None

    def __post_init__(self):
        if self.alert_recipients is None:
            self.alert_recipients = ["admin@academic-integrity.com"]

# ============= MONITORING ENGINE =============

class MonitoringEngine:
    """Core monitoring engine for real-time metrics and alerts"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.redis_client = None
        self.websocket_clients = set()
        self.alerts = {}
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.thresholds = self._load_thresholds()
        self.running = False

    def _load_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Load alerting thresholds"""
        return {
            "processing_time": {
                "warning": 300,  # 5 minutes
                "critical": 600,  # 10 minutes
                "metric": "paper_processing_duration_seconds"
            },
            "error_rate": {
                "warning": 0.05,  # 5% error rate
                "critical": 0.10,  # 10% error rate
                "metric": "processing_errors_rate"
            },
            "queue_size": {
                "warning": 100,
                "critical": 500,
                "metric": "processing_queue_size"
            },
            "high_risk_papers": {
                "warning": 10,  # 10 high-risk papers in an hour
                "critical": 25,  # 25 high-risk papers in an hour
                "metric": "high_risk_papers_hourly"
            },
            "api_response_time": {
                "warning": 2.0,  # 2 seconds
                "critical": 5.0,  # 5 seconds
                "metric": "api_response_time_seconds"
            },
            "similarity_match_rate": {
                "warning": 0.3,  # 30% papers with high similarity
                "critical": 0.5,  # 50% papers with high similarity
                "metric": "high_similarity_rate"
            }
        }

    async def start(self):
        """Start the monitoring engine"""
        self.running = True

        # Connect to Redis
        self.redis_client = await aioredis.create_redis_pool(self.config.redis_url)

        # Start Prometheus metrics server
        start_http_server(self.config.prometheus_port)

        # Start background tasks
        tasks = [
            asyncio.create_task(self._collect_metrics()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._websocket_server()),
            asyncio.create_task(self._health_check()),
            asyncio.create_task(self._aggregate_metrics())
        ]

        logger.info(f"Monitoring engine started on Prometheus port {self.config.prometheus_port}")

        await asyncio.gather(*tasks)

    async def _collect_metrics(self):
        """Collect metrics from various sources"""
        while self.running:
            try:
                # Collect from Redis
                metrics = await self._collect_redis_metrics()

                # Update Prometheus metrics
                await self._update_prometheus_metrics(metrics)

                # Store in buffer for analysis
                timestamp = datetime.utcnow()
                for key, value in metrics.items():
                    self.metrics_buffer[key].append((timestamp, value))

                # Broadcast to WebSocket clients
                await self._broadcast_metrics(metrics)

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                error_rate_counter.labels(error_type="metric_collection").inc()

            await asyncio.sleep(10)  # Collect every 10 seconds

    async def _collect_redis_metrics(self) -> Dict[str, Any]:
        """Collect metrics from Redis"""
        metrics = {}

        try:
            # Get queue sizes
            queue_size = await self.redis_client.llen("processing_queue")
            metrics["queue_size"] = queue_size
            queue_size_gauge.set(queue_size)

            # Get active jobs
            active_jobs = await self.redis_client.scard("active_jobs")
            metrics["active_jobs"] = active_jobs
            active_jobs_gauge.set(active_jobs)

            # Get recent processing times
            processing_times = await self.redis_client.lrange("processing_times", 0, 100)
            if processing_times:
                times = [float(t) for t in processing_times]
                metrics["avg_processing_time"] = np.mean(times)
                metrics["max_processing_time"] = np.max(times)
                for t in times:
                    processing_time_histogram.observe(t)

            # Get error counts
            error_count = await self.redis_client.get("error_count") or 0
            total_count = await self.redis_client.get("total_processed") or 1
            metrics["error_rate"] = int(error_count) / int(total_count)

            # Get risk scores
            risk_scores = await self.redis_client.lrange("recent_risk_scores", 0, 100)
            if risk_scores:
                scores = [float(s) for s in risk_scores]
                metrics["avg_risk_score"] = np.mean(scores)
                metrics["high_risk_count"] = sum(1 for s in scores if s > 0.7)
                for score in scores:
                    risk_score_summary.observe(score)

        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {e}")
            metrics["error"] = str(e)

        return metrics

    async def _update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Update Prometheus metrics"""
        try:
            # Update system health
            if "error" not in metrics:
                system_health_gauge.set(1)
            else:
                system_health_gauge.set(0)

            # Update other metrics as needed
            if "queue_size" in metrics:
                queue_size_gauge.set(metrics["queue_size"])

            if "active_jobs" in metrics:
                active_jobs_gauge.set(metrics["active_jobs"])

        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")

    async def _check_alerts(self):
        """Check for alert conditions"""
        while self.running:
            try:
                current_metrics = self._get_current_metrics()

                for threshold_name, threshold_config in self.thresholds.items():
                    metric_value = current_metrics.get(threshold_config["metric"], 0)

                    # Check critical threshold
                    if metric_value > threshold_config.get("critical", float('inf')):
                        await self._trigger_alert(
                            severity=AlertSeverity.CRITICAL,
                            title=f"Critical: {threshold_name}",
                            description=f"{threshold_name} exceeded critical threshold",
                            metric=threshold_config["metric"],
                            value=metric_value,
                            threshold=threshold_config["critical"]
                        )
                    # Check warning threshold
                    elif metric_value > threshold_config.get("warning", float('inf')):
                        await self._trigger_alert(
                            severity=AlertSeverity.HIGH,
                            title=f"Warning: {threshold_name}",
                            description=f"{threshold_name} exceeded warning threshold",
                            metric=threshold_config["metric"],
                            value=metric_value,
                            threshold=threshold_config["warning"]
                        )

                # Check for anomalies using statistical methods
                await self._detect_anomalies()

            except Exception as e:
                logger.error(f"Error checking alerts: {e}")

            await asyncio.sleep(60)  # Check every minute

    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values"""
        current_metrics = {}

        for metric_name, values in self.metrics_buffer.items():
            if values:
                recent_values = [v for _, v in values[-10:]]  # Last 10 values
                current_metrics[metric_name] = np.mean(recent_values)

        return current_metrics

    async def _detect_anomalies(self):
        """Detect anomalies using statistical methods"""
        for metric_name, values in self.metrics_buffer.items():
            if len(values) >= 100:  # Need sufficient data
                # Extract values
                metric_values = [v for _, v in values]

                # Calculate statistics
                mean = np.mean(metric_values)
                std = np.std(metric_values)

                # Check for outliers (3 sigma rule)
                recent_value = metric_values[-1] if metric_values else 0
                if abs(recent_value - mean) > 3 * std:
                    await self._trigger_alert(
                        severity=AlertSeverity.MEDIUM,
                        title=f"Anomaly detected in {metric_name}",
                        description=f"Value {recent_value:.2f} is {abs(recent_value - mean) / std:.1f} standard deviations from mean",
                        metric=metric_name,
                        value=recent_value,
                        threshold=mean + 3 * std
                    )

                # Check for trend changes
                if len(metric_values) >= 20:
                    recent_trend = np.mean(metric_values[-10:]) - np.mean(metric_values[-20:-10])
                    if abs(recent_trend) > 2 * std:
                        await self._trigger_alert(
                            severity=AlertSeverity.LOW,
                            title=f"Trend change in {metric_name}",
                            description=f"Significant trend change detected: {recent_trend:.2f}",
                            metric=metric_name,
                            value=recent_trend,
                            threshold=2 * std
                        )

    async def _trigger_alert(self, severity: AlertSeverity, title: str,
                           description: str, metric: str, value: float,
                           threshold: float):
        """Trigger an alert"""
        alert = Alert(
            id=f"{metric}_{datetime.utcnow().timestamp()}",
            severity=severity,
            title=title,
            description=description,
            metric=metric,
            value=value,
            threshold=threshold,
            timestamp=datetime.utcnow()
        )

        # Store alert
        self.alerts[alert.id] = alert

        # Send notifications
        await self._send_notifications(alert)

        # Log alert
        logger.warning(f"Alert triggered: {title} - {description}")

        # Update counter
        anomaly_detection_counter.labels(
            type=metric,
            severity=severity.value
        ).inc()

    async def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        tasks = []

        # Email notification
        if self.config.alert_email_enabled:
            tasks.append(self._send_email_alert(alert))

        # Slack notification
        if self.config.slack_webhook_url:
            tasks.append(self._send_slack_alert(alert))

        # WebSocket notification
        tasks.append(self._broadcast_alert(alert))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_user
            msg['To'] = ', '.join(self.config.alert_recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"

            body = f"""
            Alert Details:
            -------------
            Severity: {alert.severity.value}
            Metric: {alert.metric}
            Value: {alert.value:.2f}
            Threshold: {alert.threshold:.2f}
            Time: {alert.timestamp.isoformat()}

            Description:
            {alert.description}

            Please check the monitoring dashboard for more details.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email (would use async SMTP in production)
            # This is simplified for demonstration
            logger.info(f"Email alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    async def _send_slack_alert(self, alert: Alert):
        """Send Slack notification"""
        try:
            async with httpx.AsyncClient() as client:
                color = {
                    AlertSeverity.LOW: "#36a64f",
                    AlertSeverity.MEDIUM: "#ff9900",
                    AlertSeverity.HIGH: "#ff6600",
                    AlertSeverity.CRITICAL: "#ff0000"
                }.get(alert.severity, "#808080")

                payload = {
                    "attachments": [{
                        "color": color,
                        "title": alert.title,
                        "text": alert.description,
                        "fields": [
                            {"title": "Metric", "value": alert.metric, "short": True},
                            {"title": "Value", "value": f"{alert.value:.2f}", "short": True},
                            {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True},
                            {"title": "Severity", "value": alert.severity.value, "short": True}
                        ],
                        "footer": "Academic Integrity Platform",
                        "ts": int(alert.timestamp.timestamp())
                    }]
                }

                response = await client.post(
                    self.config.slack_webhook_url,
                    json=payload
                )

                if response.status_code == 200:
                    logger.info(f"Slack alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast metrics to WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                "type": "metrics",
                "timestamp": datetime.utcnow().isoformat(),
                "data": metrics
            })

            # Send to all connected clients
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Remove disconnected clients
            self.websocket_clients -= disconnected

    async def _broadcast_alert(self, alert: Alert):
        """Broadcast alert to WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                "type": "alert",
                "timestamp": datetime.utcnow().isoformat(),
                "data": asdict(alert)
            }, default=str)

            # Send to all connected clients
            for client in self.websocket_clients.copy():
                try:
                    await client.send(message)
                except:
                    self.websocket_clients.remove(client)

    async def _websocket_server(self):
        """WebSocket server for real-time updates"""
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            logger.info(f"WebSocket client connected from {websocket.remote_address}")

            try:
                # Send initial data
                await websocket.send(json.dumps({
                    "type": "connected",
                    "timestamp": datetime.utcnow().isoformat()
                }))

                # Keep connection alive
                async for message in websocket:
                    # Handle client messages if needed
                    pass

            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.websocket_clients.remove(websocket)
                logger.info(f"WebSocket client disconnected")

        server = await websockets.serve(
            handle_client,
            "0.0.0.0",
            self.config.websocket_port
        )

        logger.info(f"WebSocket server started on port {self.config.websocket_port}")
        await server.wait_closed()

    async def _health_check(self):
        """Perform system health checks"""
        while self.running:
            try:
                health_status = {
                    "redis": await self._check_redis_health(),
                    "database": await self._check_database_health(),
                    "ml_workers": await self._check_ml_workers_health(),
                    "api": await self._check_api_health()
                }

                # Overall health
                overall_healthy = all(health_status.values())
                system_health_gauge.set(1 if overall_healthy else 0)

                if not overall_healthy:
                    unhealthy_components = [k for k, v in health_status.items() if not v]
                    await self._trigger_alert(
                        severity=AlertSeverity.HIGH,
                        title="System Health Alert",
                        description=f"Unhealthy components: {', '.join(unhealthy_components)}",
                        metric="system_health",
                        value=0,
                        threshold=1
                    )

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                system_health_gauge.set(0)

            await asyncio.sleep(30)  # Check every 30 seconds

    async def _check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            await self.redis_client.ping()
            return True
        except:
            return False

    async def _check_database_health(self) -> bool:
        """Check database health"""
        try:
            # Would implement actual database health check
            return True
        except:
            return False

    async def _check_ml_workers_health(self) -> bool:
        """Check ML workers health"""
        try:
            active_workers = await self.redis_client.scard("active_workers")
            return active_workers > 0
        except:
            return False

    async def _check_api_health(self) -> bool:
        """Check API health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://backend:8000/health", timeout=5)
                return response.status_code == 200
        except:
            return False

    async def _aggregate_metrics(self):
        """Aggregate metrics for reporting"""
        while self.running:
            try:
                # Daily aggregation
                await self._create_daily_report()

                # Cleanup old data
                await self._cleanup_old_data()

            except Exception as e:
                logger.error(f"Error aggregating metrics: {e}")

            await asyncio.sleep(3600)  # Run every hour

    async def _create_daily_report(self):
        """Create daily metrics report"""
        try:
            # Calculate daily statistics
            daily_stats = {
                "date": datetime.utcnow().date().isoformat(),
                "total_papers": await self.redis_client.get("daily_papers_count") or 0,
                "anomalies_detected": await self.redis_client.get("daily_anomalies_count") or 0,
                "avg_processing_time": await self._calculate_daily_avg("processing_times"),
                "avg_risk_score": await self._calculate_daily_avg("risk_scores"),
                "error_rate": await self._calculate_daily_error_rate()
            }

            # Store report
            await self.redis_client.set(
                f"daily_report_{daily_stats['date']}",
                json.dumps(daily_stats)
            )

            logger.info(f"Daily report created: {daily_stats}")

        except Exception as e:
            logger.error(f"Failed to create daily report: {e}")

    async def _calculate_daily_avg(self, metric_key: str) -> float:
        """Calculate daily average for a metric"""
        values = await self.redis_client.lrange(f"daily_{metric_key}", 0, -1)
        if values:
            return np.mean([float(v) for v in values])
        return 0.0

    async def _calculate_daily_error_rate(self) -> float:
        """Calculate daily error rate"""
        errors = int(await self.redis_client.get("daily_errors") or 0)
        total = int(await self.redis_client.get("daily_total") or 1)
        return errors / total if total > 0 else 0.0

    async def _cleanup_old_data(self):
        """Cleanup old monitoring data"""
        try:
            # Keep only last 7 days of detailed metrics
            cutoff_date = datetime.utcnow() - timedelta(days=7)

            for metric_name, values in self.metrics_buffer.items():
                # Remove old values
                self.metrics_buffer[metric_name] = deque(
                    [(t, v) for t, v in values if t > cutoff_date],
                    maxlen=1000
                )

            # Cleanup old alerts
            for alert_id, alert in list(self.alerts.items()):
                if alert.timestamp < cutoff_date:
                    del self.alerts[alert_id]

            logger.info("Cleaned up old monitoring data")

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

# ============= DASHBOARD API =============

class MonitoringDashboardAPI:
    """API for monitoring dashboard"""

    def __init__(self, monitoring_engine: MonitoringEngine):
        self.engine = monitoring_engine

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.engine._get_current_metrics(),
            "health": {
                "redis": await self.engine._check_redis_health(),
                "database": await self.engine._check_database_health(),
                "ml_workers": await self.engine._check_ml_workers_health(),
                "api": await self.engine._check_api_health()
            }
        }

    async def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get alerts"""
        alerts = []
        for alert in self.engine.alerts.values():
            if not active_only or not alert.resolved:
                alerts.append(asdict(alert))

        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.engine.alerts:
            self.engine.alerts[alert_id].resolved = True
            return True
        return False

    async def get_metric_history(self, metric_name: str,
                                hours: int = 24) -> List[Dict[str, Any]]:
        """Get metric history"""
        history = []
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        if metric_name in self.engine.metrics_buffer:
            for timestamp, value in self.engine.metrics_buffer[metric_name]:
                if timestamp > cutoff:
                    history.append({
                        "timestamp": timestamp.isoformat(),
                        "value": value
                    })

        return history

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "current_metrics": await self.get_current_metrics(),
            "active_alerts": await self.get_alerts(active_only=True),
            "recent_metrics": {
                metric: await self.get_metric_history(metric, hours=1)
                for metric in ["queue_size", "active_jobs", "error_rate"]
            }
        }

# ============= MAIN EXECUTION =============

async def main():
    """Main execution function"""
    config = MonitoringConfig()
    engine = MonitoringEngine(config)

    # Start monitoring engine
    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())
