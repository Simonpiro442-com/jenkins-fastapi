pipeline {

    agent any

    environment {

        AWS_REGION = 'us-east-1'

        AWS_ACCOUNT_ID = '047631362165'

        ECR_REPOSITORY = 'fastapi-repo'

        IMAGE_NAME = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

        APP_NAME = 'fastapi-app'

        APP_PORT = '8000'

        DEPLOY_HOST = '3.239.181.234'

        DEPLOY_USER = 'ubuntu'
    }

    stages {

        stage('Checkout') {

            steps {

                echo 'Checking out source code...'

                checkout scm
            }
        }

        stage('Inspect Source') {

            steps {

                sh '''
                    echo "=============================="
                    echo "WORKSPACE"
                    echo "=============================="

                    pwd

                    echo "=============================="
                    echo "FILES"
                    echo "=============================="

                    ls -la

                    echo "=============================="
                    echo "GIT COMMIT"
                    echo "=============================="

                    git rev-parse HEAD
                '''
            }
        }

        stage('Setup Python') {

            steps {

                sh '''
                    python3 --version

                    python3 -m venv venv

                    . venv/bin/activate

                    pip install --upgrade pip

                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {

            steps {

                sh '''
                    . venv/bin/activate

                    pip install ruff

                    ruff check .
                '''
            }
        }

        stage('Unit Tests') {

            steps {

                sh '''
                    . venv/bin/activate

                    pip install pytest

                    pytest -v
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                    echo "Building Docker image..."

                    docker build \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                        -t ${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        stage('Test Docker Container') {

            steps {

                sh '''
                    echo "Starting temporary container..."

                    docker run -d \
                        --name ${APP_NAME}-test \
                        -p ${APP_PORT}:8000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "Waiting for application..."

                    sleep 5

                    echo "Testing application..."

                    curl --fail \
                        http://localhost:${APP_PORT}/

                    echo "Application test passed."

                    docker stop ${APP_NAME}-test

                    docker rm ${APP_NAME}-test
                '''
            }
        }

        stage('Login to ECR') {

            steps {

                sh '''
                    aws ecr get-login-password \
                        --region ${AWS_REGION} \
                        | docker login \
                        --username AWS \
                        --password-stdin \
                        ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                '''
            }
        }

        stage('Push Image') {

            steps {

                sh '''
                    echo "Pushing image to ECR..."

                    docker push ${IMAGE_NAME}:${BUILD_NUMBER}

                    docker push ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Deploy to EC2') {

            steps {

                sshagent(credentials: ['fastapi-ec2-deploy']) {

                    sh '''
                        echo "Deploying application..."

                        ssh \
                            -o StrictHostKeyChecking=no \
                            ${DEPLOY_USER}@${DEPLOY_HOST} \
                            "
                                aws ecr get-login-password \
                                    --region ${AWS_REGION} \
                                | docker login \
                                    --username AWS \
                                    --password-stdin \
                                    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com;

                                docker pull ${IMAGE_NAME}:${BUILD_NUMBER};

                                docker stop ${APP_NAME} || true;

                                docker rm ${APP_NAME} || true;

                                docker run -d \
                                    --name ${APP_NAME} \
                                    --restart unless-stopped \
                                    -p ${APP_PORT}:8000 \
                                    ${IMAGE_NAME}:${BUILD_NUMBER};
                            "
                    '''
                }
            }
        }

        stage('Health Check') {

            steps {

                sshagent(credentials: ['fastapi-ec2-deploy']) {

                    sh '''
                        echo "Checking application health..."

                        sleep 5

                        ssh \
                            -o StrictHostKeyChecking=no \
                            ${DEPLOY_USER}@${DEPLOY_HOST} \
                            "curl --fail http://localhost:${APP_PORT}/"
                    '''
                }
            }
        }
    }

    post {

        success {

            echo '''
            ========================================
            DEPLOYMENT SUCCESSFUL
            ========================================
            '''
        }

        failure {

            echo '''
            ========================================
            PIPELINE FAILED
            ========================================
            '''
        }

        always {

            echo 'Cleaning Jenkins workspace...'

            cleanWs()
        }
    }
}