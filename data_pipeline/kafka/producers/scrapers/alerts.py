import logging

logger = logging.getLogger(__name__)

def send_alert(site: str, message: str, severity: str = "WARNING", details: dict = None):
    """
    Logs structured alerts when scraper degradation is detected.
    This acts as a placeholder/extension point for actual notifications (e.g. Email, Slack, Webhook).
    """
    log_msg = f"[{severity}] SCRAPER ALERT for {site.upper()}: {message}"
    if details:
        log_msg += f" | Details: {details}"
        
    if severity.upper() == "ERROR":
        logger.error(log_msg)
    else:
        logger.warning(log_msg)
        
    # TODO: Implement actual notification logic here
    # e.g., requests.post(SLACK_WEBHOOK, json={"text": log_msg})
