#!/usr/bin/env bash
set -eu

HELM_PATH=$1
HELM_TEMPLATE_OUTPUT_FILE=all-k8s-docs-tmpl.yaml
HELM_DRYRUN_OUTPUT_FILE=all-k8s-docs-dryrun.yaml

if [[ -z $HELM_PATH ]]; then
    echo "Please provide path to a local helm chart."
    exit 1
fi

echo "Script start"
echo "Using ${HELM_PATH} helmchart to generate kubernetes manifests"
helm template "${HELM_PATH}" >$HELM_TEMPLATE_OUTPUT_FILE
helm install test --dry-run $HELM_PATH >$HELM_DRYRUN_OUTPUT_FILE

~/workspace/venv3.8/bin/python3 /home/michael/workspace/helm-snapper/main.py "${HELM_PATH}" "${HELM_DRYRUN_OUTPUT_FILE}"

echo "Script end"