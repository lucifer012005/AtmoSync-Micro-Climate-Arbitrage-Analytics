import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def evaluate_arbitrage_alert(container_event):
    """Triggers an alert if spoilage risk requires container rerouting."""
    container_id = container_event.get("container_id")
    health_status = container_event.get("container_health_status")
    margin = container_event.get("arbitrage_margin_usd", 0.0)

    if health_status == "HIGH_RISK" and margin > 0:
        logging.warning(
            f"[ARBITRAGE ALERT] Container {container_id} is degrading! "
            f"Rerouting to secondary market secures financial gain of ${margin:.2f}/kg."
        )
        return True
    return False

if __name__ == "__main__":
    sample_event = {
        "container_id": "CONT-A001",
        "container_health_status": "HIGH_RISK",
        "arbitrage_margin_usd": 0.65
    }
    evaluate_arbitrage_alert(sample_event)