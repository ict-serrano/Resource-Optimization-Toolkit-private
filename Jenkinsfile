pipeline {
    environment {
        PROJECT_NAME = 'serrano-rot-pipeline'
        DEPLOY = "${env.GIT_BRANCH == "origin/main" || env.GIT_BRANCH == "origin/develop" ? "true" : "false"}"
        DEPLOY_UVT = "${env.GIT_BRANCH == "origin/main" ? "true" : "false"}"
        CHART_NAME = "${env.GIT_BRANCH == "origin/main" ? "serrano-rot" : "serrano-rot-staging"}"
        VERSION = '0.1'
        DOMAIN = 'localhost'
        REGISTRY = 'serrano-harbor.rid-intrasoft.eu/serrano/serrano-rot'
        REGISTRY_URL = 'https://serrano-harbor.rid-intrasoft.eu/serrano'
        REGISTRY_CREDENTIAL = 'harbor-jenkins'
        UVT_KUBERNETES_PUBLIC_ADDRESS = 'k8s.serrano.cs.uvt.ro'
        INTEGRATION_OPERATOR_TOKEN = credentials('uvt-integration-operator-token')
    }
    agent {
        kubernetes {
            cloud 'kubernetes'
            defaultContainer 'jnlp'
            yamlFile 'build.yaml'
        }
    }
    stages {
        stage('Install requirements') {
            steps {
                container('python') {
                    sh '/usr/local/bin/python -m pip install --upgrade pip'
                    sh 'pip install -r requirements.txt'
                    sh 'pip install --no-input cyclonedx-bom'
                }
            }
        }
        stage('Unit tests') {
            steps {
                container('python') {
                    sh 'python -m unittest serrano_rot.tests'
                }
            }
        }
        stage('Sonarqube') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                container('java') {
                    withSonarQubeEnv('sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=${PROJECT_NAME}"
                    }
                    timeout(time: 10, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }
        stage('Generate BOM') {
            steps {
                container('python') {
                    sh 'cyclonedx-bom -e -F -o ./bom.xml'
                }
            }
        }
        stage('Dependency Track') {
            steps {
                container('python') {
                    dependencyTrackPublisher artifact: 'bom.xml', projectId: '39acd708-1e14-405e-932e-0af81c96554f', synchronous: true
                }
            }
        }
        stage('Docker Build') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    sh "docker build -t ${REGISTRY}:${VERSION} ."
                }
            }
        }
        stage('Docker Publish') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('docker') {
                    withDockerRegistry([credentialsId: "${REGISTRY_CREDENTIAL}", url: "${REGISTRY_URL}"]) {
                        sh "docker push ${REGISTRY}:${VERSION}"
                    }
                }
            }
        }
        /*
        stage('Deploy in INTRA Kubernetes') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm upgrade --install --force --wait --timeout 600s --namespace integration --set name=${CHART_NAME} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CHART_NAME} ./helm"
                }
            }
        }
        stage('Integration Tests') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {

            }
        }
        stage('Cleanup INTRA Deployment') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm uninstall ${CHART_NAME} --namespace integration"
                }
            }
        }
        */
    }
}
