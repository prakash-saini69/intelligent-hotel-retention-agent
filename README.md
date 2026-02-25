<div align="center">
  <img src="https://img.icons8.com/color/96/five-star-hotel.png" alt="Hotel Icon" width="80"/>
  <h1>Intelligent Hotel Retention Agent 🏨💡</h1>
  <p><b>AI-Powered Customer Retention & Churn Prevention System</b></p>
</div>

---

## 📌 Introduction
The **Intelligent Hotel Retention Agent** is a comprehensive, AI-driven solution designed to predict customer churn, identify at-risk guests, and proactively offer personalized retention packages. 

By unifying **Machine Learning (ML)**, **Retrieval-Augmented Generation (RAG)**, and an autonomous **LangGraph Agent**, this platform empowers hotel administrators to make data-backed decisions instantly and retain valuable customers.

## 📸 System Interface (Demo)

### 1. Main Chat Interface
![Chat Interface](demo/img1.png)

### 2. Agent Tool Usage & Retention Flow
![Risk Evaluation](demo/img2.png)

### 3.human  approval 
![Retention Options](demo/img3.png)

### 4. send retention email
![Retention Options](demo/img4.png)


*(Note: The `demo/` folder contains screenshots of the working Streamlit UI and Admin flow.)*

---

## 🏗️ How It Works (Project Architecture)

Our system is composed of several advanced pipelines working in tandem:

### 1. The Machine Learning (ML) Pipeline 🧠
*   **Purpose:** Predicts whether a customer is likely to cancel their booking or stop using the hotel services (Churn).
*   **Workflow:**
    *   Ingests historical booking data and customer profiles.
    *   Trains a **Random Forest / XGBoost** model.
    *   Generates a lightweight `model.joblib` artifact used for real-time inference.
*   **Outcome:** Assigns a "Risk Score" (Low/Medium/High) to specific customers when queried by the Agent.

### 2. The RAG Pipeline (Retrieval-Augmented Generation) 📚
*   **Purpose:** Provides the LLM with context regarding the hotel's static retention policies, room upgrade guidelines, and discount tiers.
*   **Workflow:**
    *   Parses PDF documents (e.g., `Retention_Policies.pdf`).
    *   Generates embeddings using HuggingFace models.
    *   Stores embeddings in a local **ChromaDB** vector database.
*   **Outcome:** Allows the Agent to accurately quote hotel rules without generating hallucinations.

### 3. The Autonomous Agent Pipeline 🤖 (LangGraph)
*   **Purpose:** The central "brain" orchestrating the user's requests.
*   **Workflow:**
    *   Powered by **Llama3 (via Groq API)** for ultra-fast reasoning.
    *   Built using **LangGraph** to manage state and tool execution.
    *   Can trigger a suite of tools:
        *   📊 `get_customer_risk_score` (Queries the ML Model)
        *   🔍 `search_retention_policy` (Queries ChromaDB)
        *   🏨 `fetch_customer_booking` (Queries SQLite DB)
        *   👔 `request_manager_approval` (Human-in-the-loop pause)
        *   📧 `send_retention_email` (Takes action)

---

## 🛠️ Technology Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend** | Streamlit (Custom styled UI) |
| **Backend API** | Flask |
| **AI / NLP** | LangChain, LangGraph, Groq API (Llama 3) |
| **Machine Learning** | Scikit-Learn, Pandas, Joblib |
| **Vector Database** | ChromaDB, HuggingFace Embeddings |
| **Relational DB** | SQLite (Synthetic data for demo purposes) |
| **CI/CD** | Jenkins, Docker, AWS S3, AWS ECR, AWS EC2 |

---

## 🚀 Professional CI/CD Pipeline (Stateless Architecture)

We employ a robust, **stateless** CI/CD architecture leveraging **Jenkins** and **AWS**, ensuring that the container remains lightweight, secure, and production-ready.

### 🔄 The Deployment Flow:
1.  **Code Push:** Developer pushes code to GitHub.
2.  **Webhook Trigger:** GitHub notifies Jenkins (running locally, exposed via ngrok).
3.  **Continuous Integration (Jenkins):**
    *   Installs dependencies and runs Python tests (`pytest`).
    *   **Trains the ML Model** dynamically and generates `model.joblib`.
    *   **Builds the Vector Store** locally using ChromaDB.
    *   **Uploads Artifacts:** Uploads the newly generated ML model and Vector DB to an **AWS S3 Bucket** (`hotel-retention-artifacts`).
4.  **Continuous Delivery (Docker & AWS):**
    *   Builds a lightweight Docker image (`python:3.10-slim`). The image *excludes* the large model and database files.
    *   Pushes the image to **AWS ECR** (Elastic Container Registry).
    *   SSH connects to an **AWS EC2** instance and pulls the latest container.

### 🐳 Container Startup (Runtime Hydration)
When the Docker container boots on the EC2 instance, the `start.sh` entry point script executes:
1.  **Downloads Artifacts:** Uses the AWS CLI to pull `model.joblib` and the ChromaDB index from S3.
2.  **Seeds Database:** Runs `seed_database.py` to generate a fresh, ephemeral SQLite database (`hotel.db`).
3.  **Launches Services:** Starts both the Flask backend API and Streamlit User Interface simultaneously.





### flow diagram 

Developer → GitHub → Webhook → Jenkins (Local via ngrok)
                     ↓
               Jenkins Pipeline
                     ↓
  ┌────────────────────────────────────┐
  │ 1. Install dependencies            │
  │ 2. Run tests                       │
  │ 3. Train ML model                  │
  │ 4. Build ChromaDB vector store     │
  │ 5. Upload artifacts to AWS S3      │
  │ 6. Build Docker image              │
  │ 7. Push image to AWS ECR           │
  │ 8. SSH to EC2 and deploy           │
  └────────────────────────────────────┘
                     ↓
              EC2 Server
                     ↓
        Docker Container Startup
                     ↓
  - Download model.joblib from S3
  - Download chroma_db from S3
  - Seed SQLite database
  - Start Flask backend

**Why this matters?** 
*This approach decouples application code from data artifacts. It guarantees clean, reproducible deployments, reduces Docker image bloat, and allows us to retrain models without restarting the application infrastructure.*

---

## 💻 Running Locally

### 1. Clone & Set Up
```bash
git clone https://github.com/your-username/intelligent-hotel-retention-agent.git
cd intelligent-hotel-retention-agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
```

### 3. Start the Application
Run the startup script to initialize everything:
```bash
# On Linux / Mac
chmod +x start.sh
./start.sh

# Or manually run in two separate terminal windows:
python main.py
streamlit run app.py
```

*Open your browser to `http://localhost:8501` to use the Agent.*