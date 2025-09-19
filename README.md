# **Veridian AI.**

Veridian AI is a full-featured, web-based AI image generation platform. It allows users to create, manage, and share AI-generated art using a powerful, uncensored backend, all while providing robust user management and administrative controls.

This project uses a hybrid architecture, combining a lightweight Flask web application with a powerful, on-demand AI engine running in a free Google Colab environment.

<img width="512" height="512" alt="1_1758232412" src="https://github.com/user-attachments/assets/39408ea1-364a-40cc-b049-2540f77688c7" />

### **Key Features**

  • User Authentication: Secure user registration, login, and session management.

  • AI Image Generation: Create high-quality, uncensored images using a prompt, with options for different aspect ratios.

  • Public/Private Toggling: Users can choose to keep their creations private or submit them to a public gallery.

  • Real-Time Live Feed: The homepage features a live feed of new public images created by the community, powered by WebSockets.

  • Personal Gallery: Each user has a secure "My Creations" dashboard to view their own images.

  • Public Gallery: A browsable gallery for all community-approved images.

### **Advanced Admin Panel:**

  • View a list of all users.

  • Inspect any user's complete private and public gallery.

  • Permanently delete content.

  • Manage a queue of download requests.

  • Secure, Permission-Based Downloads: Users must request permission from an admin to download their private, uncensored creations.

### **Account Settings:**

  • Change password functionality.

  • Parental controls to block prompts with restricted keywords.

  • Secure admin promotion via a static security code.

## **Architecture**
### Veridian AI uses a modern, hybrid architecture to provide powerful features for free:

  • Main Web Application: A lightweight Flask and MySQL application that handles the user interface, database, and user management. It's designed to be hosted on any standard, free web service.

  • AI Engine: A powerful, open-source Stable Diffusion model (e.g., RealVisXL) running as a separate API service inside a Google Colab notebook, which provides access to a free, high-performance GPU.

### Technology Stack
  • Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-SocketIO

  • Database: MySQL

  • Frontend: HTML, CSS, JavaScript

  • AI Engine: Google Colab, PyTorch, Diffusers (Stable Diffusion)

  • API Tunneling: ngrok

### Setup and Installation
Follow these steps to run the project locally.

#### 1. Clone the Repository

~~~
git clone https://github.com/your-username/veridian-ai-webapp.git
cd veridian-ai-webapp 
~~~
#### 2. Set Up the MySQL Database

Make sure you have MySQL server running.

Run the setup.sql script to create the database and user. You may need to edit the password inside the file first.

~~~
mysql -u root -p < setup.sql
~~~
#### 3. Create a Python Virtual Environment

##### For macOS/Linux
~~~
python3 -m venv venv
source venv/bin/activate
~~~

##### For Windows
~~~
python -m venv venv
venv\Scripts\activate
~~~

4. Install Dependencies

~~~
pip install -r requirements.txt
~~~

#### 6. Configure Environment Variables

Create a file named .env in the root directory.

Copy the contents of the example below and fill in your actual credentials.

~~~
SECRET_KEY='generate_a_long_random_string'
DATABASE_URL='mysql+mysqlconnector://veridian_user:YourStrongPasswordHere@localhost/veridian_db'
AI_API_ENDPOINT=''
ADMIN_SECURITY_CODE='YourSecretAdminPassword123'
~~~

### How to Run
Because this project runs in two parts, you will need two terminals.

#### 1. Start the AI Engine (in Google Colab)

Open the Veridian_AI_Engine.ipynb notebook in Google Colab.

Add your Hugging Face and ngrok tokens to the Colab Secrets (as HF_TOKEN and NGROK_AUTHTOKEN).

Set the runtime type to T4 GPU.

Run the main cell. At the end of the output, it will give you a public ngrok URL. Copy this URL.

#### 2. Configure and Start the Main Website

Open the .env file in your project folder.

Paste the ngrok URL into the AI_API_ENDPOINT variable. Make sure to add /generate-image to the end.

~~~
AI_API_ENDPOINT='https://<your-ngrok-url>.ngrok-free.app/generate-image'
~~~
In your local terminal (with the venv activated), run the Flask application:

~~~
python app.py
~~~

##### Open your web browser and navigate to http://127.0.0.1:5000.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Created by Parth Patil
