"""
Script to launch local virtual environment and/or deploy to GCP Cloud.

Update the Constant Data for your configuration.

Run the script.
    bash> python deploy.py

Script will run through a series of checks:
    # Check if gcloud is installed.
    # Check if gcloud configuration exists.
    # Check if local virtual environment (venv) exists.

Script will then ask what you want to do:
    # [Under Evaluation] Should we ask to start the web server?
    # Do you want to deploy to the GCP cloud?
    
"""

##############################################################################
# IMPORTS
##############################################################################
import subprocess
from pprint import pprint

##############################################################################
# CONSTANT DATA
##############################################################################

PROJECT_NAME = "irma-covered-calls-test"
ZONE_NAME = "us-central1"
ACCOUNT = "matt.hess@lookoutmountainresearch.com"
FUNCTION_NAME = "coveredcalls"
PUBSUB_TOPIC = "coveredcalls_analysis"
CONFIG_NAME = "function-coveredcalls"
BUCKETNAME = "lmr_coveredcalls"

##############################################################################
# FUNCTIONS
##############################################################################

"""

gcloud init 
    --account 
    --project 
    [--no-browser] 
    [--console-only, --no-launch-browser] 
    [--skip-diagnostics] 
    [GCLOUD_WIDE_FLAG …]

EXAMPLE CREATE BUCKET: 
gcloud iam service-accounts create SA_NAME \
    --description="DESCRIPTION" \
    --display-name="DISPLAY_NAME"

COMMAND CREATE BUCKET:
gcloud iam roles create bucketAdmin \
    --project PROJECT_NAME \
    --title "Bucket admin" \
    --description "This role has only the storage.buckets.admin permission" \
    --permissions storage.buckets.get

objects update	

--storage-class
--encryption-key
--clear-encryption-key	

storage.objects.get
storage.objects.list
storage.objects.create
storage.objects.delete

EXAMPLE CREATE STORAGE CERTIFICATE:
gcloud iam service-accounts keys create OUTPUT-FILE \
    --iam-account=IAM_ACCOUNT \
    [--key-file-type=KEY_FILE_TYPE; default="json"] \
    [GCLOUD_WIDE_FLAG …] \

COMMAND CREATE STORAGE CERTIFICATE


EXAMPLE FUNCTIONS DEPLOY:
gcloud functions deploy YOUR_FUNCTION_NAME \
[--gen2] \
--region=YOUR_REGION \
--runtime=YOUR_RUNTIME \
--source=YOUR_SOURCE_LOCATION \
--entry-point=YOUR_CODE_ENTRYPOINT \
TRIGGER_FLAGS

COMMAND DEPLOY FUNCTION:

"""


def check_gcloud_installation():
    """
    Checks to see if gcloud is installed and if not, asks if you want to install.

        Args:
            None

        Raises:
            Exception: No such file or directory

        Returns:
            None
    """
    try:
        output = subprocess.run(['gcloud', '--version'], stdout=subprocess.PIPE)
        pprint(output.stdout.decode('utf-8'))
        if "Google Cloud SDK" in str(output.stdout):
            print("Installed")
    except Exception as e:
        print(e)
        install_gcloud = input("ERROR: 'gcloud' not installed - would you like to install? (y or n): ")
        if install_gcloud == "y":
            subprocess.run(['sudo', 'apt-get', 'install', 'gcloud'], stdout=subprocess.PIPE)
    return

def check_gcloud_configurations(config_name):
    """
    Checks to see if gcloud configuration has been configured and asks if 
    you want to install.

        Args:
            None

        Raises:
            Exception: No such file or directory

        Returns:
            None
    """
    try:
        output = subprocess.run(f'gcloud', 'config', 'configurations', 'list', f'--filter={CONFIG_NAME}', stdout=subprocess.PIPE)
        pprint(output.stdout.decode('utf-8'))
        if "Listed 0 items" in str(output.stdout):
            gcloud_config_status = "NOT FOUND"
        else:
            gcloud_config_status = "INSTALLED"
    except Exception as e:
        print(e)
        gcloud_config_status = "ERROR"
    print(gcloud_config_status)
    if gcloud_config_status != "INSTALLED":
        print(f"{CONFIG_NAME} was not found.")
        config_setup = input(f"Would you like to configure '{CONFIG_NAME}'? (y or n): ")
        if config_setup == "y":
            subprocess.run(['gcloud', 'config', 'configurations', 'create', CONFIG_NAME], stdout=subprocess.PIPE)
            subprocess.run(['gcloud', 'config', 'configurations', 'activate', CONFIG_NAME], stdout=subprocess.PIPE)
            subprocess.run(['gcloud', 'config', 'set', 'project', PROJECT_NAME], stdout=subprocess.PIPE)
            subprocess.run(['gcloud', 'config', 'set', 'compute/zone', ZONE_NAME], stdout=subprocess.PIPE)
            subprocess.run(['gcloud', 'config', 'set', 'account', ACCOUNT], stdout=subprocess.PIPE)
    if gcloud_config_status == "INSTALLED":
        print(f"{CONFIG_NAME} has been found.")
        config_activate = input(f"Would you like to activate the {CONFIG_NAME} configuration? (y or n): ")
        if config_activate == "y":
            subprocess.run(['gcloud', 'config', 'configurations', 'activate', CONFIG_NAME], stdout=subprocess.PIPE)
    return

def deploy_pubsub():
    """
    Deploy the Pub/Sub(s) for the app.

        Args:
            None

        Raises:
            

        Returns:
            None
    """
    subprocess.run([
        'gcloud',
        'pubsub',
        'topics',
        'create',
        PUBSUB_TOPIC
        ], stdout=subprocess.PIPE)
    return

def deploy_function():
    """
    Deploy the function(s) for the app.

        Args:
            None

        Raises:
            

        Returns:
            None
    """
    subprocess.run([
        'gcloud',
        'functions',
        'deploy',
        FUNCTION_NAME,
            '--gen2',
            f'--region={ZONE_NAME}',
            '--runtime=python39',
            '--source=.',
            '--entry-point=pubsub_handler',
            f'--trigger-topic={PUBSUB_TOPIC}'
        ], stdout=subprocess.PIPE)
    pass
