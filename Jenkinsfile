class Globals {
    static String mchbuildPipPackage = 'mchbuild>=1.0.0,<2.0.0'
    static String VAULT_URL = 'https://secrets.apps-svcz.prod.cp1.meteoswiss.ch'
    static String PIP_INDEX_URL = 'https://hub.meteoswiss.ch/nexus/repository/python-all/simple'
}

pipeline {
    agent { label 'podman' }

    triggers {
        cron('TZ=UTC\n30 3 * * *')  // Daily at 3:30 UTC
    }

    environment {
        PATH = "$workspace/.venv-mchbuild/bin:$PATH"
        HTTP_PROXY = 'http://proxy.meteoswiss.ch:8080'
        HTTPS_PROXY = 'http://proxy.meteoswiss.ch:8080'
        NO_PROXY = '.meteoswiss.ch,localhost,.cscs.ch'
    }

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(artifactDaysToKeepStr: '7', numToKeepStr: '10', daysToKeepStr: '45'))
        timeout(time: 1, unit: 'HOURS')
    }

    stages {
        stage('Setup') {
            steps {
                sh """
                    python -m venv .venv-mchbuild
                    PIP_INDEX_URL=${Globals.PIP_INDEX_URL} \
                        .venv-mchbuild/bin/pip install --upgrade "${Globals.mchbuildPipPackage}"
                """
            }
        }

        stage('Test Polytope Notebooks') {
            steps {
                script {
                    def solution = sh(script: '.venv-mchbuild/bin/mchbuild -g project', returnStdout: true).trim()

                    withVault(
                        configuration: [
                            vaultUrl: Globals.VAULT_URL,
                            vaultCredentialId: "polytope-vault-approle",
                            engineVersion: 2
                        ],
                        vaultSecrets: [[
                            path: "mch/polytope/polytope-prod-secrets", engineVersion: 2, secretValues: [
                                [envVar: 'POLYTOPE_USER_KEY', vaultKey: 'polytope-validation-user-key'],
                                [envVar: 'POLYTOPE_ADDRESS', vaultKey: 'polytope-validation-url']
                            ]
                        ]]
                    ) {
                        // mchbuild collapses every non-zero exit to 1, so we can't
                        // tell an orange run from a red one by exit code. check_notebooks.py
                        // writes the authoritative outcome to validation_status.txt instead.
                        sh 'rm -f validation_status.txt'
                        def exitCode = sh(
                            script: '.venv-mchbuild/bin/mchbuild test.notebooks_execution',
                            returnStatus: true
                        )
                        def status = fileExists('validation_status.txt')
                            ? readFile('validation_status.txt').trim()
                            : 'FAILURE'
                        echo "Notebook validation outcome: ${status}"

                        if (status == 'UNSTABLE') {
                            unstable('Some notebooks could not run: forecast not yet available in FDB')
                        } else if (status != 'SUCCESS') {
                            error("Notebook validation failed (mchbuild exit ${exitCode})")
                        }
                    }
                }
            }
        }
    }

    post {
        failure {
            emailext(
                subject: "Notebook validation failed: ${env.JOB_BASE_NAME}",
                attachLog: true,
                body: "Pipeline failed: ${env.BUILD_URL}",
                to: env.BRANCH_NAME == 'main' ? "p_polytope@meteoswiss.ch" : "",
                recipientProviders: [requestor(), developers()]
            )
        }
        cleanup { deleteDir() }
    }
}
