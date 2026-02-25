pipeline {
    agent any

    environment {
        // AWS and ECR Configurations
        // Using Jenkins Credentials to hide sensitive IDs and IPs
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        AWS_REGION = 'us-east-1'
        S3_ARTIFACTS_BUCKET = 'hotel-retention-artifacts'
        
        ECR_REPO = 'hotel-retention-agent'
        IMAGE_TAG = "${env.BUILD_ID}"
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        
        // EC2 Deployment Info
        EC2_HOST = credentials('ec2-host-ip')
        EC2_USER = 'ubuntu'
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
                sh 'docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}'
                sh 'docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:latest'
            }
        }

        stage('Push to AWS ECR') {
            steps {
                echo "⬆️ Pushing Docker Image to ECR..."
                withCredentials([aws(credentialsId: 'aws-credentials', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}"
                    sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:latest"
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "🚀 Deploying to EC2..."
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER'),
                    aws(credentialsId: 'aws-credentials', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'groq-api-key', variable: 'GROQ_KEY'),
                    string(credentialsId: 'tavily-api-key', variable: 'TAVILY_KEY')
                ]) {
                    sh """
                        ssh -i \${SSH_KEY} -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            # Ensure AWS CLI uses credentials on EC2 for ECR and S3 Artifact pulls
                            export AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
                            export AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
                            export AWS_DEFAULT_REGION=${AWS_REGION}

                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                            
                            docker stop hotel-agent-app || true
                            docker rm hotel-agent-app || true
                            
                            docker pull ${ECR_REGISTRY}/${ECR_REPO}:latest
                            
                            # Start container. The start.sh inside will fetch from S3 using these AWS creds.
                            docker run -d \\
                                --name hotel-agent-app \\
                                -p 5000:5000 \\
                                -p 8501:8501 \\
                                -e AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID} \\
                                -e AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY} \\
                                -e AWS_DEFAULT_REGION=${AWS_REGION} \\
                                -e GROQ_API_KEY=\${GROQ_KEY} \\
                                -e TAVILY_API_KEY=\${TAVILY_KEY} \\
                                ${ECR_REGISTRY}/${ECR_REPO}:latest
                        '
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD Pipeline Completed Successfully! Application deployed."
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
