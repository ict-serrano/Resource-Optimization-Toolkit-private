pipeline {
    environment {
        PROJECT_NAME = 'serrano-rot-pipeline'
        DEPLOY = "${env.GIT_BRANCH == "origin/main" || env.GIT_BRANCH == "origin/develop" ? "true" : "false"}"
        DEPLOY_UVT = "${env.GIT_BRANCH == "origin/main" ? "true" : "false"}"
        ENGINE = "${env.GIT_BRANCH == "origin/main" ? "serrano-rot-engine" : "serrano-rot-engine-staging"}"
        CONTROLLER = "${env.GIT_BRANCH == "origin/main" ? "serrano-rot-controller" : "serrano-rot-controller-staging"}"
        VERSION = '0.1'
        DOMAIN = 'localhost'
        REGISTRY = 'serrano-harbor.rid-intrasoft.eu/serrano/serrano-rot-pipeline'
        REGISTRY_URL = 'https://serrano-harbor.rid-intrasoft.eu/serrano'
        REGISTRY_CREDENTIAL = 'harbor-jenkins'
        UVT_KUBERNETES_PUBLIC_ADDRESS = 'api.k8s.cloud.ict-serrano.eu'
        INTEGRATION_OPERATOR_TOKEN = credentials('uvt-integration-operator-token')
        PORT = "10020"
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
                    sh 'pip3 install -r requirements.txt'
                    sh 'pip3 install Flask -U'
                    sh 'pip3 install --no-input cyclonedx-bom'
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
        stage('Deploy Rot Engine in INTRA Kubernetes') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm upgrade --install --force --wait --timeout 600s --namespace integration --set name=${ENGINE} --set image.tag=${VERSION} --set domain=${DOMAIN} ${ENGINE} ./helm/engine"
                }
            }
        }
        stage('Deploy Rot Controller in INTRA Kubernetes') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm upgrade --install --force --wait --timeout 600s --namespace integration --set name=${CONTROLLER} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CONTROLLER} ./helm/controller"
                }
            }
        }
        stage('Integration Tests') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('python') {
                    sh "python -u /home/jenkins/agent/workspace/serrano-rot-pipeline/unittest/unit_test.py"  
                }
            }
        }
        stage('Cleanup INTRA Deployment') {
            when {
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                container('helm') {
                    sh "helm uninstall ${ENGINE} --namespace integration"
                    sh "helm uninstall ${CONTROLLER} --namespace integration"
                    sh "rm -rf deployments"
                }
            }
        }
        /*stage('Deploy ROT Engine in UVT Kubernetes') {
            when {
                environment name: 'DEPLOY_UVT', value: 'true'
            }
            steps {
                container('helm') {
                    sh "kubectl config set-cluster kubernetes-uvt --certificate-authority=uvt.cer --embed-certs=true --server=https://${UVT_KUBERNETES_PUBLIC_ADDRESS}:6443"
                    sh "kubectl config set-credentials integration-operator --token=${INTEGRATION_OPERATOR_TOKEN}"
                    sh "kubectl config set-context kubernetes-uvt --cluster=kubernetes-uvt --user=integration-operator"
                    sh "helm upgrade --install --force --wait --timeout 600s --kube-context=kubernetes-uvt --namespace integration --set name=${ENGINE} --set image.tag=${VERSION} --set domain=${DOMAIN} ${ENGINE} ./helm-uvt/engine"
                }
            }
        }
        stage('Deploy ROT Controller in UVT Kubernetes') {
            when {
                environment name: 'DEPLOY_UVT', value: 'true'
            }
            steps {
                container('helm') {
                    sh "kubectl config set-cluster kubernetes-uvt --certificate-authority=uvt.cer --embed-certs=true --server=https://${UVT_KUBERNETES_PUBLIC_ADDRESS}:6443"
                    sh "kubectl config set-credentials integration-operator --token=${INTEGRATION_OPERATOR_TOKEN}"
                    sh "kubectl config set-context kubernetes-uvt --cluster=kubernetes-uvt --user=integration-operator"
                    sh "helm upgrade --install --force --wait --timeout 600s --kube-context=kubernetes-uvt --namespace integration --set name=${CONTROLLER} --set image.tag=${VERSION} --set domain=${DOMAIN} ${CONTROLLER} ./helm-uvt/controller"
                }
            }
        }*/
    }
}