# 🧠 CodeSense
> Real-time developer cognitive load monitor using behavioral ML + AI

## What is CodeSense?
CodeSense monitors how hard your brain is working while you code.
It detects focus, struggle and overload in real-time by analyzing
your keystroke patterns — no camera, 100% private.

## Features
- ⌨️ Real-time keystroke & mouse behavior tracking
- 🤖 XGBoost ML model with 98% accuracy
- 🧠 AI suggestions powered by Groq LLaMA
- 📊 Live futuristic dashboard built with Streamlit
- 🔒 100% local — no data sent anywhere

## Tech Stack
- Python, XGBoost, scikit-learn, Streamlit
- Groq LLaMA API, pynput, pandas, numpy

## How to Run
Start the tracker in Terminal 1:
python tracker.py

Start the dashboard in Terminal 2:
streamlit run dashboard.py

Then open http://localhost:8501 in your browser!

## Demo
Brain states detected:
- 🟢 Focused — typing smoothly, making progress
- 🟡 Struggling — slowing down, more errors
- 🔴 Overloaded — long pauses, lots of backspaces
