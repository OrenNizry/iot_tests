# IoT Hardware Automation Assignment

This project simulates a small IoT system with three Nodes and three Endpoints.  
It includes a fake API (`IoTAPI`) and unit tests that verify OTA and DFU logic.

---

## 🧩 Project Structure

```
.
├── iot.py                # Main IoT simulation and API logic
├── tests.py              # Unit tests using unittest
├── requirements.txt      # Dependencies
├── README.md             # Project overview
└── .gitignore
```

---

## ⚙️ Setup Instructions

1. Clone the repository:
   ```bash
   git clone <your-repo-link>
   cd <repo-name>
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Run the Tests

You can run all tests using:
```bash
python -m unittest discover
```

or simply:
```bash
pytest
```

---

## 💡 Notes
- No real hardware or cloud components are used — everything runs locally.
- `iot.py` contains the fake API (`IoTAPI`) and the data model for Nodes and Endpoints.
- `tests.py` includes unit tests that validate version updates, battery checks, and OTA behavior.
- This project was submitted as part of a **Hardware Automation Student** assignment.
