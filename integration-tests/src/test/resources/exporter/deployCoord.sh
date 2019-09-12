# Copyright 2019, Oracle Corporation and/or its affiliates.  All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at http://oss.oracle.com/licenses/upload
monitoringExporterDir=$1
domainNS=$2
operatorNS=$3
samplesDir=${monitoringExporterDir}/src/samples/kubernetes/deployments
kubectl apply -f ${samplesDir}/monitoring-namespace.yaml
#kubectl apply -f ${samplesDir}/prometheus-deployment.yaml
#kubectl apply -f ${samplesDir}/alertmanager-deployment.yaml
#kubectl apply -f ${samplesDir}/crossnsrbac_${domainNS}_${operatorNS}.yaml
kubectl apply -f ${samplesDir}/coordinator_${domainNS}.yaml

echo "Run the script [deployCoord.sh] ..."
