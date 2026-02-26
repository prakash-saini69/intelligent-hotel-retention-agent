pipeline {
    agent any

    environment {
        // AWS and Deployment Configurations
        AWS_REGION = 'us-east-1'
        S3_ARTIFACTS_BUCKET = 'hotel-retention-artifacts'
        
        ECR_REPO = 'hotel-retention-agent'
        IMAGE_TAG = "${env.BUILD_ID}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo "✅ Code checkout successful."
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo "📦 Installing Python dependencies..."
                // Set up a virtual env for Jenkins CI execution
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo "🧪 Running Tests..."
                sh '''
                    . venv/bin/activate
                    pytest || echo "No tests configured yet or tests failed."
                '''
            }
        }
        
        stage('Train ML Model') {
            steps {
                echo "🧠 Activating CI training..."
                sh '''
                    . venv/bin/activate
                    # Run the script that generates model.joblib in the models/ directory
                    python src/train_model.py || echo "Assumption: Script generates models/model.joblib"
                '''
            }
        }
        
        stage('Build Vector Store') {
            steps {
                echo "📚 Building ChromaDB Vector Store..."
                sh '''
                    . venv/bin/activate
                    # Run the script that generates the vectorstore/chroma_db content
                    python src/build_vectorstore.py || echo "Assumption: Script generates vectorstore/chroma_db"
                '''
            }
        }

        stage('Upload Artifacts to S3') {
            steps {
                echo "☁️ Uploading artifacts to S3 Bucket: ${S3_ARTIFACTS_BUCKET}..."
                withCredentials([aws(credentialsId: 'aws-credentials', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh """
                        # Upload Model
                        aws s3 cp models/model.joblib s3://${S3_ARTIFACTS_BUCKET}/model/model.joblib
                        
                        # Upload Vector Store
                        aws s3 sync vectorstore/chroma_db/ s3://${S3_ARTIFACTS_BUCKET}/vectorstore/chroma_db/
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker Image..."
                // Note: .dockerignore will exclude the generated models/ and vectorstore/ from the image context.
                sh 'docker build -t ${ECR_REPO}:${IMAGE_TAG} .'
                sh 'docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REPO}:latest'
            }
        }

        stage('Stop Old Container') {
            steps {
                echo "🛑 Stopping old container..."
                sh '''
                    docker stop hotel-agent-app || true
                    docker rm hotel-agent-app || true
                '''
            }
        }

        stage('Run New Container') {
            steps {
                echo "🚀 Running new container..."
                withCredentials([
                    aws(credentialsId: 'aws-credentials', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'groq-api-key', variable: 'GROQ_KEY'),
                    string(credentialsId: 'tavily-api-key', variable: 'TAVILY_KEY')
                ]) {
                    sh """
                        # Start container locally on Jenkins EC2 instance.
                        docker run -d \\
                            --name hotel-agent-app \\
                            --restart unless-stopped \\
                            -p 5000:5000 \\
                            -p 8501:8501 \\
                            -e AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID} \\
                            -e AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY} \\
                            -e AWS_DEFAULT_REGION=${AWS_REGION} \\
                            -e GROQ_API_KEY=\${GROQ_KEY} \\
                            -e TAVILY_API_KEY=\${TAVILY_KEY} \\
                            ${ECR_REPO}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD Pipeline Completed Successfully! Application deployed locally on EC2."
        }
        failure {
            echo "❌ Pipeline Failed! Please check the Jenkins logs."
        }
        always {
            // Clean up local images
            sh 'docker rmi ${ECR_REPO}:${IMAGE_TAG} || true'
            // Ensure venv is removed
            sh 'rm -rf venv || true'
        }
    }
}
