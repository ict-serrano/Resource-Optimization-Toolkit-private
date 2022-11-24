{{/*
Expand the name of the chart.
*/}}
{{- define "serrano-rot-controller.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "serrano-rot-controller.fullname" -}}
{{"serrano-rot-controller" -}}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "serrano-rot-controller.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "serrano-rot-controller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "serrano-rot-controller.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "serrano-rot-controller.labels" -}}
helm.sh/chart: {{ include "serrano-rot-controller.chart" . }}
{{ include "serrano-rot-controller.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "serrano-rot-controller.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "serrano-rot-controller.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}