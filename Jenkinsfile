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

    stages {
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
    }
}

