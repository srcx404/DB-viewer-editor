import os
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QAction, QFileDialog, QTreeWidget, QTreeWidgetItem,
                            QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTextEdit, QPushButton, QMessageBox, QTabWidget, QLabel,
                            QStatusBar, QAbstractItemView, QInputDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QEvent
from db_connector import DBConnector

class DBViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
        self.current_table = None
        self.db_modified = False  # 添加修改状态跟踪
        self.init_ui()

    def init_ui(self):
        # 设置窗口
        self.setWindowTitle('DB-Viewer-Editor')
        # self.setWindowIcon(QIcon('build/i.png'))
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('准备就绪')

        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        
        # 打开数据库动作
        open_action = QAction('打开数据库', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_database)
        file_menu.addAction(open_action)
        
        # 添加保存操作
        save_action = QAction('保存修改', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_changes)
        file_menu.addAction(save_action)
        
        # 添加编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        # 添加刷新表格操作
        refresh_action = QAction('刷新当前表', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_current_table)
        edit_menu.addAction(refresh_action)
        
        # 添加表格修改操作
        add_row_action = QAction('添加行', self)
        add_row_action.triggered.connect(self.add_row_dialog)
        edit_menu.addAction(add_row_action)
        
        delete_row_action = QAction('删除选中行', self)
        delete_row_action.triggered.connect(self.delete_selected_rows)
        edit_menu.addAction(delete_row_action)
        
        # 退出动作
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧树状视图
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('数据库结构')
        self.tree.setMinimumWidth(250)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        splitter.addWidget(self.tree)
        
        # 右侧部分
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建表格视图
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 允许编辑单元格
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        # 连接单元格修改信号
        self.table.itemChanged.connect(self.on_cell_changed)
        
        # 创建 SQL 查询区域
        sql_layout = QHBoxLayout()
        self.sql_input = QTextEdit()
        self.sql_input.setMaximumHeight(100)
        self.sql_input.setPlaceholderText("输入 SQL 查询...")
        
        execute_button = QPushButton("执行")
        execute_button.clicked.connect(self.execute_query)
        execute_button.setMaximumWidth(100)
        
        sql_layout.addWidget(self.sql_input)
        sql_layout.addWidget(execute_button)
        
        right_layout.addWidget(self.table, stretch=4)
        right_layout.addLayout(sql_layout, stretch=1)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([250, 950])
        
        main_layout.addWidget(splitter)
    
    def open_database(self):
        # 在打开新数据库前检查是否有未保存的修改
        if self.db is not None and self.db_modified:
            reply = QMessageBox.question(self, '未保存的修改', 
                                        '当前数据库有未保存的修改，是否保存？',
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                        QMessageBox.Save)
            
            if reply == QMessageBox.Save:
                self.save_changes()
            elif reply == QMessageBox.Cancel:
                return
            # Discard 什么都不做，继续打开新数据库
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "打开数据库文件", "", 
            "数据库文件 (*.db *.sqlite *.sqlite3);;所有文件 (*)", 
            options=options
        )
        
        if file_name:
            try:
                self.db = DBConnector(file_name)
                self.db_modified = False  # 重置修改状态
                self.refresh_tree()
                self.statusBar.showMessage(f'已连接到数据库: {os.path.basename(file_name)}')
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开数据库: {str(e)}")
    
    def save_changes(self):
        """保存所有数据库修改"""
        if self.db is None:
            return
            
        if not self.db_modified:
            self.statusBar.showMessage('没有需要保存的修改')
            return
            
        try:
            self.db.commit()
            self.db_modified = False
            self.statusBar.showMessage('所有修改已保存')
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存修改: {str(e)}")
    
    def refresh_tree(self):
        if not self.db:
            return
            
        self.tree.clear()
        
        # 添加表
        tables_item = QTreeWidgetItem(self.tree)
        tables_item.setText(0, "表")
        tables_item.setExpanded(True)
        
        for table in self.db.get_tables():
            table_item = QTreeWidgetItem(tables_item)
            table_item.setText(0, table)
            table_item.setData(0, Qt.UserRole, {"type": "table", "name": table})
            
            # 添加列
            columns = self.db.get_columns(table)
            for column in columns:
                col_item = QTreeWidgetItem(table_item)
                col_item.setText(0, f"{column[0]} ({column[1]})")
        
    def on_tree_item_clicked(self, item):
        data = item.data(0, Qt.UserRole)
        if data and data["type"] == "table":
            self.current_table = data["name"]
            self.display_table_data(data["name"])
            
    def refresh_current_table(self):
        if self.current_table:
            self.display_table_data(self.current_table)
            
    def display_table_data(self, table_name):
        if not self.db:
            return
            
        try:
            # 断开itemChanged信号，避免加载数据时触发更新
            self.table.itemChanged.disconnect(self.on_cell_changed)
            
            data, headers = self.db.get_table_data(table_name)
            
            self.table.clear()
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            
            self.table.setRowCount(len(data))
            
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
            
            # 添加：根据内容自动调整列宽
            self.auto_adjust_column_widths(data, headers)
                    
            self.statusBar.showMessage(f"表 '{table_name}' 已加载 ({len(data)} 行)")
            
            # 重新连接itemChanged信号
            self.table.itemChanged.connect(self.on_cell_changed)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载表数据: {str(e)}")
            # 确保信号重新连接
            self.table.itemChanged.connect(self.on_cell_changed)
    
    def on_cell_changed(self, item):
        if not self.db or not self.current_table:
            return
            
        row = item.row()
        col = item.column()
        new_value = item.text()
        
        try:
            # 获取主键，假设是第一列（实际应该查询数据库获取真正的主键）
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            primary_key_col = 0  # 假设第一列是主键
            primary_key_val = self.table.item(row, primary_key_col).text()
            column_name = headers[col]
            
            # 构建更新SQL
            query = f"UPDATE {self.current_table} SET {column_name} = ? WHERE {headers[primary_key_col]} = ?"
            
            # 执行更新但不提交
            self.db.cursor.execute(query, (new_value, primary_key_val))
            self.db_modified = True  # 标记为已修改
            
            self.statusBar.showMessage(f"已更新 {self.current_table}.{column_name} (未保存)")
        except Exception as e:
            QMessageBox.warning(self, "更新失败", str(e))
            self.refresh_current_table()  # 刷新以恢复原始数据
    
    def add_row_dialog(self):
        if not self.current_table or not self.db:
            QMessageBox.warning(self, "警告", "请先选择一个表")
            return
            
        try:
            # 获取表的列结构
            columns = self.db.get_columns(self.current_table)
            column_names = [col[0] for col in columns]
            
            # 构建插入SQL
            placeholders = ", ".join(["?"] * len(column_names))
            columns_str = ", ".join(column_names)
            
            values = []
            for col_name in column_names:
                value, ok = QInputDialog.getText(self, f"添加行", f"请输入 {col_name} 的值:")
                if not ok:
                    return  # 用户取消
                values.append(value)
            
            # 执行插入但不提交
            query = f"INSERT INTO {self.current_table} ({columns_str}) VALUES ({placeholders})"
            self.db.cursor.execute(query, values)
            self.db_modified = True  # 标记为已修改
            
            # 刷新表格
            self.refresh_current_table()
            self.statusBar.showMessage(f"已向表 {self.current_table} 添加新行 (未保存)")
        except Exception as e:
            QMessageBox.warning(self, "添加失败", str(e))
    
    def delete_selected_rows(self):
        if not self.current_table or not self.db:
            QMessageBox.warning(self, "警告", "请先选择一个表")
            return
            
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return
            
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要从表 {self.current_table} 删除 {len(selected_rows)} 行数据吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
            
        try:
            # 获取主键列（假设是第一列）
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            primary_key_col = 0
            
            # 执行删除操作
            deleted_count = 0
            for row in sorted(selected_rows, reverse=True):  # 从后向前删除，避免索引变化
                primary_key_val = self.table.item(row, primary_key_col).text()
                self.db.cursor.execute(f"DELETE FROM {self.current_table} WHERE {headers[primary_key_col]} = ?", 
                                      (primary_key_val,))
                deleted_count += 1
                
            # 标记为已修改但不提交
            self.db_modified = True
            
            # 刷新表格
            self.refresh_current_table()
            self.statusBar.showMessage(f"已从表 {self.current_table} 删除 {deleted_count} 行 (未保存)")
        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))
    
    def execute_query(self):
        if not self.db:
            QMessageBox.warning(self, "警告", "请先打开数据库")
            return
            
        query = self.sql_input.toPlainText().strip()
        if not query:
            return
            
        try:
            data, headers = self.db.execute_query(query)
            
            self.table.clear()
            if headers:
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                
                self.table.setRowCount(len(data))
                
                for row_idx, row in enumerate(data):
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.table.setItem(row_idx, col_idx, item)
                
                # 添加：自动调整列宽
                self.auto_adjust_column_widths(data, headers)
                
                self.statusBar.showMessage(f"查询已执行，返回 {len(data)} 行")
            else:
                # 如果是非查询操作（如INSERT、UPDATE、DELETE），标记为已修改
                if self.current_table and query.upper().startswith(("INSERT", "UPDATE", "DELETE")):
                    self.db_modified = True
                    self.refresh_current_table()
                self.statusBar.showMessage("查询已执行 (未保存)")
        except Exception as e:
            QMessageBox.critical(self, "SQL 错误", str(e))
            
    def auto_adjust_column_widths(self, data, headers):
        """根据内容自动调整列宽"""
        # 设置列宽基于头部文本和样本数据
        for col_idx, header in enumerate(headers):
            # 先计算标题宽度
            header_width = len(header) * 10 + 30  # 粗略估计标题所需宽度
            
            # 评估前10行数据的宽度
            sample_width = 0
            for row_idx in range(min(10, len(data))):
                if row_idx < len(data) and col_idx < len(data[row_idx]):
                    cell_content = str(data[row_idx][col_idx])
                    content_width = len(cell_content) * 8 + 20  # 粗略估计内容宽度
                    sample_width = max(sample_width, content_width)
            
            # 设置列宽为标题宽度和样本数据宽度的最大值
            column_width = max(header_width, sample_width, 100)  # 至少100像素宽
            self.table.setColumnWidth(col_idx, min(column_width, 300))  # 限制最大宽度为300
    
    def closeEvent(self, event):
        """在关闭窗口前检查是否有未保存的修改"""
        if self.db is not None and self.db_modified:
            reply = QMessageBox.question(self, '未保存的修改', 
                                        '是否保存对数据库的修改？',
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                        QMessageBox.Save)
            
            if reply == QMessageBox.Save:
                self.save_changes()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()  # 取消关闭
        else:
            event.accept()
