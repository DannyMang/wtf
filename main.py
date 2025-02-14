# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
import requests

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False

    def paintEvent(self, event):
        if self.is_selecting:
            from PyQt5.QtGui import QPainter, QColor
            qp = QPainter(self)
            qp.setPen(QColor(255, 0, 0, 127))
            qp.setBrush(QColor(255, 0, 0, 127))
            qp.drawRect(self.begin.x(), self.begin.y(),
                       self.end.x() - self.begin.x(),
                       self.end.y() - self.begin.y())
            
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.is_selecting = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting:
            self.is_selecting = False
            # Capture the screen area
            from PyQt5.QtGui import QScreen
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, 
                min(self.begin.x(), self.end.x()),
                min(self.begin.y(), self.end.y()),
                abs(self.end.x() - self.begin.x()),
                abs(self.end.y() - self.begin.y()))
            
            # Convert screenshot to text using pytesseract
            try:
                import pytesseract
                from PIL import Image
                import io
                
                # Convert QPixmap to PIL Image
                buffer = QBuffer()
                buffer.open(QBuffer.ReadWrite)
                screenshot.save(buffer, "PNG")
                pil_img = Image.open(io.BytesIO(buffer.data()))
                
                # Extract text
                text = pytesseract.image_to_string(pil_img)
                
                # Send text to main window
                if hasattr(self.parent(), 'process_selection'):
                    self.parent().process_selection(text)
            except ImportError:
                print("Please install pytesseract: pip install pytesseract")
            except Exception as e:
                print(f"Error processing image: {e}")
            
            self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize available_models before calling initUI
        self.available_models = []
        # Check available models from Ollama
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                self.available_models = [model['name'] for model in response.json()['models']]
        except requests.exceptions.ConnectionError:
            self.text_display = QTextEdit()  # Create text_display early for error message
            self.text_display.setText("Error: Cannot connect to Ollama. Is it running?")
        
        self.initUI()
        self.selection_window = None

    def initUI(self):
        self.setWindowTitle('Text Explainer')
        self.setGeometry(100, 100, 400, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create buttons
        self.select_button = QPushButton('Select Text', self)
        self.select_button.clicked.connect(self.start_selection)
        
        # Text display area
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        # Add model selector dropdown
        self.model_selector = QComboBox(self)
        self.model_selector.addItems(self.available_models if self.available_models else ['No models found'])

        # Add widgets to layout
        layout.addWidget(self.model_selector)
        layout.addWidget(self.select_button)
        layout.addWidget(self.text_display)

    def start_selection(self):
        if not self.selection_window:
            self.selection_window = TransparentWindow()
            self.selection_window.showFullScreen()
            
    def process_selection(self, selected_text):
        if not self.available_models:
            self.text_display.setText("Error: No Ollama models available. Is Ollama running?")
            return

        selected_model = self.model_selector.currentText()
        
        # Use Ollama API instead of direct LLM
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': selected_model,
                    'prompt': f"Please explain the meaning and context of: {selected_text}",
                    'stream': False
                })
            
            if response.status_code == 200:
                explanation = response.json()['response']
                self.text_display.setText(f"Selected text: {selected_text}\n\nExplanation:\n{explanation}")
            else:
                self.text_display.setText(f"Error: Failed to get response from Ollama (Status: {response.status_code})")
        
        except requests.exceptions.ConnectionError:
            self.text_display.setText("Error: Cannot connect to Ollama. Is it running?")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()