import os
import subprocess
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def define_env(env_name):
    """Define environment/store-specific variables."""
    if env_name == "prd1":
        env_vars = {
            "APP_HOST": ["hostname610", "hostname612", "hostname614", "hostname616"],
            "WEB_HOST": ["hostnameweb601", "hostnameweb602", "hostnameweb603", "hostnameweb604", "hostnameweb605"],
            "SOLR_HOST": ["hostnamesrch601", "hostnamesrch603", "hostnamesrch608"],
            "WC_HOST": "hostname601",
            "APP_QNTTY": [2, 2, 2, 2],
            "SOLR_QNTTY": [1, 1, 1],
            "APP_SERV": ["app110", "app210", "app112", "app212", "app114", "app214", "app116", "app216"],
            "SOLR_SERV": ["srchapp1", "srchapp3", "srchapp8"],
            "INS": "prod01"
        }
    elif env_name == "prd2":
        env_vars = {
            "APP_HOST": ["ws8sc601", "hostname611", "hostname613", "hostname615", "hostname617"],
            "WEB_HOST": ["hostnameweb601", "hostnameweb602", "hostnameweb603", "hostnameweb604", "hostnameweb605"],
            "SOLR_HOST": ["hostnamesrch602", "hostnamesrch604"],
            "WC_HOST": "hostname601",
            "APP_QNTTY": [1, 2, 2, 2, 2],
            "SOLR_QNTTY": [1, 1],
            "APP_SERV": ["app1sc01", "app111", "app211", "app113", "app213", "app115", "app215", "app117", "app217"],
            "SOLR_SERV": ["srchapp2", "srchapp4"],
            "INS": "prod01"
        }
    elif env_name == "stg":
        env_vars = {
            "APP_HOST": ["stgsrv601"],
            "WEB_HOST": ["stgsrveb601"],
            "SOLR_HOST": ["stgsrch601"],
            "WC_HOST": "stg601",
            "APP_QNTTY": [1],
            "SOLR_QNTTY": [1],
            "APP_SERV": ["server1"],
            "SOLR_SERV": ["srchapp1"],
            "INS": "stg01"
        }
    else:
        raise ValueError(f"Incorrect environment name: {env_name}")

    env_vars.update({
        "WAS": "/usr/opt/app/IBM/WebSphere/AppServer",
        "WASBIN": f"/usr/opt/app/IBM/WebSphere/AppServer/profiles/{env_vars['INS']}/bin",
        "WASLOG": f"/usr/opt/app/IBM/WebSphere/AppServer/profiles/{env_vars['INS']}/logs",
        "SOLRINS": f"{env_vars['INS']}_solr",
        "SOLRBIN": f"/usr/opt/app/IBM/WebSphere/AppServer/profiles/{env_vars['SOLRINS']}/bin",
        "SOLRLOG": f"/usr/opt/app/IBM/WebSphere/AppServer/profiles/{env_vars['SOLRINS']}/logs"
    })

    return env_vars

def chk_status(rc, message, severity):
    """Handle status messages and errors."""
    severity = severity.upper()
    message = f"{severity}: {message} ({rc})"
    
    if severity == "ERROR":
        logging.error(message)
    else:
        logging.info(message)
    
    if rc == 1:
        sys.exit(rc)

def send_alert_mail():
    """Send an alert email."""
    logging.warning("Sending alert email...")
    subprocess.run(['echo', '"Please check PROD Deployment log. Manual action required."', '|', 'mutt', '-s', '"[WARN]: eComm PROD Deployment: Action required"', '<email_list>'])

def was_define(was_type, env_vars):
    """Define WAS-specific variables."""
    if was_type == "solr":
        return {
            "BIN": env_vars['SOLRBIN'],
            "LOGS": env_vars['SOLRLOG'],
            "PS": f"{env_vars['INS']}_search",
            "HOST_LIST": env_vars['SOLR_HOST'],
            "SERV_LIST": env_vars['SOLR_SERV'],
            "QNTTY_LIST": env_vars['SOLR_QNTTY'],
            "CACHE_PORTS": [10116],
            "PROTOCOL": "http"
        }
    elif was_type == "wc":
        return {
            "BIN": env_vars['WASBIN'],
            "LOGS": env_vars['WASLOG'],
            "PS": f"{env_vars['INS']}_node",
            "HOST_LIST": env_vars['APP_HOST'],
            "SERV_LIST": env_vars['APP_SERV'],
            "QNTTY_LIST": env_vars['APP_QNTTY'],
            "CACHE_PORTS": [10117, 10147],
            "PROTOCOL": "https"
        }
    else:
        raise ValueError(f"was_restart: wrong WAS type specified! ({was_type})")

def was_restart(was_type, action, timeout=None, env_vars=None):
    """Restart or manage WAS services."""
    NODE_TIMEOUT = 150
    APP_TIMEOUT = timeout or 900
    logging.info(f"was_restart: Using timeout {APP_TIMEOUT} ms.")

    was_vars = was_define(was_type, env_vars)
    bin_dir = was_vars['BIN']
    host_list = was_vars['HOST_LIST']
    serv_list = was_vars['SERV_LIST']
    qntty_list = was_vars['QNTTY_LIST']

    if action == "stop":
        for i, host in enumerate(host_list):
            logging.info(f"Stopping Node on {host}")
            commands = [f"ssh {host} '{bin_dir}/stopNode.sh > /dev/null 2>&1 &'"]

            for j in range(qntty_list[i]):
                logging.info(f"Stopping App {serv_list[j]}")
                commands.append(f"ssh {host} '{bin_dir}/stopServer.sh {serv_list[j]} > /dev/null 2>&1 &'")

            for command in commands:
                subprocess.run(command, shell=True)

    elif action == "start":
        chk_action_stat("sync_stat", was_vars)
        for host in host_list:
            logging.info(f"Starting Node on {host}")
            subprocess.run(f"ssh {host} '{bin_dir}/startNode.sh > /dev/null 2>&1 &'", shell=True)

        logging.info("Waiting for node agent startup...")
        subprocess.run(f"sleep {NODE_TIMEOUT}", shell=True)

        for i, host in enumerate(host_list):
            logging.info(f"Checking Node agent status on {host}")
            result = subprocess.run(f"ssh {host} 'ps -ef | grep nodeagent | grep {was_vars['PS']}'", shell=True)
            if result.returncode == 0:
                logging.info(f"Node on {host} is running.")
                for j in range(qntty_list[i]):
                    logging.info(f"Starting App {serv_list[j]}")
                    subprocess.run(f"ssh {host} '{bin_dir}/startServer.sh {serv_list[j]} > /dev/null 2>&1 &'", shell=True)
            else:
                logging.error(f"Node on {host} is NOT running. Please check manually.")
                send_alert_mail()

        subprocess.run(f"sleep {APP_TIMEOUT}", shell=True)
        chk_action_stat("app_stat", was_vars)

    elif action == "sync":
        for host in host_list:
            logging.info(f"Checking Node agent status on {host}")
            result = subprocess.run(f"ssh {host} 'ps -ef | grep {was_vars['PS']} | grep -v grep'", shell=True)
            if result.returncode == 1:
                logging.info(f"JVM process on {host} is NOT running. Syncing Node...")
                subprocess.run(f"ssh {host} '{bin_dir}/syncNode.sh {env_vars['WC_HOST']} 8879 > /dev/null 2>&1 &'", shell=True)
            else:
                logging.error(f"Sync cannot be started on {host}. JVM is running!!! Proceed manually.")
                send_alert_mail()

    else:
        raise ValueError(f"was_restart: wrong action specified! ({action})")

def chk_action_stat(action, was_vars):
    """Check Sync/App state."""
    host_list = was_vars['HOST_LIST']
    serv_list = was_vars['SERV_LIST']
    qntty_list = was_vars['QNTTY_LIST']
    ps = was_vars['PS']

    if action == "sync_stat":
        for i, host in enumerate(host_list):
            retry = 0
            while retry < 2:
                logging.info(f"Checking Sync Node process status on {host}")
                process_run = subprocess.run(f"ssh {host} 'ps -ef | grep syncNode.sh | grep -v grep'", shell=True).returncode
                sync_state = subprocess.run(f"ssh {host} 'grep {datetime.now().strftime('%-m/%-d/%y')} {was_vars['LOGS']}/syncNode.log | grep The\ configuration\ synchronization\ completed\ successfully | grep -v grep'", shell=True).returncode
                
                if process_run == 1 and sync_state == 0:
                    logging.info("Sync on {host} completed successfully!")
                    break
                else:
                    logging.warning("Sync on {host} failed or process still running. Retrying...")
                    subprocess.run("sleep 300", shell=True)
                    retry += 1

            if retry == 2:
                logging.error("Sync on {host} failed twice. Please check manually.")
                send_alert_mail()

    elif action == "app_stat":
        for i, host in enumerate(host_list):
            for j in range(qntty_list[i]):
                logging.info(f"Checking JVM status {serv_list[j]} on {host}")
                process_run = subprocess.run(f"ssh {host} 'ps -ef | grep java | grep {ps} | grep {serv_list[j]}'", shell=True).returncode

                if process_run == 0:
                    logging.info(f"JVM {serv_list[j]} on {host} is running!")
                else:
                    logging.error(f"JVM {serv_list[j]} on {host} is NOT running. Please check manually.")
                    send_alert_mail()

    else:
        raise ValueError(f"chk_action_stat: wrong action specified! ({action})")

if __name__ == "__main__":
    # Define environment-specific variables
    env_name = "prd1"  # Example: "prd1", "prd2", or "stg"
    env_vars = define_env(env_name)

    # Example usage
    was_restart("wc", "stop", env_vars=env_vars)
    was_restart("wc", "start", env_vars=env_vars)
    was_restart("solr", "sync", env_vars=env_vars)
