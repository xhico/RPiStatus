# -*- coding: utf-8 -*-
# !/usr/bin/python3

import datetime
import json
import os
import socket
import traceback
import logging
import subprocess
from Misc import get911, sendEmail


def is_host_reachable(host):
    """
    Check if a host is reachable by pinging it.

    Args:
        host (str): The host to ping.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    try:
        # Use the "ping" command with a count of 1 and a timeout of 2 seconds
        result = subprocess.run(["ping", "-c", str(config["PING_COUNT"]), "-W", str(config["PING_TIMEOUT"]), host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # Check the return code to determine if the ping was successful
        if result.returncode == 0:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


def lastStatus(rpi):
    """
    Get the last recorded status of an RPI.

    Args:
        rpi (str): The name of the RPI.

    Returns:
        bool: True if the last status was 'True' (alive), False otherwise.
    """
    if len(SAVED_INFO) != 0:
        try:
            return SAVED_INFO[0][rpi]
        except Exception:
            logger.error("No " + rpi + " found in SAVED_INFO")
            return False
    return False


def main():
    """
    The main function that checks the status of multiple RPIs and saves the information to a JSON file.
    """
    hostname = str(socket.gethostname()).upper()

    # RPi Uppercase && Remove localhost
    RPIs = [rpi.upper() for rpi in config["RPIs"] if rpi.upper() != hostname]

    # Add timestamp to info
    timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    info = {"timestamp": timestamp}

    # Iterate over every RPi
    for rpi in RPIs:

        # Check if isAlive
        isAlive = is_host_reachable(rpi + ".xhico")
        logger.info(rpi + " | " + str(isAlive))
        info[rpi] = isAlive

        # Send Email
        emailMsg = ""
        if not isAlive and lastStatus(rpi):
            emailMsg = "DOWN" + " - " + rpi + " - " + timestamp
        elif isAlive and not lastStatus(rpi):
            emailMsg = "UP" + " - " + rpi + " - " + timestamp
        if emailMsg != "":
            logger.info("Send Email")
            sendEmail(emailMsg, emailMsg)

    # Saved Info
    global SAVED_INFO
    SAVED_INFO = list(reversed(SAVED_INFO))
    SAVED_INFO.append(info)
    savedInfo = list(reversed(SAVED_INFO))
    with open(savedInfoFile, "w") as outFile:
        json.dump(savedInfo, outFile, indent=2)

    return


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Load configuration from JSON file
    configFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(configFile) as inFile:
        config = json.load(inFile)

    # Load SAVED_INFO from JSON file
    savedInfoFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_info.json")
    if not os.path.exists(savedInfoFile):
        with open(savedInfoFile, "w") as outFile:
            json.dump([], outFile, indent=2)
    with open(savedInfoFile) as inFile:
        SAVED_INFO = json.load(inFile)

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
