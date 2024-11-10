import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QSplitter, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.spatial import Voronoi, voronoi_plot_2d
from matplotlib.patches import Rectangle

class VoronoiCanvas(FigureCanvas):
    # 初始化畫布
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = fig.add_subplot(111)

        super().__init__(fig)
        self.points = []
        self.init_canvas()

        self.mpl_connect("button_press_event", self.on_click)

    def init_canvas(self):
        # Set initial limits for the canvas
        self.ax.set_xlim(0, 600)
        self.ax.set_ylim(0, 600)
        # self.ax.set_axis_off()  # Hide the axis (no ticks, labels, or grid)

        # Draw the canvas border (rectangle)
        self.draw_canvas_border()

        self.draw()

    def draw_canvas_border(self):
        # Draw the border of the canvas (a rectangle)
        border = Rectangle((0, 0), 600, 600, linewidth=5, edgecolor='black', facecolor='none')
        self.ax.add_patch(border)

    def on_click(self, event):
        # Check if click is inside the axes (plot area)
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.add_point(round(x), round(y))

    def add_point(self, x, y):
        self.points.append((x, y))
        print(f"Added point: ({x}, {y})")
        self.plot_points()

    def plot_points(self):
        # Clear and plot all points (without displaying coordinates)
        self.ax.clear()
        self.init_canvas()
        for (x, y) in self.points:
            self.ax.plot(x, y, 'bo')  # Plot the point
            # Display coordinates on the canvas
            self.ax.text(x + 5, y + 5, f"({round(x, 1)},{round(y, 1)})", fontsize=10, color='black')
        self.draw()

    def run_voronoi(self):
        
        if len(self.points) < 2:
            return

        if len(self.points) == 2:
            self.plot_two_points()
            return
        

    def clean(self):
        print("Cleaning canvas...")
        self.ax.clear()
        self.points.clear()
        self.init_canvas()

    def next_set(self):
        self.clean()
        self.points = np.random.rand(10, 2) * 600  # Adjust to match canvas size
        self.plot_points()

    

    
            
    def plot_two_points(self):
        # 選取最近添加的兩個點
        (x1, y1), (x2, y2) = self.points[0], self.points[1]

        # 計算中心點
        center_x = round((x1 + x2) / 2, 1)
        center_y = round((y1 + y2) / 2, 1)
        print(f"Center point: ({center_x}, {center_y})")

        # 計算斜率及法向量斜率
        if x1 == x2:
            x_values = [0, 600]
            y_values = [center_y, center_y]
        elif y1 == y2:
            x_values = [center_x, center_x]
            y_values = [0, 600]
        else:
            a, b = self.perpendicular_line_params(x1, y1, x2, y2)
            print(f"Perpendicular line: y = {a}x + {b}")
            temp_point = []
            
            # 計算通過中心點的法向量線的邊界範圍
            # (0, y)
            y_at_x_min = b
            if y_at_x_min >= 0 and y_at_x_min <= 600:
                temp_point.append((0, y_at_x_min))
            # (600, y)
            y_at_x_max = round(a * 600 + b, 3)
            if y_at_x_max >= 0 and y_at_x_max <= 600:
                temp_point.append((600, y_at_x_max))
            # (x, 0)
            x_at_y_min = round((0 - b) / a, 3)
            if x_at_y_min >= 0 and x_at_y_min <= 600:
                temp_point.append((x_at_y_min, 0))
            # (x, 600)
            x_at_y_max = round((600 - b) / a, 3)
            if x_at_y_max >= 0 and x_at_y_max <= 600:
                temp_point.append((x_at_y_max, 600))
            
            x1, y1 = temp_point[0]
            x2, y2 = temp_point[1]
            
            print(f"Points: ({x1}, {y1}), ({x2}, {y2})")
            
            x_values = [x1, x2]
            y_values = [y1, y2]

        # 繪製法向量線
        self.ax.plot(x_values, y_values, 'r--')  # 紅色虛線
        self.draw()
        
    def perpendicular_line_params(self, x1, y1, x2, y2):
        # 計算原始斜率
        if x2 == x1:  # 避免除以零的情況（垂直線）
            raise ValueError("The line is vertical; cannot compute perpendicular slope.")
        
        m_original = (y2 - y1) / (x2 - x1)
        print(f"Original slope: {m_original}")
        
        # 計算垂直線的斜率
        a = round(-1 / m_original, 3)
        print(f"Perpendicular slope: {a}")

        # 計算中點
        center_x = round((x1 + x2) / 2, 1)
        center_y = round((y1 + y2) / 2, 1)

        # 計算截距
        b = round(center_y - a * center_x, 3)

        return a, b

        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            try:
                self.canvas.points = np.loadtxt(file_path, delimiter=',')
                self.canvas.plot_points()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            np.savetxt(file_path, self.canvas.points, delimiter=',')
            QMessageBox.information(self, "Save File", "Points saved successfully.")

class VoronoiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voronoi Diagram Application")
        self.setGeometry(300, 300, 1200, 800)
            # 視窗的大小設為 1200 x 800 像素，並將視窗位置調整到螢幕上 (300, 300) 的位置。

        # Main Canvas for Voronoi Diagram
        self.canvas = VoronoiCanvas(self)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Create main layout for the window
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        # Create splitter to separate canvas and buttons
        splitter = QSplitter(Qt.Horizontal)

        # Create buttons and their layout
        button_layout = QVBoxLayout()

        btn_run = QPushButton("Run")
        btn_run.clicked.connect(self.canvas.run_voronoi)
        
        btn_clean = QPushButton("Clean")
        btn_clean.clicked.connect(self.canvas.clean)
        
        btn_next_set = QPushButton("NextSet")
        btn_next_set.clicked.connect(self.canvas.next_set)
        
        btn_open_file = QPushButton("OpenFile")
        btn_open_file.clicked.connect(self.canvas.open_file)
        
        btn_save_file = QPushButton("SaveFile")
        btn_save_file.clicked.connect(self.canvas.save_file)

        # Set the width to half and height to double
        for btn in [btn_run, btn_clean, btn_next_set, btn_open_file, btn_save_file]:
            btn.setFixedWidth(150)  # Half the usual width (default might be around 200)
            btn.setFixedHeight(60)  # Double the usual height (default might be around 30)

        # Add buttons to the layout
        button_layout.addWidget(btn_run)
        button_layout.addWidget(btn_clean)
        button_layout.addWidget(btn_next_set)
        button_layout.addWidget(btn_open_file)
        button_layout.addWidget(btn_save_file)

        # Set vertical alignment to center the buttons in the layout
        button_layout.setAlignment(Qt.AlignHCenter)

        # Create button widget and set its layout
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Add the canvas and button layout to the splitter
        splitter.addWidget(self.canvas)
        splitter.addWidget(button_widget)

        # Set splitter sizes (left part for canvas, right part for buttons)
        splitter.setSizes([900, 300])  # 900 px for canvas, 300 px for buttons

        # Add splitter to the main layout
        layout.addWidget(splitter)

        # Set the central widget of the main window
        self.setCentralWidget(central_widget)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoronoiApp()
    window.show()
    sys.exit(app.exec_())
