from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 Starting IoT Platform...")
    print("📊 Dashboard: http://127.0.0.1:5000")
    print("🔌 Device Manager: http://127.0.0.1:5000/device-manager")
    print("🧠 AI Assistant: http://127.0.0.1:5000/ai-assistant")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)