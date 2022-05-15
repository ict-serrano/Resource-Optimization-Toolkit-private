import os
import time
import uuid
import logging
import sqlite3


from serrano_rot.utils.enums import ExecutionStatus
import serrano_rot.controller.dbFormatter as dbFormatter

from flask import Flask
from flask import request
from flask import jsonify
from flask import make_response

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

logger = logging.getLogger('SERRANO.ROT.AccessInterface')


class AccessInterface(QThread):

    restInterfaceMessage = pyqtSignal(object)

    def __init__(self, config):

        QThread.__init__(self)

        self.address = config["address"]
        self.port = config["port"]

        self.rest_app = Flask(__name__)

        logger.info("AccessInterface is ready ...")

        auth = HTTPBasicAuth()

        self.db = "%s/.rot/rot.db" % os.path.expanduser("~")

        @auth.verify_password
        def verify_password(username, password):
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password,))
                row = cur.fetchone()
                if row is not None:
                    return username

        @auth.error_handler
        def unauthorized():
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

        @self.rest_app.route("/api/v1/rot/history", methods=["GET"])
        @auth.login_required
        def execution_history():
            data = []
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT client_uuid FROM users WHERE username = ?", (request.authorization.username,))
                client_uuid = cur.fetchone()[0]
                cur.execute("SELECT * FROM executions WHERE client_uuid = ?", (client_uuid,))
                for row in cur.fetchall():
                    data.append(dbFormatter.ExecutionRow(row).to_dict())
            return make_response(jsonify({"executions": data}), 200)

        @self.rest_app.route("/api/v1/rot/executions", methods=["GET"])
        @auth.login_required
        def executions():
            data = []
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT client_uuid FROM users WHERE username = ?", (request.authorization.username,))
                client_uuid = cur.fetchone()[0]
                cur.execute("SELECT * FROM executions WHERE (status = ? or status = ?) AND client_uuid = ?",
                            (ExecutionStatus.PENDING, ExecutionStatus.STARTED, client_uuid))
                for row in cur.fetchall():
                    data.append(dbFormatter.ExecutionRow(row).to_dict())
            return make_response(jsonify({"executions": data}), 200)

        @self.rest_app.route("/api/v1/rot/execution/<uuid:execution_id>", methods=["GET", "DELETE"])
        @auth.login_required
        def execution_details(execution_id):
            if request.method == "GET":
                data = {}
                with sqlite3.connect(self.db) as con:
                    print(execution_id)
                    cur = con.cursor()
                    cur.execute("SELECT * FROM executions WHERE execution_id = ?", (str(execution_id),))
                    row = cur.fetchone()
                    if row is not None:
                        data = dbFormatter.ExecutionRow(row).to_dict()
                return make_response(jsonify(data), 200)

            elif request.method == "DELETE":
                print(execution_id)
                self.restInterfaceMessage.emit({"cmd": "terminate", "execution_id": execution_id})
                return make_response(jsonify({}), 200)

        @self.rest_app.route("/api/v1/rot/execution", methods=["POST"])
        @auth.login_required
        def start_execution():
            execution_id = str(uuid.uuid4())
            logger.info("Incoming request for new execution. Assigned UUID: %s" % execution_id)
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                # Check if there are available engines
                cur.execute("SELECT count(*) FROM engines WHERE active = 1")
                at = int(time.time())
                if cur.fetchone()[0] > 0:
                    execution_status = ExecutionStatus.PENDING
                    request_status = "Accepted"
                    log_entry = "Valid request, forward it to Dispatcher"
                    logger.info("Request %s is accepted" % execution_id)
                else:
                    execution_status = ExecutionStatus.FAILED
                    request_status = "Rejected"
                    log_entry = "There is no execution engine available."
                    logger.info("Request %s is rejected" % execution_id)

                cur.execute("SELECT client_uuid FROM users WHERE username = ?", (request.authorization.username,))
                client_uuid = cur.fetchone()[0]

                cur.execute("INSERT INTO executions(execution_id,client_uuid,status,created_at,updated_at) VALUES "
                            "(?,?,?,?,?)", (execution_id, client_uuid, execution_status, at, at,))
                con.commit()
                cur.execute("INSERT INTO logs(execution_id,created_at,log_by,log_entry) VALUES "
                            "(?,?,?,?)", (execution_id, at, "AccessInterface", log_entry,))
                con.commit()

            self.restInterfaceMessage.emit({"cmd": "create", "execution_id": execution_id, "client_uuid": client_uuid,
                                            "request_params": request.json})
            return make_response(jsonify({"execution_id": execution_id, "status": request_status}), 200)

        @self.rest_app.route("/api/v1/rot/statistics", methods=["GET"])
        @auth.login_required
        def execution_statistics():
            return make_response(jsonify({}), 200)

        @self.rest_app.route("/api/v1/rot/engines", methods=["GET"])
        @auth.login_required
        def active_engines():
            data = []
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT id FROM engines WHERE active = 1")
                for row in cur.fetchall():
                    data.append(row[0])
            return make_response(jsonify({"engines": data}), 200)

        @self.rest_app.route("/api/v1/rot/engine/<uuid:engine_id>", methods=["GET"])
        @auth.login_required
        def engine_details(engine_id):
            data = {}
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM engines WHERE id = ?", (str(engine_id),))
                row = cur.fetchone()
                if row is not None:
                    data = dbFormatter.EngineRow(row).to_dict()
            return make_response(jsonify(data), 200)

        @self.rest_app.route("/api/v1/rot/logs/<uuid:execution_id>", methods=["GET"])
        @auth.login_required
        def execution_logs(execution_id):
            data = []
            with sqlite3.connect(self.db) as con:
                cur = con.cursor()
                cur.execute("SELECT log_by,log_entry,created_at FROM logs WHERE execution_id = ?", (str(execution_id),))
                for row in cur.fetchall():
                    data.append(dbFormatter.LogRow(row).to_dict())
            return make_response(jsonify({"log_details": data}), 200)

    def __del__(self):
        self.wait()

    def run(self):
        logger.info("AccessInterface is running ...")

        self.rest_app.run(host=self.address, port=self.port, debug=False)
