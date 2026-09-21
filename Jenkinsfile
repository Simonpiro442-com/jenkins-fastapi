pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository has been checked out by Jenkins'
            }
        }

        stage('Show Files') {
            steps {
                sh '''
                    echo "Current directory:"
                    pwd

                    echo "Repository contents:"
                    ls -la
                '''
            }
        }
    }
}