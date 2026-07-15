import argparse
import sys
import logging
from typing import List, Dict, Any

from selector_review_queue import SelectorReviewQueue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Review and validate AI-generated CSS selector suggestions.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()

    queue_manager = SelectorReviewQueue()
    pending = queue_manager.get_pending()

    if not pending:
        logger.info("✅ No pending selector suggestions to review.")
        return

    logger.info(f"🔍 Found {len(pending)} pending selector suggestion(s).\n")

    if not args.interactive:
        logger.info("Run with --interactive to approve or reject suggestions.")
        for item in pending:
            logger.info(f"[{item['site']}] Field: '{item['field']}'")
            logger.info(f"   Suggested: {item['new_selector']}")
            logger.info(f"   Confidence: {item['confidence']:.0%}")
        return

    for item in pending:
        logger.info("=" * 60)
        logger.info(f"SITE:       {item['site'].upper()}")
        logger.info(f"FIELD:      {item['field']}")
        logger.info(f"SUGGESTION: {item['new_selector']}")
        logger.info(f"CONFIDENCE: {item['confidence']:.0%}")
        logger.info(f"REASONING:  {item['reasoning']}")
        logger.info(f"EXAMPLE:    {item['example_value']}")
        logger.info("=" * 60)
        
        while True:
            choice = input("Action? [a]pprove primary, [f]allback only, [r]eject, [s]kip: ").lower().strip()
            if choice in ['a', 'f', 'r', 's']:
                break
            logger.info("Invalid choice. Please use a, f, r, or s.")
            
        if choice == 'a':
            if queue_manager.approve_suggestion(item['id'], is_fallback=False):
                logger.info("✅ Approved as primary selector.")
        elif choice == 'f':
            if queue_manager.approve_suggestion(item['id'], is_fallback=True):
                logger.info("✅ Approved as fallback selector.")
        elif choice == 'r':
            if queue_manager.reject_suggestion(item['id']):
                logger.info("❌ Rejected suggestion.")
        elif choice == 's':
            logger.info("⏭️ Skipped for now.")
            
        print("\n")

    logger.info("Review complete.")

if __name__ == "__main__":
    main()
