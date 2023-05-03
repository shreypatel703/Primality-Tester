import json
import logging

LOGGER = logging.getLogger(__name__)

def manage_operations(message_dict, job_queue):
    LOGGER.debug("TCP received\n%s", json.dumps(message_dict, indent=2))

    if message_dict["message_type"] == "new_job":
        job_queue.append(message_dict)