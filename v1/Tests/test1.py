import utils
import os
tmp_path = "output"

utils.send_message({
    "message_type": "new_job",
    "n": "13",
    "output_directory": tmp_path,
}, port=6000)

# Wait for output to be created
utils.wait_for_exists(f"{tmp_path}/job_0")


