## How to install
1. Clone the project  
    ```bash
    git clone https://github.com/KGH1113/one-card.git
    ```
2. Create virtual env (Optional, Recommended)   
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # Windows (Powershell)
    source venv/Scripts/activate # Mac, Linux (bash)
    ```
3. Install packages   
    ```bash
    pip install -r requirements.txt
    ```
4. Run project
    ```bash
    python main.py
    ```
5. Pyinstaller (Optional)   
    ```
    pyinstaller -w -F main.py
    ```