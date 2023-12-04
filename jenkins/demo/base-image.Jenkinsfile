pipeline {
    agent { label 'podman'}

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(artifactDaysToKeepStr: '7', artifactNumToKeepStr: '5', daysToKeepStr: '7', numToKeepStr: '5'))
        timeout(time: 48, unit: 'HOURS')
    }

    parameters {
        booleanParam(name: 'PUSH_IMAGES_TO_NEXUS', defaultValue: false, description: 'Push images to Nexus?')
    }

    environment { 
        TAG = "${sh(script: "echo `date +%g%m.$GIT_COMMIT`", returnStdout: true).trim()}"

        IMAGE_TAG = "numericalweatherpredictions/polytope/demo/base:$TAG"
        INTERNAL_IMAGE_TAG = "docker-intern-nexus.meteoswiss.ch/$IMAGE_TAG"
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
        stage('Build demo/base base image'){
            steps{
                sh '''
                    #!/bin/bash
                    podman build -f demo/base-image/Dockerfile \
                        -t $IMAGE_TAG \
                        --build-arg container_registry=docker-all-nexus.meteoswiss.ch \
                        --build-arg http_proxy='http://proxy.meteoswiss.ch:8080/' \
                        --build-arg https_proxy='http://proxy.meteoswiss.ch:8080/' \
                        --build-arg no_proxy=.meteoswiss.ch,localhost,localaddress,127.0.0.1 \
                        --format docker \
                        .
                    
                    podman tag $IMAGE_TAG $INTERNAL_IMAGE_TAG
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

                        podman push $INTERNAL_IMAGE_TAG
                    '''
                }
            } 
            
        } 
    }
    post { 
        cleanup {
            sh '''
                podman image rm -f $IMAGE_TAG
                podman image rm -f $INTERNAL_IMAGE_TAG

                podman logout docker-intern-nexus.meteoswiss.ch || true
            '''
        }
    }
}
