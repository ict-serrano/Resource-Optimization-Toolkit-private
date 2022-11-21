{{/*
Expand the name of the chart.
*/}}
{{- define "serrano-rot-pipeline.name" -}}
{{- "serrano-rot-pipeline" }}
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
app.kubernetes.io/name: {{ include "serrano-rot-pipeline.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "serrano-rot-pipeline.labels" -}}
helm.sh/chart: {{ include "serrano-rot-pipeline.fullname" . }}
{{ include "serrano-rot-pipeline.selectorLabels" . }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "serrano-rot-pipeline.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "serrano-rot-pipeline.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
