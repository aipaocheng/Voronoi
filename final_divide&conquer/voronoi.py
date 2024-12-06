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
        self.left_edges = []
        self.right_edges = []
        
        self.left_voronoi = []
        self.right_voronoi = []
        
        self.left_hull = []
        self.right_hull = []
        self.left_delete_hull = []
        self.right_delete_hull = []
        self.merge_hull = []
        self.tangent = []
        
        self.test_sets = []
        self.test_set_index = 0
        self.init_canvas()
        
        self.step = 0
        self.SBS_count = -1
        self.SBS_hp = []
        self.SBS_output = []
        self.SBS_tangent = []

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

    # 劃出self.edges中的所有線段
    def plot_lines(self):
        for edge in self.edges:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'black')
        self.draw()
        
    # 劃出self.left_hull中的所有線段
    def plot_left_hull(self):
        for i in range(len(self.left_hull)):
            x1, y1 = self.left_hull[i]
            x2, y2 = self.left_hull[(i + 1) % len(self.left_hull)]
            self.ax.plot([x1, x2], [y1, y2], 'blue')
        self.draw()
        
    # 劃出self.right_hull中的所有線段
    def plot_right_hull(self):
        for i in range(len(self.right_hull)):
            x1, y1 = self.right_hull[i]
            x2, y2 = self.right_hull[(i + 1) % len(self.right_hull)]
            self.ax.plot([x1, x2], [y1, y2], 'blue')
        self.draw()
        
    # 劃出self.left_delete_hull中的所有線段
    def plot_output_left(self):
        # print(f"left_delete_hull:{self.left_delete_hull}")
        # print(len(self.left_delete_hull)-1)
        for i in range(len(self.left_delete_hull)-1):
            x1, y1 = self.left_delete_hull[i]
            x2, y2 = self.left_delete_hull[(i + 1) % len(self.left_delete_hull)]
            self.ax.plot([x1, x2], [y1, y2], 'blue')
        self.draw()
        
    # 劃出self.right_delete_hull中的所有線段
    def plot_output_right(self):
        # print(f"right_delete_hull:{self.right_delete_hull}")
        # print(len(self.right_delete_hull)-1)
        for i in range(len(self.right_delete_hull)-1):
            x1, y1 = self.right_delete_hull[i]
            x2, y2 = self.right_delete_hull[(i + 1) % len(self.right_delete_hull)]
            self.ax.plot([x1, x2], [y1, y2], 'blue')
        self.draw()
    
    # 劃出self.tangent(上下切線)中的所有線段
    def plot_tangent(self):
        # print(self.tangent)
        # tangent[0] tangent[1] upper
        x1, y1 = self.tangent[0]
        x2, y2 = self.tangent[1]
        self.ax.plot([x1, x2], [y1, y2], 'purple')
        # tangent[2] tangent[3] lower
        x1, y1 = self.tangent[2]
        x2, y2 = self.tangent[3]
        self.ax.plot([x1, x2], [y1, y2], 'purple')
        self.draw()
    
    def plot_left_voronoi(self):
        print(f"left edges: {self.left_voronoi}")
        for edge in self.left_voronoi:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'green')
        self.draw()
        
    def plot_right_voronoi(self):
        print(f"right edges: {self.right_voronoi}")
        for edge in self.right_voronoi:
            x_values = [edge[0], edge[2]]
            y_values = [edge[1], edge[3]]
            self.ax.plot(x_values, y_values, 'orange')
        self.draw()
        
    def plot_SBS(self, count):
        self.init_canvas()
        self.plot_points()
        
        self.plot_left_voronoi()
        self.plot_right_voronoi()
        # output = self.SBS_hp[count]
        # print(f"SBS_hp output:{output}")
        # for edge in output:
        #     x_values = [edge[0], edge[2]]
        #     y_values = [edge[1], edge[3]]
        #     self.ax.plot(x_values, y_values, 'pink')
        for i in range(count+1):
            output = self.SBS_hp[i]
            x_values = [output[0], output[2]]
            y_values = [output[1], output[3]]
            self.ax.plot(x_values, y_values, 'pink')
            
        # output = self.SBS_output[count]
        # for edge in output:
        #     x_values = [edge[0], edge[2]]
        #     y_values = [edge[1], edge[3]]
        #     self.ax.plot(x_values, y_values, 'blue')
        
        output = self.SBS_tangent[count]    
        x_values = [output[0], output[2]]
        y_values = [output[1], output[3]]
        self.ax.plot(x_values, y_values, 'purple')
        
        # for edge in self.SBS_tangent[count]:
        #     # print(f"edge:{edge}")
        #     x_values = [edge[0], edge[2]]
        #     y_values = [edge[1], edge[3]]
        #     self.ax.plot(x_values, y_values, 'purple')
        self.draw()
        
    def plot_SBS_finally(self):
        self.init_canvas()
        self.plot_points()
        self.plot_lines()
        print("Finally")
    ####################################################################################

    def run_voronoi(self):        
        # 將 self.points 根據 x 座標進行排序
        points_sort = sorted(self.points, key=lambda point: point[0])

        # 呼叫分治法
        voronoi_edges = self.divide_and_conquer(points_sort)
        self.edges.clear()
        self.edges.extend(voronoi_edges)
        self.init_canvas()
        self.plot_points()
        self.plot_lines()
        self.draw()

    def stepByStep(self):
        # print("Step by step")
        if self.step == 0:
            print("Running Voronoi algorithm...")
            self.run_voronoi()
            self.init_canvas()
            self.plot_points()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 1:
            print("Step 1 : Displaying left convex hull...")
            self.plot_left_hull()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 2:
            print("Step 2 : Displaying right convex hull...")
            self.plot_right_hull()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 3:
            print("Step 3 : Displaying tangent...")
            self.plot_tangent()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 4:
            print("Step 4 : Displaying output left convex hull...")
            self.init_canvas()
            self.plot_points()
            self.plot_tangent()
            self.plot_output_left()
            self.plot_right_hull()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 5:
            print("Step 5 : Displaying output right convex hull...")
            self.init_canvas()
            self.plot_points()
            self.plot_tangent()
            self.plot_output_left()
            self.plot_output_right()
            self.step += 1
            self.step = self.step % 7
        elif self.step == 6:
            print("Step 6 : Displaying hyperplane...")
            print(self.SBS_count)
            self.init_canvas()
            self.plot_points()
            if self.SBS_count == -1:
                self.plot_tangent()
                self.plot_left_voronoi()
                self.plot_right_voronoi()
            elif self.SBS_count < len(self.SBS_hp):
                self.plot_SBS(self.SBS_count)
            else:
                self.plot_SBS_finally()
                self.step += 1
                self.step = self.step % 7
            self.SBS_count += 1
            self.draw()
            
            
            
    
    def clean(self):
        print("Cleaning canvas...")

        self.ax.clear()
        self.points.clear()
        self.edges.clear()
        self.left_edges.clear()
        self.right_edges.clear()
        
        self.left_voronoi.clear()
        self.right_voronoi.clear()
        
        self.left_hull.clear()
        self.right_hull.clear()
        self.left_delete_hull.clear()
        self.right_delete_hull.clear()
        self.merge_hull.clear()
        self.tangent.clear()
        
        self.test_sets.clear()
        self.test_set_index = 0
        
        self.step = 0
        self.SBS_hp.clear()
        self.SBS_output.clear()
        self.SBS_count = -1
        self.SBS_tangent.clear()
        
        self.init_canvas()

    def next_set(self):
        if self.test_sets:
            if self.test_set_index < len(self.test_sets):
                print(f"Displaying test set {self.test_set_index + 1}.")
                self.ax.clear()
                self.points.clear()
                self.edges.clear()
                self.left_edges.clear()
                self.right_edges.clear()
                
                self.left_voronoi.clear()
                self.right_voronoi.clear()
                
                self.left_hull.clear()
                self.right_hull.clear()
                self.left_delete_hull.clear()
                self.right_delete_hull.clear()
                self.merge_hull.clear()
                self.tangent.clear()
                
                self.step = 0
                self.SBS_count = -1
                self.SBS_hp = []
                self.SBS_output = []
                self.SBS_tangent = []
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
                # self.ax.clear()
                # self.init_canvas()
                # self.test_sets.clear()
                # self.test_set_index = 0
                # self.points.clear()
                # self.edges.clear()
                self.clean()
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

        # print(self.points)
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
            return ([])
        elif len(points_sort) == 2:
            edges = self.plot_two_points(points_sort)
            return edges
        elif len(points_sort) == 3:
            edges = self.plot_three_points(points_sort)
            return edges

        mid = len(points_sort) // 2 # 向下取整數
        left_points = points_sort[:mid]
        right_points = points_sort[mid:]

        left_edges = self.divide_and_conquer(left_points)
        self.left_voronoi.clear()
        for edge in left_edges:
            self.left_voronoi.append(edge)
            
        right_edges = self.divide_and_conquer(right_points)
        self.right_voronoi.clear()
        for edge in right_edges:
            self.right_voronoi.append(edge)
        
        # if left_edges:
        #     for edge in left_edges:
        #         x_values = [edge[0], edge[2]]
        #         y_values = [edge[1], edge[3]]
        #         self.ax.plot(x_values, y_values, 'green')
                
        # if right_edges:
        #     for edge in right_edges:
        #         x_values = [edge[0], edge[2]]
        #         y_values = [edge[1], edge[3]]
        #         self.ax.plot(x_values, y_values, 'orange')
        # self.draw()

        self.merge_voronoi(left_points, right_points)
        edges = self.hyperplane(left_edges, right_edges)
        return edges
        
    def merge_voronoi(self, left_points, right_points):
        # convex_hull
        left_hull = self.convex_hull(left_points)
        self.left_hull.clear()
        for point in left_hull:
            self.left_hull.append(point)
        # self.plot_left_hull()
        
        right_hull = self.convex_hull(right_points)
        self.right_hull.clear()
        for point in right_hull:
            self.right_hull.append(point)
        # self.plot_right_hull()
        
        merge_hull, left_delete_hull, right_delete_hull, upper_left, upper_right, lower_left, lower_right = self.merge_convex_hull(left_hull, right_hull)
        
        self.left_delete_hull.clear()
        for point in left_delete_hull:
            self.left_delete_hull.append(point)
        self.right_delete_hull.clear()
        for point in right_delete_hull:
            self.right_delete_hull.append(point)
        self.merge_hull.clear()
        for point in merge_hull:
            self.merge_hull.append(point)
        self.tangent.clear()
        self.tangent.append(upper_left)
        self.tangent.append(upper_right)
        self.tangent.append(lower_left)
        self.tangent.append(lower_right)
        
        # self.init_canvas()
        # self.plot_points()
        
        # self.plot_output_left()
        # self.plot_output_right()
        # self.plot_tangent()
        
        ################################################################################################
        # 尋找HYPERPLANE
        
    def hyperplane(self, left_edges, right_edges):
        self.SBS_hp.clear()
        self.SBS_output.clear()
        self.SBS_tangent.clear()
        
        hp_edges = []
        hp_point1 = self.tangent[0]
        # print(f"hp_point1:{hp_point1}")
        hp_point2 = self.tangent[1]
        # print(f"hp_point2:{hp_point2}")
        # hp_point1 = upper_left[0], upper_left[1]
        # hp_point2 = upper_right[0], upper_right[1]
        a_hp, b_hp = self.perpendicular_line_params(self.tangent[0][0], self.tangent[0][1], self.tangent[1][0], self.tangent[1][1])
        a_vp, b_vp = self.perpendicular_line_params(self.tangent[2][0], self.tangent[2][1], self.tangent[3][0], self.tangent[3][1])
        
        border_a, border_b = self.border_points(a_hp, b_hp)
        if border_b[1] > border_a[1]:
            border_a, border_b = border_b, border_a
        if a_hp == None:
            border_a = [(hp_point1[0]+hp_point2[0])/2, 10**15]
        elif a_hp == 0:
            border_a = [0, hp_point1[1]]
        else:
            y = 10**15
            x = (y - b_hp) / a_hp
            border_a = [x, y]
        # print(f"border_a:{border_a}")
        # print(f"border_b:{border_b}")
        # print("--------------------")
        
        # 建立一個array，用來確認left與right的index是否有被使用過
        left_index = [0] * len(left_edges)
        right_index = [0] * len(right_edges)
        # print(f"left_index length:{len(left_index)}")
        # print(f"right_index length:{len(right_index)}")
        
        while True:
            temp = []
            temp.append(hp_point1[0])
            temp.append(hp_point1[1])
            temp.append(hp_point2[0])
            temp.append(hp_point2[1])
            self.SBS_tangent.append((temp))
            intersection_left = []
            intersection_right = []

            # 尋找hp與所有left_edges的交點，並且存入intersection_left
            for i in range(len(left_edges)):
                if left_index[i] == 1:
                    continue
                edge = left_edges[i]
                x1, y1, x2, y2 = edge[0], edge[1], edge[2], edge[3]
                a, b = self.two_points_find_ab(x1, y1, x2, y2)
                x, y = self.find_intersection(a_hp, b_hp, a, b)
                if x != None and y != None:
                    # 檢查此點是否在(x1, y1)與(x2, y2)之間
                    if self.is_between(x1, x2, x) and self.is_between(y1, y2, y) and y <= border_a[1]:
                        intersection_left.append((x, y, i))
                    # self.intersection_left.append((x, y))
            # print(f"intersection_left_length:{len(self.intersection_left)}")
            
            # 尋找hp與所有right_edges的交點，並且存入intersection_right
            for i in range(len(right_edges)):
                if right_index[i] == 1:
                    continue
                edge = right_edges[i]
                x1, y1, x2, y2 = edge[0], edge[1], edge[2], edge[3]
                a, b = self.two_points_find_ab(x1, y1, x2, y2)
                x, y = self.find_intersection(a_hp, b_hp, a, b)
                
                if x != None and y != None:
                    # 檢查此點是否在(x1, y1)與(x2, y2)之間
                    if self.is_between(x1, x2, x) and self.is_between(y1, y2, y) and y <= border_a[1]:
                        intersection_right.append((x, y, i))
                    # self.intersection_right.append((x, y))
            # print(f"intersection_right_length:{len(self.intersection_right)}")
                    
            # 遍尋intersection_left與intersection_right，尋找y最大的點
            y_max = float('-inf')
            index = -1
            flag = 0
            for i in range(len(intersection_left)):
                if intersection_left[i][1] > y_max:
                    index = i
                    y_max = intersection_left[i][1]
            for i in range(len(intersection_right)):
                if intersection_right[i][1] > y_max:
                    index = i
                    y_max = intersection_right[i][1]
                    flag = 1
            
            if index == -1:
                break
            
            if flag == 0:
                idx = intersection_left[index][2]
                # 標示為已使用
                left_index[idx] = 1
                
                # hp轉向點
                border_b = [intersection_left[index][0], intersection_left[index][1]]
                # print(f"border_b:{border_b}")
                
                # 將此段hp加入edges
                hp_edges.append([border_a[0], border_a[1], border_b[0], border_b[1], hp_point1[0], hp_point1[1], hp_point2[0], hp_point2[1]])
                # self.SBS_hp.append(hp_edges) #TODO
                # print(f"hp:{border_a[0], border_a[1], border_b[0], border_b[1]}")
                
                # 刪線
                if left_edges[idx][0] < left_edges[idx][2]:
                    left_edges[idx][2], left_edges[idx][3] = border_b[0], border_b[1]
                else:
                    left_edges[idx][0], left_edges[idx][1] = border_b[0], border_b[1]
                                
                # hp轉向
                if hp_point1[0] == left_edges[idx][4] and hp_point1[1] == left_edges[idx][5]:
                    hp_point1 = left_edges[idx][6], left_edges[idx][7]
                elif hp_point1[0] == left_edges[idx][6] and hp_point1[1] == left_edges[idx][7]:
                    hp_point1 = left_edges[idx][4], left_edges[idx][5]
                elif hp_point2[0] == left_edges[idx][4] and hp_point2[1] == left_edges[idx][5]:
                    hp_point2 = left_edges[idx][6], left_edges[idx][7]
                elif hp_point2[0] == left_edges[idx][6] and hp_point2[1] == left_edges[idx][7]:
                    hp_point2 = left_edges[idx][4], left_edges[idx][5]
                # print(f"hp_point1:{hp_point1}")
                # print(f"hp_point2:{hp_point2}")
                a_hp, b_hp = self.perpendicular_line_params(hp_point1[0], hp_point1[1], hp_point2[0], hp_point2[1])

            else:
                idx = intersection_right[index][2]
                right_index[idx] = 1
                border_b = [intersection_right[index][0], intersection_right[index][1]]
                hp_edges.append([border_a[0], border_a[1], border_b[0], border_b[1], hp_point1[0], hp_point1[1], hp_point2[0], hp_point2[1]])
                # self.SBS_hp.append(hp_edges) #TODO
                
                if right_edges[idx][0] < right_edges[idx][2]:
                    right_edges[idx][0], right_edges[idx][1] = border_b[0], border_b[1]
                else:
                    right_edges[idx][2], right_edges[idx][3] = border_b[0], border_b[1]
                                    
                if hp_point1[0] == right_edges[idx][4] and hp_point1[1] == right_edges[idx][5]:
                    hp_point1 = right_edges[idx][6], right_edges[idx][7]
                elif hp_point1[0] == right_edges[idx][6] and hp_point1[1] == right_edges[idx][7]:
                    hp_point1 = right_edges[idx][4], right_edges[idx][5]
                elif hp_point2[0] == right_edges[idx][4] and hp_point2[1] == right_edges[idx][5]:
                    hp_point2 = right_edges[idx][6], right_edges[idx][7]
                elif hp_point2[0] == right_edges[idx][6] and hp_point2[1] == right_edges[idx][7]:
                    hp_point2 = right_edges[idx][4], right_edges[idx][5]
                a_hp, b_hp = self.perpendicular_line_params(hp_point1[0], hp_point1[1], hp_point2[0], hp_point2[1])
                
            border_a = border_b
            
            temp = []
            for edge in left_edges:
                temp.append(edge) #TODO
            for edge in right_edges:
                temp.append(edge) #TODO
            self.SBS_output.append([temp]) #TODO
        
        # 劃出最後一段的hp
        end1, end2 = self.border_points(a_vp, b_vp)
        if end1[1] > end2[1]:
            border_b = end2
        else:
            border_b = end1
        hp_edges.append([border_a[0], border_a[1], border_b[0], border_b[1], self.tangent[2][0], self.tangent[2][1], self.tangent[3][0], self.tangent[3][1]])
        # self.SBS_hp.append(hp_edges) #TODO
        
        # for edge in edges:
        #     print(int(edge[0]), int(edge[1]), int(edge[2]), int(edge[3]))
        
        for edge in hp_edges:
            self.SBS_hp.append(edge)
        
        output_left = []
        output_right = []
        # 檢查left_index，若為1則將其加入output_left
        for i in range(len(left_index)):
            if left_index[i] == 1:
                output_left.append(left_edges[i])
            else:
                a, b = self.two_points_find_ab(left_edges[i][0], left_edges[i][1], left_edges[i][2], left_edges[i][3])
                flag = 0
                for j in range(len(hp_edges)):
                    temp_a, temp_b = self.two_points_find_ab(hp_edges[j][0], hp_edges[j][1], hp_edges[j][2], hp_edges[j][3])
                    temp_x, temp_y = self.find_intersection(a, b, temp_a, temp_b)
                    if self.is_between(hp_edges[j][0], hp_edges[j][2], temp_x) and self.is_between(hp_edges[j][1], hp_edges[j][3], temp_y):
                        flag = 1
                        break
                if flag == 0:
                    output_left.append(left_edges[i])
                else:
                    if left_edges[i][0] < left_edges[i][2]:
                        if self.is_between(left_edges[i][0], temp_x, left_edges[i][2]):
                            output_left.append(left_edges[i])
                    elif left_edges[i][0] > left_edges[i][2]:
                        if self.is_between(left_edges[i][2], temp_x, left_edges[i][0]):
                            output_left.append(left_edges[i])

        # 檢查right_index，若為1則將其加入output_right
        for i in range(len(right_index)):
            if right_index[i] == 1:
                output_right.append(right_edges[i])
            else:
                a, b = self.two_points_find_ab(right_edges[i][0], right_edges[i][1], right_edges[i][2], right_edges[i][3])
                flag = 0
                for j in range(len(hp_edges)):
                    temp_a, temp_b = self.two_points_find_ab(hp_edges[j][0], hp_edges[j][1], hp_edges[j][2], hp_edges[j][3])
                    temp_x, temp_y = self.find_intersection(a, b, temp_a, temp_b)
                                            
                    if temp_x != None and temp_y != None:
                        if self.is_between(hp_edges[j][0], hp_edges[j][2], temp_x) and self.is_between(hp_edges[j][1], hp_edges[j][3], temp_y):
                            flag = 1
                            break
                if flag == 0:
                    output_right.append(right_edges[i])
                else:
                    if right_edges[i][0] < right_edges[i][2]:
                        if self.is_between(right_edges[i][2], temp_x, right_edges[i][0]):
                            output_right.append(right_edges[i])
                    elif right_edges[i][0] > right_edges[i][2]:
                        if self.is_between(right_edges[i][0], temp_x, right_edges[i][2]):
                            output_right.append(right_edges[i])
        temp = []
        for edge in output_left:
            temp.append(edge)
        for edge in output_right:
            temp.append(edge)
        self.SBS_output.append(temp) #TODO
                
        
        # 劃出edges中的所有線段
        # for edge in edges:
        #     x_values = [edge[0], edge[2]]
        #     y_values = [edge[1], edge[3]]
        #     self.ax.plot(x_values, y_values, 'pink')
            
        for edge in output_left:
            hp_edges.append(edge)
            # x_values = [edge[0], edge[2]]
            # y_values = [edge[1], edge[3]]
            # self.ax.plot(x_values, y_values, 'blue')
            
        for edge in output_right:
            hp_edges.append(edge)
            # x_values = [edge[0], edge[2]]
            # y_values = [edge[1], edge[3]]
            # self.ax.plot(x_values, y_values, 'purple')
            
        print(f"SBShp:{len(self.SBS_hp)}")    
        print(f"SBSoutput:{len(self.SBS_output)}")
        print(f"SBStangent:{len(self.SBS_tangent)}")
        
        # print(f"SBS_hp:{self.SBS_hp}")
        # print(f"SBS_output:{self.SBS_output}")
        # print(f"SBS_tangent:{self.SBS_tangent}")
        
        return hp_edges
    
    def convex_hull(self, points):
        if len(points) == 1:
            return points
        elif len(points) == 2:
            if points[0][0] > points[1][0]:
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
            # 找到左凸包x最大的點
            left_idx = 0
            for i in range(1, len(left_convex)):
                if left_convex[i][0] > left_convex[left_idx][0]:
                    left_idx = i
                    
            # 找到右凸包x最小的點
            right_idx = 0
            for i in range(1, len(right_convex)):
                if right_convex[i][0] < right_convex[right_idx][0]:
                    right_idx = i
            while True:
                updated = False
                # 固定左凸包的索引 遍尋右凸包的索引
                for i in range(len(right_convex)):
                    result = orientation(left_convex[left_idx], right_convex[right_idx], right_convex[i])
                    if result == -1:
                        right_idx = i
                        updated = True
                    elif result == 0:
                        if self.two_points_distance(left_convex[left_idx][0], left_convex[left_idx][1], right_convex[right_idx][0], right_convex[right_idx][1]) > self.two_points_distance(left_convex[left_idx][0], left_convex[left_idx][1], right_convex[i][0], right_convex[i][1]):
                            right_idx = i
                            updated = True
                        
                # 固定右凸包的索引 遍尋左凸包的索引
                for i in range(len(left_convex)):
                    result = orientation(right_convex[right_idx], left_convex[left_idx], left_convex[i])
                    if result == 1:
                        left_idx = i
                        updated = True
                    elif result == 0:
                        if self.two_points_distance(right_convex[right_idx][0], right_convex[right_idx][1], left_convex[left_idx][0], left_convex[left_idx][1]) > self.two_points_distance(right_convex[right_idx][0], right_convex[right_idx][1], left_convex[i][0], left_convex[i][1]):
                            left_idx = i
                            updated = True
                
                if not updated:
                    break
            return left_idx, right_idx

        def find_lower_tangent():
            """找到左凸包與右凸包的下切線"""
            # 找到左凸包x最大的點
            left_idx = 0
            for i in range(1, len(left_convex)):
                if left_convex[i][0] > left_convex[left_idx][0]:
                    left_idx = i
                    
            # 找到右凸包x最小的點
            right_idx = 0
            for i in range(1, len(right_convex)):
                if right_convex[i][0] < right_convex[right_idx][0]:
                    right_idx = i
            
            while True:
                updated = False
                # 固定左凸包的索引 遍尋右凸包的索引
                for i in range(len(right_convex)):
                    result = orientation(left_convex[left_idx], right_convex[right_idx], right_convex[i])
                    if result == 1:
                        right_idx = i
                        updated = True
                    elif result == 0:
                        if self.two_points_distance(left_convex[left_idx][0], left_convex[left_idx][1], right_convex[right_idx][0], right_convex[right_idx][1]) > self.two_points_distance(left_convex[left_idx][0], left_convex[left_idx][1], right_convex[i][0], right_convex[i][1]):
                            right_idx = i
                            updated = True
                        
                # 固定右凸包的索引 遍尋左凸包的索引
                for i in range(len(left_convex)):
                    result = orientation(right_convex[right_idx], left_convex[left_idx], left_convex[i])
                    if result == -1:
                        left_idx = i
                        updated = True
                    elif result == 0:
                        if self.two_points_distance(right_convex[right_idx][0], right_convex[right_idx][1], left_convex[left_idx][0], left_convex[left_idx][1]) > self.two_points_distance(right_convex[right_idx][0], right_convex[right_idx][1], left_convex[i][0], left_convex[i][1]):
                            left_idx = i
                            updated = True
                            
                if not updated:
                    break
                
            return left_idx, right_idx
        
        # print("Left convex hull:")
        # for point in left_convex:
        #     print(point)
        # print("Right convex hull:")
        # for point in right_convex:
        #     print(point)
        
        # 找到上下切線
        upper_left, upper_right = find_upper_tangent()
        lower_left, lower_right = find_lower_tangent()
        # print(f"Upper tangent: {left_convex[upper_left]} - {right_convex[upper_right]}")
        # print(f"Lower tangent: {left_convex[lower_left]} - {right_convex[lower_right]}")

        # 合併凸包
        merged_hull = []
        output_left = []
        output_right = []
        # 添加左凸包的有效點
        idx = upper_left 
        while True:
            # print(f"Left convex: {left_convex[idx]}")
            output_left.append(left_convex[idx])
            merged_hull.append(left_convex[idx])

            # 如果到達 lower_left，停止
            if idx == lower_left:
                break

            # 順時針方向移動索引
            idx = (idx + 1) % len(left_convex)

        # 添加右凸包的有效點
        idx = lower_right
        while True:
            # print(f"Right convex: {right_convex[idx]}")
            output_right.append(right_convex[idx])
            merged_hull.append(right_convex[idx])

            # 如果到達 upper_right，停止
            if idx == upper_right:
                break

            # 順時針方向移動索引
            idx = (idx + 1) % len(right_convex)

        return merged_hull, output_left, output_right, left_convex[upper_left], right_convex[upper_right], left_convex[lower_left], right_convex[lower_right]
    
    
    
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
        edges.append([x_values[0], y_values[0], x_values[1], y_values[1], x1, y1, x2, y2])
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
                edges.append([0, mid_y12, 600, mid_y12, x1, y1, x2, y2])
                edges.append([0, mid_y13, 600, mid_y13, x1, y1, x3, y3])
            elif (y2 > y1 and y2 < y3) or (y2 < y1 and y2 > y3): # y2為中間點
                edges.append([0, mid_y12, 600, mid_y12, x1, y1, x2, y2])
                edges.append([0, mid_y23, 600, mid_y23, x2, y2, x3, y3])
            elif (y3 > y1 and y3 < y2) or (y3 < y1 and y3 > y2): # y3為中間點
                edges.append([0, mid_y13, 600, mid_y13, x1, y1, x3, y3])
                edges.append([0, mid_y23, 600, mid_y23, x2, y2, x3, y3])
        elif y1 == y2 and y2 == y3: # 三點在同一條水平線上
            # 由x的大小找出中間的點
            if (x1 > x2 and x1 < x3) or (x1 < x2 and x1 > x3): # x1為中間點
                edges.append([mid_x12, 0, mid_x12, 600, x1, y1, x2, y2])
                edges.append([mid_x13, 0, mid_x13, 600, x1, y1, x3, y3])
            elif (x2 > x1 and x2 < x3) or (x2 < x1 and x2 > x3): # x2為中間點
                edges.append([mid_x12, 0, mid_x12, 600, x1, y1, x2, y2])
                edges.append([mid_x23, 0, mid_x23, 600, x2, y2, x3, y3])
            elif (x3 > x1 and x3 < x2) or (x3 < x1 and x3 > x2): # x3為中間點
                edges.append([mid_x13, 0, mid_x13, 600, x1, y1, x3, y3])
                edges.append([mid_x23, 0, mid_x23, 600, x2, y2, x3, y3])
        elif a12 == a23: # 三點共線但不為垂直線
            if (y1 > y2 and y1 < y3) or (y1 < y2 and y1 > y3): # y1為中間點
                a, b = self.perpendicular_line_params(x1, y1, x2, y2)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x2, y2])
                a, b = self.perpendicular_line_params(x1, y1, x3, y3)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x3, y3])
            elif (y2 > y1 and y2 < y3) or (y2 < y1 and y2 > y3): # y2為中間點
                a, b = self.perpendicular_line_params(x1, y1, x2, y2)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x2, y2])
                a, b = self.perpendicular_line_params(x2, y2, x3, y3)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x2, y2, x3, y3])
            elif (y3 > y1 and y3 < y2) or (y3 < y1 and y3 > y2): # y3為中間點
                a, b = self.perpendicular_line_params(x1, y1, x3, y3)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x1, y1, x3, y3])
                a, b = self.perpendicular_line_params(x2, y2, x3, y3)
                temp = self.border_points(a, b)
                edges.append([temp[0][0], temp[0][1], temp[1][0], temp[1][1], x2, y2, x3, y3])
        else:
            triangle_type, angle = self.is_obtuse_triangle(x1, y1, x2, y2, x3, y3)

            # 計算三角形的外心
            pb_a12, pb_b12 = self.perpendicular_line_params(x1, y1, x2, y2)
            pb_a23, pb_b23 = self.perpendicular_line_params(x2, y2, x3, y3)
            pb_a13, pb_b13 = self.perpendicular_line_params(x1, y1, x3, y3)
            
            x, y = self.find_intersection(pb_a12, pb_b12, pb_a23, pb_b23)
            # print(f"Outer center: ({x}, {y})")
            # 繪製外心
            # self.ax.plot(x, y, 'ro')
            # self.draw()
            
            if triangle_type == 2: # 銳角
                temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                edges.append([x, y, temp[0], temp[1], x1, y1, x2, y2])
                temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                edges.append([x, y, temp[0], temp[1], x2, y2, x3, y3])
                temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                edges.append([x, y, temp[0], temp[1], x1, y1, x3, y3])
                self.draw()
            else: # 鈍角 直角
                if angle == 'A':
                    temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                    edges.append([x, y, temp[0], temp[1], x1, y1, x2, y2])
                    temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                    edges.append([x, y, temp[0], temp[1], x1, y1, x3, y3])
                elif angle == 'B':
                    temp = self.line_points(x, y, mid_x12, mid_y12, 0)
                    edges.append([x, y, temp[0], temp[1], x1, y1, x2, y2])
                    temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                    edges.append([x, y, temp[0], temp[1], x2, y2, x3, y3])
                else:
                    temp = self.line_points(x, y, mid_x13, mid_y13, 0)
                    edges.append([x, y, temp[0], temp[1], x1, y1, x3, y3])
                    temp = self.line_points(x, y, mid_x23, mid_y23, 0)
                    edges.append([x, y, temp[0], temp[1], x2, y2, x3, y3])
                
                if triangle_type == 0: # 鈍角
                    if angle == 'A':
                        temp = self.line_points(x, y, mid_x23, mid_y23, 1)
                        edges.append([x, y, temp[0], temp[1], x2, y2, x3, y3])
                    elif angle == 'B':
                        temp = self.line_points(x, y, mid_x13, mid_y13, 1)
                        edges.append([x, y, temp[0], temp[1], x1, y1, x3, y3])
                    else:
                        temp = self.line_points(x, y, mid_x12, mid_y12, 1)
                        edges.append([x, y, temp[0], temp[1], x1, y1, x2, y2])
                elif triangle_type == 1: # 直角
                    if angle == 'A':
                        temp_A, temp_B = self.border_points(pb_a23, pb_b23)
                        if math.dist((x1, y1), temp_A) > math.dist((x1, y1), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append([x, y, temp[0], temp[1], x2, y2, x3, y3])
                    elif angle == 'B':
                        temp_A, temp_B = self.border_points(pb_a13, pb_b13)
                        if math.dist((x2, y2), temp_A) > math.dist((x2, y2), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append([x, y, temp[0], temp[1], x1, y1, x3, y3])
                    else:
                        temp_A, temp_B = self.border_points(pb_a12, pb_b12)
                        if math.dist((x3, y3), temp_A) > math.dist((x3, y3), temp_B):
                            temp = temp_A
                        else:
                            temp = temp_B
                        edges.append([x, y, temp[0], temp[1], x1, y1, x2, y2])
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
    
    # 給予兩個點，計算兩個點的距離
    def two_points_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    # 給予兩條直線的斜率和截距，計算交點
    def find_intersection(self, a1, b1, a2, b2):
        # 檢查斜率是否相同，若相同則兩條直線平行，沒有交點
        # print(a1, b1, a2, b2)
        
        if a1 == a2:
            print("The lines are parallel, no intersection.")
            return None, None
        
        if (a1 == None and b1 == None) or (a2 == None and b2 == None):
            return None, None
        
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
                temp_point.append([0, y_at_x_min])
            # (600, y)
            y_at_x_max = a * 600 + b
            if y_at_x_max >= 0 and y_at_x_max <= 600:
                temp_point.append([600, y_at_x_max])
            # (x, 0)
            x_at_y_min = (0 - b) / a
            if x_at_y_min >= 0 and x_at_y_min <= 600:
                temp_point.append([x_at_y_min, 0])
            # (x, 600)
            x_at_y_max = (600 - b) / a
            if x_at_y_max >= 0 and x_at_y_max <= 600:
                temp_point.append([x_at_y_max, 600])
            return temp_point[0], temp_point[1]
    
    # 計算中點
    def mid_point(self, x1, y1, x2, y2):
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        return mid_x, mid_y
    
    # 檢查 c 是否位於 a 和 b 之間（包括邊界）
    def is_between(self, a, b, c):
        try:
            return min(a, b) <= c <= max(a, b)
        except TypeError:
            return False
    
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
                        self.points.append([int(x), int(y)])
                        # print(f"Added point: ({x}, {y})")
                        
                    if line.startswith("E"):
                        x1, y1, x2, y2 = map(float, line.split()[1:])
                        self.edges.append([int(x1), int(y1), int(x2), int(y2), 99999, 99999, 99999, 99999])
                        # print(f"Added edge: ({x1}, {y1}) to ({x2}, {y2})")
                        
                # 顯示讀取的點
                # for point in self.points:
                #     print(f"Point: {point}")
                # for edge in self.edges:
                #     print(f"Edge: {edge}")
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
                # for i, test_set in enumerate(self.test_sets):
                #     print(f"Test set {i + 1} ({len(test_set)} points): {test_set}")
                # print("File processing completed.\n")
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
        
        btn_stepByStep = QPushButton("StepByStep")
        btn_stepByStep.clicked.connect(self.canvas.stepByStep)
        
        btn_clean = QPushButton("Clean")
        btn_clean.clicked.connect(self.canvas.clean)
        
        btn_next_set = QPushButton("NextSet")
        btn_next_set.clicked.connect(self.canvas.next_set)
        
        btn_open_file = QPushButton("OpenFile")
        btn_open_file.clicked.connect(self.canvas.open_file)
        
        btn_save_file = QPushButton("SaveFile")
        btn_save_file.clicked.connect(self.canvas.save_file)

        # Set the width to half and height to double
        for btn in [btn_run, btn_stepByStep, btn_clean, btn_next_set, btn_open_file, btn_save_file]:
            btn.setFixedWidth(150)  # Half the usual width (default might be around 200)
            btn.setFixedHeight(60)  # Double the usual height (default might be around 30)

        # Add buttons to the layout
        button_layout.addWidget(btn_run)
        button_layout.addWidget(btn_stepByStep)
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
