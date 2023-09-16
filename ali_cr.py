import os
import time
import logging
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get


# Configure logging
logging.basicConfig(
    filename="backup.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def backup_device_config(task):
    try:
        # Retrieve the running config using Napalm
        config_result = task.run(task=napalm_get, getters=["get_config"])
        running_config = config_result.result["get_config"]["running"]

        # Create the backup directory if it doesn't exist
        backup_dir = f"/home/backup/{task.host}"
        os.makedirs(backup_dir, exist_ok=True)

        # Generate the backup file name with a timestamp
        timestamp = time.strftime("%m-%d-%Y_%H-%M-%S", time.localtime())
        backup_filename = f"{task.host}_{timestamp}.cfg"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Write the running config to the backup file
        with open(backup_path, "w" , encoding="utf-8") as backup_file:
            backup_file.write(running_config)

        # Log success and file size
        file_size = os.path.getsize(backup_path)
        logging.info(
            f"Backup of {task.host} configuration saved to {backup_path} (file size = {file_size} bytes)"
        )

    except ImportError as err_msg:
        # Log the error and mark the backup as unsuccessful
        logging.error(f"Error while backing up {task.host}: {str(err_msg)}")

def main():
    nornir_func = InitNornir(config_file="config.yaml")

    # Create a summary results file with a timestamp
    timestamp = time.strftime("%m-%d-%Y_%H-%M-%S", time.localtime())
    summary_results_file = f"/home/backup/summaries/{timestamp}_results.txt"

    with open(summary_results_file, "a", encoding="utf-8") as summary_results:
        summary_results.write(f"{timestamp}: \n\n")

    # Execute the backup task for each device
    nornir_func.run(task=backup_device_config)
if __name__ == "__main__":
    main()
