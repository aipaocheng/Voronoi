# $LAN=PYTHON$
# 國立中山大學 資工所甲組
# M133040073 艾保丞
import sys
import numpy as np
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QSplitter, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle

class VoronoiCanvas(FigureCanvas):
    # 初始化畫布
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = fig.add_subplot(111)

        super().__init__(fig)
        self.points = []
        self.edges = []
        self.left_hull = []
        self.right_hull = []
        self.test_sets = []
        self.test_set_index = 0
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
        # 檢查新點是否已在 points 中
        if (x, y) not in self.points:
            self.points.append((x, y))
            # print(f"Added point: ({x}, {y})")
            self.plot_points()
            self.plot_lines()
        else:
            print(f"Point ({x}, {y}) already exists, not added.")

    def plot_points(self):  
        # Clear and plot all points (without displaying coordinates)
        self.ax.clear()
        self.init_canvas()
        for (x, y) in self.points:
            if x < 0 or x > 600 or y < 0 or y > 600:
                print(f"Point ({x}, {y}) is out of bounds.")
                continue
            self.ax.plot(x, y, 'bo')  # Plot the point
            # Display coordinates on the canvas
            self.ax.text(x + 5, y + 5, f"({x},{y})", fontsize=10, color='black')
        self.draw()

    # 給予兩個點，劃出直線
    def plot_lines(self):
        for edge in self.edges:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'black')
        self.draw()
        
    ####################################################################################

    def run_voronoi(self):        
        points_sort = np.array(self.points)
        points_sort = points_sort[np.argsort(points_sort[:, 0])]  # 根據 x 座標排序
        
        # 呼叫分治法
        voronoi_edges = self.divide_and_conquer(points_sort)
        # self.edges.extend(voronoi_edges)
        self.plot_lines()
        self.draw()
        # if len(self.points) < 2:
        #     return
        # elif len(self.points) == 2:
        #     # print("Two points.")
        #     self.plot_two_points()
        # elif len(self.points) == 3:
        #     # print("Three points.")
        #     self.plot_three_points()
        # else:
        #     print("too many points")
        #     return

    def clean(self):
        print("Cleaning canvas...")
        self.ax.clear()
        self.points.clear()
        self.edges.clear()
        self.test_sets.clear()
        self.test_set_index = 0
        self.init_canvas()

    def next_set(self):
        if self.test_sets:
            if self.test_set_index < len(self.test_sets):
                print(f"Displaying test set {self.test_set_index + 1}.")
                self.points.clear()
                self.edges.clear()
                for point in self.test_sets[self.test_set_index]:
                    self.add_point(round(point[0]), round(point[1]))
                self.test_set_index += 1
                self.test_set_index = self.test_set_index % len(self.test_sets)
                self.run_voronoi()
            else:
                print("No more test sets to display.")
        else:
            print("No test sets loaded.")

    def open_file(self):
        # 彈出檔案選擇對話框
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                self.ax.clear()
                self.init_canvas()
                self.test_sets.clear()
                self.test_set_index = 0
                self.points.clear()
                self.edges.clear()
                self.file_processing(file_path)
            except Exception as e:
                print(f"Error loading file: {e}")
                QMessageBox.critical(self, "Error", "An error occurred while loading the file.")
        
    def save_file(self):
        self.points = sorted(self.points, key=lambda point: (point[0], point[1]))
        # 遍歷 self.edges 中的每一筆邊，確保順序為 (x1, y1) < (x2, y2)
        for i in range(len(self.edges)):
            x1, y1, x2, y2 = self.edges[i]
            
            # 如果 x2 < x1 或者 x 座標相同且 y2 < y1，則交換順序
            if x2 < x1 or (x1 == x2 and y2 < y1):
                self.edges[i] = (x2, y2, x1, y1)
            else:
                # 保持原順序
                self.edges[i] = (x1, y1, x2, y2)
        # 使用 x1 值對 self.edges 進行排序
        self.edges.sort(key=lambda edge: edge[0])

        print(self.points)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w') as file:
                for x, y in self.points:
                    # 格式化輸出每行為 "P x y"
                    file.write(f'P {int(x)} {int(y)}\n')
                for x1, y1, x2, y2 in self.edges:
                    # 格式化輸出每行為 "E x1 y1 x2 y2"
                    file.write(f'E {int(x1)} {int(y1)} {int(x2)} {int(y2)}\n')
                    
            QMessageBox.information(self, "Save File", "Points saved successfully.")

    ####################################################################################
    
    def divide_and_conquer(self, points_sort):
        if len(points_sort) == 1:
            return ()
        elif len(points_sort) == 2:
            edges = self.plot_two_points(points_sort)
            if len(self.edges) == 2:
                self.edges.extend(edges)
                return ()
            else:
                return edges
        elif len(points_sort) == 3:
            edges = self.plot_three_points(points_sort)
            if len(self.edges) == 3:
                self.edges.extend(edges)
                return ()
            else:
                return edges

        mid = len(points_sort) // 2 # 向下取整數
        left_points = points_sort[:mid]
        right_points = points_sort[mid:]

        left_edges = self.divide_and_conquer(left_points)
        right_edges = self.divide_and_conquer(right_points)
        
        for edge in left_edges:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'green')
        for edge in right_edges:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'orange')
        self.draw()

        self.merge_voronoi(left_points, right_points, left_edges, right_edges)
        # return self.merge_voronoi(left_points, right_points, left_edges, right_edges)
        
    def merge_voronoi(self, left_points, right_points, left_edges, right_edges):
        # convex_hull
        left_hull = self.convex_hull(left_points)
        self.left_hull = left_hull
        right_hull = self.convex_hull(right_points)
        self.right_hull = right_hull
        
        merge_hull = self.merge_convex_hull(left_hull, right_hull)
        # 使用藍色畫出合併後的凸包
        for i in range(len(merge_hull)):
            x1, y1 = merge_hull[i]
            x2, y2 = merge_hull[(i + 1) % len(merge_hull)]
            self.ax.plot([x1, x2], [y1, y2], 'blue')
        self.draw()
    
    def convex_hull(self, points):
        
        if len(points) < 3:
            if points[0][0] < points[1][0]:
                points[0], points[1] = points[1], points[0]
            return points
        elif len(points) == 3:
            # 選擇x最小的為第一個點
            points = sorted(points, key=lambda point: point[1])
            points = sorted(points, key=lambda point: point[0])
            if points[1][1] > points[2][1]: 
                points[1], points[2] = points[2], points[1]
                
            a1, b1 = self.two_points_find_ab(points[0][0], points[0][1], points[1][0], points[1][1])
            a2, b2 = self.two_points_find_ab(points[0][0], points[0][1], points[2][0], points[2][1])
            
            if a1 == a2:
                return points
            elif a1 == None:
                points[1], points[2] = points[2], points[1]
            elif a2 == None:
                pass
            else:
                if a1 > a2:
                    points[1], points[2] = points[2], points[1]
            
            for i in range(3):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % 3]
                # 使用藍色畫出convex hull的邊
                self.ax.plot([x1, x2], [y1, y2], 'blue')
            self.draw()
            return points  
        else:
            return points
        
    def merge_convex_hull(self, left_convex, right_convex):
        def orientation(p1, p2, p3):
            """
            判斷三點的方向：
            - 返回 1 表示順時針 (右轉)
            - 返回 -1 表示逆時針 (左轉)
            - 返回 0 表示三點共線
            """
            cross_product = (p3[1] - p1[1]) * (p2[0] - p1[0]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
            if cross_product > 0:
                return -1  # 逆時針
            elif cross_product < 0:
                return 1  # 順時針
            else:
                return 0  # 共線

        def find_upper_tangent():
            """找到左凸包與右凸包的上切線"""
            
            left_idx = len(left_convex) - 1  
            right_idx = 0  # 從右凸包的最左點開始
            print(f"start from {left_convex[left_idx]}, {right_convex[right_idx]}")
                        
            while True:
                updated = False
                # 移動左凸包的索引
                while True:
                    result = orientation(right_convex[right_idx], left_convex[left_idx], left_convex[(left_idx-1) % len(left_convex)])
                    if result == 1:  # 順時針
                        left_idx = (left_idx + 1) % len(left_convex)
                        updated = True
                    else:
                        break

                # 移動右凸包的索引
                while True:
                    result = orientation(left_convex[left_idx], right_convex[right_idx], right_convex[(right_idx+1) % len(right_convex)])
                    if result == -1:
                        right_idx = (right_idx - 1) % len(right_convex)
                        updated = True
                    else:
                        break
                    
                if not updated:
                    break
                
            return left_idx, right_idx

        def find_lower_tangent():
            """找到左凸包與右凸包的下切線"""
            left_idx = len(left_convex) - 1  # 從左凸包的最右點開始
            right_idx = 0  # 從右凸包的最左點開始
            
            while True:
                updated = False
                # 移動右凸包的索引
                while True:
                    result = orientation(left_convex[left_idx], right_convex[right_idx], right_convex[(right_idx+1) % len(right_convex)])
                    if result == 1:
                        right_idx = (right_idx + 1) % len(right_convex)
                        updated = True
                    elif result == 0:
                        right_idx = (right_idx + 1) % len(right_convex)
                        updated = True
                    else:
                        break

                # 移動左凸包的索引
                while True:
                    result = orientation(right_convex[right_idx], left_convex[left_idx], left_convex[(left_idx - 1) % len(left_convex)])
                    if result == -1:
                        left_idx = (left_idx - 1) % len(left_convex)
                        updated = True
                    elif result == 0:
                        left_idx = (left_idx - 1) % len(left_convex)
                        updated = True
                    else:
                        break
                    
                if not updated:
                    break
                
            return left_idx, right_idx
        
        # 找到上下切線
        upper_left, upper_right = find_upper_tangent()
        lower_left, lower_right = find_lower_tangent()
        print(f"Upper tangent: {left_convex[upper_left]} - {right_convex[upper_right]}")
        print(f"Lower tangent: {left_convex[lower_left]} - {right_convex[lower_right]}")

        # 合併凸包
        merged_hull = []
        output_left = []
        output_right = []
        # 添加左凸包的有效點
        idx = upper_left
        while idx != (lower_left + 1) % len(left_convex):
            output_left.append(left_convex[idx])
            merged_hull.append(left_convex[idx])
            idx = (idx + 1) % len(left_convex)

        # 添加右凸包的有效點
        idx = lower_right
        while idx != (upper_right + 1) % len(right_convex):
            output_right.append(right_convex[idx])
            merged_hull.append(right_convex[idx])
            idx = (idx + 1) % len(right_convex)

        return merged_hull
    # def merge_convex_hull(self, left_hull, right_hull):
    #     # 將點按照 x 座標排序
    #     points_sort = sorted(points, key=lambda point: (point[0], point[1]))

    #     # 初始化凸包
    #     hull = []
    #     # 進行兩次迴圈，以確保所有點都被處理
    #     for i in range(2):
    #         # 開始計算凸包
    #         while len(hull) >= 2 and self.cross_product(hull[-2], hull[-1], points[0]) < 0:
    #             hull.pop()
    #         hull.append(points[0])
    #         points_sort = points_sort[1:]

    #     return hull
    
    
    # 如果只有兩個點
    def plot_two_points(self, points_sort):
        edges = []
        # 選取最近添加的兩個點
        (x1, y1), (x2, y2) = points_sort[0], points_sort[1]

        # 計算中心點
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        # print(f"Center point: ({center_x}, {center_y})")

        # 計算斜率及法向量斜率
        if x1 == x2:
            x_values = [0, 600]
            y_values = [center_y, center_y]
        elif y1 == y2:
            x_values = [center_x, center_x]
            y_values = [0, 600]
        else:
            a, b = self.perpendicular_line_params(x1, y1, x2, y2)
            # print(f"Perpendicular line: y = {a}x + {b}")
            
            if a is None:
                x_values = [center_x, center_x]
                y_values = [0, 600]
            else:
                (x_out1, y_out1), (x_out2, y_out2) = self.border_points(a, b)
                                
                x_values = [x_out1, x_out2]
                y_values = [y_out1, y_out2]

        # 繪製法向量線
        edges.append((x_values[0], y_values[0], x_values[1], y_values[1], x1, y1, x2, y2))
        # self.ax.plot(x_values, y_values, 'black')
        # self.plot_lines()
        # self.draw()
        return edges
    
    # 如果有三個點
    def plot_three_points(self, points_sort):
        edges = []
        # 選取最近添加的三個點
        (x1, y1), (x2, y2), (x3, y3) = points_sort[0], points_sort[1], points_sort[2]
        
        mid_x12, mid_y12 = self.mid_point(x1, y1, x2, y2)
        mid_x23, mid_y23 = self.mid_point(x2, y2, x3, y3)
        mid_x13, mid_y13 = self.mid_point(x1, y1, x3, y3)      
        
        # 判斷三點共線
        a12, b12 = self.two_points_find_ab(x1, y1, x2, y2)
        a23, b23 = self.two_points_find_ab(x2, y2, x3, y3)
        if a12 == None and a23 == None: # 三點在同一條垂直線上
            # 由y的大小找出中間的點
            if (y1 > y2 and y1 < y3) or (y1 < y2 and y1 > y3): # y1為中間點
                edges.append((0, mid_y12, 600, mid_y12, x1, y1, x2, y2))
                edges.append((0, mid_y13, 600, mid_y13, x1, y1, x3, y3))
            elif (y2 > y1 and y2 < y3) or (y2 < y1 and y2 > y3): # y2為中間點
                edges.append((0, mid_y12, 600, mid_y12, x1, y1, x2, y2))
                edges.append((0, mid_y23, 600, mid_y23, x2, y2, x3, y3))
            elif (y3 > y1 and y3 < y2) or (y3 < y1 and y3 > y2): # y3為中間點
                edges.append((0, mid_y13, 600, mid_y13, x1, y1, x3, y3))
                edges.append((0, mid_y23, 600, mid_y23, x2, y2, x3, y3))
        elif y1 == y2 and y2 == y3: # 三點在同一條水平線上
            # 由x的大小找出中間的點
            if (x1 > x2 and x1 < x3) or (x1 < x2 and x1 > x3): # x1為中間點
                edges.append((mid_x12, 0, mid_x12, 600, x1, y1, x2, y2))
                edges.append((mid_x13, 0, mid_x13, 600, x1, y1, x3, y3))
            elif (x2 > x1 and x2 < x3) or (x2 < x1 and x2 > x3): # x2為中間點
                edges.append((mid_x12, 0, mid_x12, 600, x1, y1, x2, y2))
                edges.append((mid_x23, 0, mid_x23, 600, x2, y2, x3, y3))
            elif (x3 > x1 and x3 < x2) or (x3 < x1 and x3 > x2): # x3為中間點
                edges.append((mid_x13, 0, mid_x13, 600, x1, y1, x3, y3))
                edges.append((mid_x23, 0, mid_x23, 600, x2, y2, x3, y3))
        elif a12 == a23: # 三點共線但不為垂直線
            if (y1 > y2 and y1 < y3) or (y1 < y2 and y1 > y3): # y1為中間點
                a, b = self.perpendicular_line_params(x1, y1, x2, y2)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x2, y2))
                a, b = self.perpendicular_line_params(x1, y1, x3, y3)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x3, y3))
            elif (y2 > y1 and y2 < y3) or (y2 < y1 and y2 > y3): # y2為中間點
                a, b = self.perpendicular_line_params(x1, y1, x2, y2)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x2, y2))
                a, b = self.perpendicular_line_params(x2, y2, x3, y3)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x2, y2, x3, y3))
            elif (y3 > y1 and y3 < y2) or (y3 < y1 and y3 > y2): # y3為中間點
                a, b = self.perpendicular_line_params(x1, y1, x3, y3)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x3, y3))
                a, b = self.perpendicular_line_params(x2, y2, x3, y3)
                temp = self.border_points(a, b)
                edges.append((temp[0][0], temp[0][1], temp[1][0], temp[1][1], x2, y2, x3, y3))
        else:
            triangle_type, angle = self.is_obtuse_triangle(x1, y1, x2, y2, x3, y3)

            # 計算三角形的外心
            pb_a12, pb_b12 = self.perpendicular_line_params(x1, y1, x2, y2)
            pb_a23, pb_b23 = self.perpendicular_line_params(x2, y2, x3, y3)
            pb_a13, pb_b13 = self.perpendicular_line_params(x1, y1, x3, y3)
            
            x, y = self.find_intersection(pb_a12, pb_b12, pb_a23, pb_b23)
            # print(f"Outer center: ({x}, {y})")
            # 繪製外心
            self.ax.plot(x, y, 'ro')
            self.draw()
            
            if triangle_type == 2: # 銳角
                temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                edges.append((x, y, temp[0], temp[1], x1, y1, x2, y2))
                temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                edges.append((x, y, temp[0], temp[1], x2, y2, x3, y3))
                temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                edges.append((x, y, temp[0], temp[1], x1, y1, x3, y3))
                self.draw()
            else: # 鈍角 直角
                if angle == 'A':
                    temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                    edges.append((x, y, temp[0], temp[1], x1, y1, x2, y2))
                    temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                    edges.append((x, y, temp[0], temp[1], x1, y1, x3, y3))
                elif angle == 'B':
                    temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                    edges.append((x, y, temp[0], temp[1], x1, y1, x2, y2))
                    temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                    edges.append((x, y, temp[0], temp[1], x2, y2, x3, y3))
                else:
                    temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                    edges.append((x, y, temp[0], temp[1], x1, y1, x3, y3))
                    temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                    edges.append((x, y, temp[0], temp[1], x2, y2, x3, y3))
                
                if triangle_type == 0: # 鈍角
                    if angle == 'A':
                        temp = self.line_points(x, y, mid_x23, mid_y23, 1)
                        edges.append((x, y, temp[0], temp[1], x2, y2, x3, y3))
                    elif angle == 'B':
                        temp = self.line_points(x, y, mid_x13, mid_y13, 1)
                        edges.append((x, y, temp[0], temp[1], x1, y1, x3, y3))
                    else:
                        temp = self.line_points(x, y, mid_x12, mid_y12, 1)
                        edges.append((x, y, temp[0], temp[1], x1, y1, x2, y2))
                elif triangle_type == 1: # 直角
                    if angle == 'A':
                        temp_A, temp_B = self.border_points(pb_a23, pb_b23)
                        if math.dist((x1, y1), temp_A) > math.dist((x1, y1), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append((x, y, temp[0], temp[1], x2, y2, x3, y3))
                    elif angle == 'B':
                        temp_A, temp_B = self.border_points(pb_a13, pb_b13)
                        if math.dist((x2, y2), temp_A) > math.dist((x2, y2), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append((x, y, temp[0], temp[1], x1, y1, x3, y3))
                    else:
                        temp_A, temp_B = self.border_points(pb_a12, pb_b12)
                        if math.dist((x3, y3), temp_A) > math.dist((x3, y3), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append((x, y, temp[0], temp[1], x1, y1, x2, y2))
        #         self.draw()
        # self.plot_lines()
        return edges
    
    
    # 給予兩個點，其中垂線之a和b
    def perpendicular_line_params(self, x1, y1, x2, y2):
        # 計算原始斜率
        if y1 == y2:  # 避免除以零的情況（垂直線）
            a = None
            b = (x1 + x2) / 2
        elif x1 == x2:  # 避免除以零的情況（水平線）
            a = 0
            b = (y1 + y2) / 2
        else:
            m_original = (y2 - y1) / (x2 - x1)
            # print(f"Original slope: {m_original}")
            
            # 計算垂直線的斜率
            a = -1 / m_original
            
            # print(f"Perpendicular slope: {a}")

            # 計算中點
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # 計算截距
            b = center_y - a * center_x

        return a, b
    
    # 給予兩個點，計算直線方程式 y = ax + b 中的 a 和 b
    def two_points_find_ab(self, x1, y1, x2, y2):
        if x1 == x2:
            a = None
            b = None
        else:
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
        return a, b
        
    # 給予兩條直線的斜率和截距，計算交點
    def find_intersection(self, a1, b1, a2, b2):
        # 檢查斜率是否相同，若相同則兩條直線平行，沒有交點
        if a1 == a2:
            print("The lines are parallel, no intersection.")
            return None
        
        if a1 is None:
            # 若其中一條直線為垂直線，則交點的 x 座標為 b1
            x = b1
            # 計算對應的 y 值，將 x 帶入另一條直線方程式
            y = a2 * x + b2
        elif a2 is None:
            # 若其中一條直線為垂直線，則交點的 x 座標為 b2
            x = b2
            # 計算對應的 y 值，將 x 帶入另一條直線方程式
            y = a1 * x + b1
        else:
            # 若兩條直線均有斜率，則計算交點的 x 座標
            x = (b2 - b1) / (a1 - a2)
            # 計算對應的 y 值，將 x 帶入其中一條直線方程式
            y = a1 * x + b1
        return (x, y)
    
    # 判斷為哪一種三角形
    def is_obtuse_triangle(self, x1, y1, x2, y2, x3, y3):
        # 計算三邊的長度
        a = math.dist((x2, y2), (x3, y3))  # BC
        b = math.dist((x1, y1), (x3, y3))  # AC
        c = math.dist((x1, y1), (x2, y2))  # AB

        # 找出最大邊長
        max_side = max(a, b, c)
        sides = sorted([a, b, c])  # 排序邊長
        
        if max_side == a:
            angle = 'A'
        elif max_side == b:
            angle = 'B'
        else:
            angle = 'C'
        
        # 使用勾股定理的逆定理判斷是否為鈍角三角形
        if sides[2] ** 2 > sides[0] ** 2 + sides[1] ** 2:
            tri_type = 0  # 鈍角三角形
        elif sides[2] ** 2 == sides[0] ** 2 + sides[1] ** 2:
            tri_type = 1  # 直角三角形
        else:
            tri_type = 2  # 銳角三角形
        
        return tri_type, angle
    
    # 給予一直線，計算在邊上的兩個點
    def border_points(self, a, b):
        temp_point = []
        if a is None:
            return (b, 0), (b, 600)
        elif a == 0:
            return (0, b), (600, b)
        else:
            # 計算通過中心點的法向量線的邊界範圍
            # (0, y)
            y_at_x_min = b
            if y_at_x_min >= 0 and y_at_x_min <= 600:
                temp_point.append((0, y_at_x_min))
            # (600, y)
            y_at_x_max = a * 600 + b
            if y_at_x_max >= 0 and y_at_x_max <= 600:
                temp_point.append((600, y_at_x_max))
            # (x, 0)
            x_at_y_min = (0 - b) / a
            if x_at_y_min >= 0 and x_at_y_min <= 600:
                temp_point.append((x_at_y_min, 0))
            # (x, 600)
            x_at_y_max = (600 - b) / a
            if x_at_y_max >= 0 and x_at_y_max <= 600:
                temp_point.append((x_at_y_max, 600))
            return temp_point[0], temp_point[1]
    
    # 計算中點
    def mid_point(self, x1, y1, x2, y2):
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        return mid_x, mid_y
    
    # 
    def line_points(self, x, y, mid_x, mid_y, order):
        a, b = self.two_points_find_ab(x, y, mid_x, mid_y)
        if order == 0: # 外心 中點 邊界
            if a is None:
                if y > mid_y:
                    temp_point = (x, 0)
                else:
                    temp_point = (x, 600)
            else:
                border1, border2 = self.border_points(a, b)
                if x == mid_x:
                    if y < mid_y:
                        temp_point = border1
                        if border2[1] > border1[1]:
                            temp_point = border2
                    else:
                        temp_point = border1
                        if border2[1] < border1[1]:
                            temp_point = border2
                else:
                    if x < mid_x:
                        temp_point = border1
                        if border2[0] > border1[0]:
                            temp_point = border2
                    else:
                        temp_point = border1
                        if border2[0] < border1[0]:
                            temp_point = border2
        else: # 中點 外心 邊界
            if a is None:
                if y > mid_y:
                    temp_point = (mid_x, 600)
                else:
                    temp_point = (mid_x, 0)
            else:
                border1, border2 = self.border_points(a, b)
                if x == mid_x:
                    if y < mid_y:
                        temp_point = border1
                        if border2[1] < border1[1]:
                            temp_point = border2
                    else:
                        temp_point = border1
                        if border2[1] > border1[1]:
                            temp_point = border2
                else:
                    if x < mid_x:
                        temp_point = border1
                        if border2[0] < border1[0]:
                            temp_point = border2
                    else:
                        temp_point = border1
                        if border2[0] > border1[0]:
                            temp_point = border2
        return temp_point

    def file_processing(self, file_path):
        # 讀取檔案
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            i = 0  # 行索引
            if lines[0][0] == 'P':
                while i < len(lines):
                    line = lines[i].strip()
                    i += 1
                    # 忽略 # 開頭的行
                    if line.startswith("#"):
                        continue
                    
                    # 若行為 "0"，則停止讀取
                    if line == "0":
                        break
                    
                    # 若行是 "P x y"，則解析為座標
                    if line.startswith("P"):
                        x, y = map(float, line.split()[1:])
                        self.points.append((int(x), int(y)))
                        print(f"Added point: ({x}, {y})")
                        
                    if line.startswith("E"):
                        x1, y1, x2, y2 = map(float, line.split()[1:])
                        self.edges.append((int(x1), int(y1), int(x2), int(y2), 99999, 99999, 99999, 99999))
                        print(f"Added edge: ({x1}, {y1}) to ({x2}, {y2})")
                        
                # 顯示讀取的點
                for point in self.points:
                    print(f"Point: {point}")
                for edge in self.edges:
                    print(f"Edge: {edge}")
                self.plot_points()
                self.plot_lines()
                QMessageBox.information(self, "Open File", "Output file loaded successfully.")
            else:
                while i < len(lines):
                    line = lines[i].strip()
                    i += 1
                    # 忽略 # 開頭的行
                    if line.startswith("#"):
                        continue
                    
                    # 若行為 "0"，則停止讀取
                    if line == "0":
                        break
                    
                    # 若行是數字，代表之後的行數需解析為座標
                    if line.isdigit():
                        num_coords = int(line)  # 獲取後續要讀取的座標數量
                        coords = []  # 儲存這組座
                        # 讀取指定數量的非 # 開頭的座標行
                        while len(coords) < num_coords and i < len(lines):
                            coord_line = lines[i].strip()
                            i += 1
                            
                            # 忽略 # 開頭的行
                            if coord_line.startswith("#"):
                                continue
                            
                            # 解析 x, y 座標
                            x, y = map(float, coord_line.split())
                            coords.append((x, y))
                        
                        # 將這組座標添加至測試集
                        if len(coords) == num_coords:
                            self.test_sets.append(coords)
                        
                # 顯示讀取的測試集
                for i, test_set in enumerate(self.test_sets):
                    print(f"Test set {i + 1} ({len(test_set)} points): {test_set}")
                print("File processing completed.\n")
                QMessageBox.information(self, "Open File", "Read test sets successfully.\nPress 'NextSet' to display the first set.")
            
            
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
