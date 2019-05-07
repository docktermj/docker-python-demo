#!/usr/bin/env python

import os
import signal
import sys
import time
import json

from flask import Flask, render_template
app = Flask(__name__)


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

try:
    from G2Module import G2Module
    from G2AnonModule import G2AnonModule
    from G2AuditModule import G2AuditModule
    from G2ProductModule import G2ProductModule
except:
    print("ERROR: Could not import G2Module, G2AnonModule, G2AuditModule, or G2ProductModule")
    print("Possible causes:")
    print("    SENZING_DIR not available.")
    print("    PYTHONPATH environment variable not set correctly.")
    print("    LD_LIBRARY_PATH environment variable not set correctly.")
    print("Ctrl-C to exit")
    time.sleep(3600)
    sys.exit(0)

# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

debug = False

# Establish directories and paths

senzing_directory = os.environ.get("SENZING_DIR", "/opt/senzing")
senzing_python_directory = "{0}/g2/python".format(senzing_directory)
g2module_ini_pathname = "{0}/G2Module.ini".format(senzing_python_directory)

# Add python directory to System Path

sys.path.append(senzing_python_directory)

# Initialize Senzing G2 modules.

g2_module = G2Module('pyG2', g2module_ini_pathname, debug)
g2_module.init()

g2_audit_module = G2AuditModule('pyG2Audit', g2module_ini_pathname, debug)
g2_audit_module.init()

g2_product_module = G2ProductModule('pyG2Product', g2module_ini_pathname, debug)
g2_product_module.init()

# -----------------------------------------------------------------------------
# @app.routes
# -----------------------------------------------------------------------------


@app.route("/")
def app_root():

    # Pretty print (sort and indent)

    version_string = g2_product_module.version()
    version_dictionary = json.loads(version_string)
    version = json.dumps(version_dictionary, sort_keys=True, indent=4)

    license_string = g2_product_module.license()
    license_dictionary = json.loads(license_string)
    license = json.dumps(license_dictionary, sort_keys=True, indent=4)

    config_string = g2_module.exportConfig()
    config_dictionary = json.loads(config_string)
    config = json.dumps(config_dictionary, sort_keys=True, indent=4)

    summary_dictionary = g2_audit_module.getSummaryData()
    summary = json.dumps(summary_dictionary, sort_keys=True, indent=4)

    return render_template("index.html", version=version, config=config, summary=summary, license=license)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    app.run()

