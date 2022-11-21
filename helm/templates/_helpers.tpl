{{/*
Expand the name of the chart.
*/}}
{{- define "serrano-rot-pipeline.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "serrano-rot-pipeline.fullname" -}}
{{- "serrano-rot-pipeline" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "serrano-rot-pipeline.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "serrano-rot-pipeline.selectorLabels" -}}
{{- "serrano-rot-pipeline" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "serrano-rot-pipeline.labels" -}}
{{- "serrano-rot-pipeline" }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "serrano-rot-pipeline.serviceAccountName" -}}
{{- "serrano-rot-pipeline" }}
{{- end }}
