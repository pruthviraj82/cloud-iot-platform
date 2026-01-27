# 🌐 Smart IoT Platform

🔗 **Live Application:** [https://cloud-iot-platform-4.onrender.com](https://cloud-iot-platform-4.onrender.com)

A lightweight, cloud-hosted **Flask-based IoT dashboard** designed to receive, visualize, and manage real-time device data. Built with simplicity in mind, this platform supports **local serial devices (Arduino, sensors)** through a secure forwarding agent and runs smoothly on modern cloud platforms like **Render** or **Heroku**.

---

## ✨ Key Features

* 📊 **Real-time IoT data dashboard**
* 🔌 **Local USB / Serial device support** via secure agent
* ☁️ **Cloud-hosted (Render / Heroku compatible)**
* 🔐 **Token-based device authentication**
* ⚙️ **Production-ready Gunicorn + WSGI setup**
* 🧩 Clean, minimal Flask project structure

---

## 🚀 Live Demo

👉 Click here to view the running application:

**[https://cloud-iot-platform-4.onrender.com](https://cloud-iot-platform-4.onrender.com)**

(Use this link to showcase the project in resumes, submissions, or demos.)

---

## 🛠 Prerequisites

Make sure you have the following installed:

* Python **3.8+** (✅ recommended: **3.11**)
* `pip`
* Git (optional, for cloning)

---

## ▶️ Run Locally

### 1️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start the Application

```bash
python run.py
# or
flask run
```

The app will be available at:

```
http://127.0.0.1:5000
```

---

## ☁️ Deployment (Render / Heroku)

This project is production-ready and includes a **Procfile**:

```text
web: gunicorn wsgi:application
```

### 🔧 Environment Variables (Required)

Set these on your hosting platform:

* `SECRET_KEY`
* `DEVICE_AGENT_TOKEN` (for serial agent authentication)
* Database variables (if enabled later)

⚠️ **Never commit secrets to GitHub.** Always use environment variables.

The `wsgi.py` file is environment-aware, allowing smooth deployment across platforms.

---

## 🔁 Local Serial Agent (Arduino → Cloud)

Cloud servers **cannot access USB / COM ports directly**. To stream live sensor data from Arduino or any serial device, use the **Local Serial Agent**.

### 🧠 How It Works

```
Arduino → USB/COM → Local Agent → Cloud API → Dashboard
```

---

### 🧩 Step-by-Step Setup

#### 1️⃣ Set Agent Token on Server (Cloud)

```bash
export DEVICE_AGENT_TOKEN="your_secret_token"
# Windows PowerShell:
$env:DEVICE_AGENT_TOKEN="your_secret_token"
```

#### 2️⃣ Run the Cloud App

Deploy or run the Flask app normally.

#### 3️⃣ Run the Serial Agent on Local Machine

(Where Arduino / USB device is connected)

```bash
pip install -r requirements.txt
python agent/serial_agent.py \
  --port COM3 \
  --baud 9600 \
  --server https://cloud-iot-platform-4.onrender.com/api/forward-serial \
  --token your_secret_token
```

📡 The agent reads serial lines and securely forwards them to the hosted application, which treats them as **live IoT device data**.

---

## 🧪 Supported Devices

* Arduino Uno / Nano
* ESP32 / ESP8266 (via serial)
* Any USB-serial sensor device

---

## 📂 Project Structure (Simplified)

```
Smart-IoT-Platform/
│
├── app/            # Flask app logic
├── agent/          # Local serial forwarding agent
├── templates/      # Dashboard UI
├── static/         # CSS / JS
├── run.py          # Local entry point
├── wsgi.py         # Production entry point
├── requirements.txt
└── Procfile
```

---

## 🔮 Future Enhancements

* 📈 Live charts & analytics
* 🔔 Alerts (Email / WhatsApp)
* 🗄️ Database logging (PostgreSQL / MongoDB)
* 👤 User authentication
* 📱 Mobile-friendly UI

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss improvements.

---

## 📄 License

This project is open-source and free to use for learning and academic purposes.

---

⭐ If you like this project, consider starring the repo — it really helps!
