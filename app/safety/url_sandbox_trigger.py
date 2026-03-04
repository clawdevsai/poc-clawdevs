#!/usr/bin/env python3
"""
Serviço HTTP que dispara o Job url-sandbox no cluster (patch security-config + delete/create Job).
Usado pelo Cloudflare Worker (Cron) para automatizar fetch de URL agendado.
Rota: POST /trigger com {"url": "https://..."} e opcional Authorization: Bearer <TRIGGER_SECRET>.
"""
from __future__ import annotations

import os
import sys
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Instale flask: pip install flask", file=sys.stderr)
    sys.exit(1)

try:
    from kubernetes import client, config
except ImportError:
    print("Instale kubernetes: pip install kubernetes", file=sys.stderr)
    sys.exit(1)

NAMESPACE = os.environ.get("NAMESPACE", "ai-agents")
CONFIGMAP_NAME = "security-config"
JOB_NAME = "url-sandbox"
TRIGGER_SECRET = os.environ.get("TRIGGER_SECRET", "")

app = Flask(__name__)


def _load_k8s():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.CoreV1Api(), client.BatchV1Api()


def _check_auth():
    if not TRIGGER_SECRET:
        return True
    auth = request.headers.get("Authorization") or request.headers.get("X-API-Key")
    if not auth:
        return False
    if auth.startswith("Bearer "):
        return auth[7:] == TRIGGER_SECRET
    return auth == TRIGGER_SECRET


def _valid_url(url: str) -> bool:
    if not url or not url.strip():
        return False
    u = url.strip()
    return u.startswith("http://") or u.startswith("https://")


@app.route("/health", methods=["GET"])
def health():
    return "", 200


@app.route("/trigger", methods=["POST"])
def trigger():
    if not _check_auth():
        return jsonify({"error": "unauthorized"}), 401

    url = None
    if request.is_json and request.json:
        url = request.json.get("url") or request.json.get("URL_SANDBOX_TARGET")
    if not url:
        url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing url (body {\"url\": \"...\"} or query ?url=...)"}), 400

    url = url.strip()
    if not _valid_url(url):
        return jsonify({"error": "invalid url (must be http:// or https://)"}), 400

    try:
        v1, batch = _load_k8s()
    except Exception as e:
        return jsonify({"error": f"k8s config: {e}"}), 500

    # 1) Patch ConfigMap security-config
    try:
        body = {"data": {"URL_SANDBOX_TARGET": url}}
        v1.patch_namespaced_config_map(CONFIGMAP_NAME, NAMESPACE, body)
    except Exception as e:
        return jsonify({"error": f"patch configmap: {e}"}), 500

    # 2) Delete Job if exists
    try:
        batch.delete_namespaced_job(JOB_NAME, NAMESPACE, propagation_policy="Background")
    except client.rest.ApiException as e:
        if e.status != 404:
            return jsonify({"error": f"delete job: {e}"}), 500

    # 3) Create Job (spec from embedded YAML)
    job_body = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": JOB_NAME, "namespace": NAMESPACE, "labels": {"app": "url-sandbox"}},
        "spec": {
            "ttlSecondsAfterFinished": 600,
            "backoffLimit": 0,
            "template": {
                "metadata": {"labels": {"app": "url-sandbox"}},
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "fetch",
                            "image": "python:3.12-slim",
                            "command": ["python", "/scripts/url_sandbox_fetch.py"],
                            "envFrom": [{"configMapRef": {"name": "security-config", "optional": True}}],
                            "env": [{"name": "REDIS_HOST", "value": "redis-service.ai-agents.svc.cluster.local"}],
                            "volumeMounts": [
                                {"name": "scripts", "mountPath": "/scripts", "readOnly": True},
                                {"name": "output", "mountPath": "/tmp"},
                            ],
                            "resources": {"limits": {"memory": "128Mi", "cpu": "100m"}},
                        }
                    ],
                    "volumes": [
                        {"name": "scripts", "configMap": {"name": "url-sandbox-scripts", "optional": True}},
                        {"name": "output", "emptyDir": {}},
                    ],
                },
            },
        },
    }
    try:
        batch.create_namespaced_job(NAMESPACE, job_body)
    except Exception as e:
        return jsonify({"error": f"create job: {e}"}), 500

    return jsonify({"ok": True, "url": url, "job": JOB_NAME}), 200


def main():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
