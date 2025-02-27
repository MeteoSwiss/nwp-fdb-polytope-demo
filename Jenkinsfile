class Globals {
    // constants
    static final String PROJECT = 'nwp-fdb-polytope-demo'
}

@Library('dev_tools@main') _
pipeline {
    agent { label 'podman' }

    options {
        // New jobs should wait until older jobs are finished
        disableConcurrentBuilds()
        // Discard old builds
        buildDiscarder(logRotator(artifactDaysToKeepStr: '7', artifactNumToKeepStr: '1', daysToKeepStr: '45', numToKeepStr: '10'))
        // Timeout the pipeline build after 1 hour
        timeout(time: 1, unit: 'HOURS')
    }

    parameters {
        booleanParam(name: 'PUSH_IMAGES_TO_NEXUS', defaultValue: false, description: 'Push images to Nexus?')
    }

    environment { 
        TAG = "${sh(script: "echo `date +%g%m.$GIT_COMMIT`", returnStdout: true).trim()}"

        IMAGE_TAG = "numericalweatherpredictions/polytope/demo/notebook:$TAG"
        INTERNAL_IMAGE_TAG = "docker-intern-nexus.meteoswiss.ch/$IMAGE_TAG"
        PUBLIC_IMAGE_TAG = "docker-public-nexus.meteoswiss.ch/$IMAGE_TAG"
        HTTP_PROXY = "http://proxy.meteoswiss.ch:8080/"
    }

    stages {
        stage('Podman version') {
            steps {
                sh '''
                    #!/bin/bash 
                    podman version
                '''
            }
        }
        stage('Presubmit Test') {
            steps {
                script { 
                    runWithPodman(
                        'docker-all-nexus.meteoswiss.ch/jupyter/minimal-notebook:python-3.11',
                        '''
                        mkdir /home/jovyan/notebooks &&
                        cp notebooks/*ipynb /home/jovyan/notebooks &&
                        cp verify_clear.sh /home/jovyan &&
                        cd /home/jovyan &&
                        sh verify_clear.sh
                        '''
                    )
                }
            }
        }
        stage('Build demo notebook image'){
            steps{
                sh '''
                    #!/bin/bash
                    podman build -f Dockerfile.notebooks \
                        -t $IMAGE_TAG \
                        --build-arg container_registry=docker-all-nexus.meteoswiss.ch \
                        --format docker \
                        .
                    
                    podman tag $IMAGE_TAG $INTERNAL_IMAGE_TAG
                    podman tag $IMAGE_TAG $PUBLIC_IMAGE_TAG
                '''
            }
        }
        stage('Tag & push image') {
            when { 
                anyOf{
                    branch "main"
                    expression { return params.PUSH_IMAGES_TO_NEXUS }
                } 
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'openshift-nexus',
                                    passwordVariable: 'NXPASS',
                                    usernameVariable: 'NXUSER')]) {
                    sh '''
                        podman login docker-intern-nexus.meteoswiss.ch -u $NXUSER -p $NXPASS
                        podman login docker-public-nexus.meteoswiss.ch -u $NXUSER -p $NXPASS

                        podman push $INTERNAL_IMAGE_TAG
                        podman push $PUBLIC_IMAGE_TAG
                    '''
                }
            } 
        } 
    }

    post {
        failure {
            echo 'Sending email'
            emailext(subject: "${currentBuild.fullDisplayName}: ${currentBuild.currentResult}",
                attachLog: true,
                attachmentsPattern: 'generatedFile.txt',
                body: "Job '${env.JOB_NAME} #${env.BUILD_NUMBER}': ${env.BUILD_URL}",
                recipientProviders: [requestor(), developers()])
        }
        success {
            echo 'Build succeeded'
        }
        cleanup {
            sh '''
                podman image rm -f $IMAGE_TAG
                podman image rm -f $INTERNAL_IMAGE_TAG
                podman image rm -f $PUBLIC_IMAGE_TAG

                podman logout docker-intern-nexus.meteoswiss.ch || true
                podman logout docker-public-nexus.meteoswiss.ch || true
            '''
        }
    }
}

