import sqlite3

class DBConnector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            # 关闭连接前不自动提交，让应用层控制提交
            self.conn.close()
    
    def get_tables(self):
        # 获取所有表名
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()]
    
    def get_columns(self, table_name):
        # 获取表列信息
        self.cursor.execute(f"PRAGMA table_info('{table_name}')")
        return [(row[1], row[2]) for row in self.cursor.fetchall()]  # (name, type)
    
    def get_table_data(self, table_name, limit=100):
        # 获取表数据
        self.cursor.execute(f"SELECT * FROM '{table_name}' LIMIT {limit}")
        data = self.cursor.fetchall()
        headers = [description[0] for description in self.cursor.description]
        return data, headers
    
    def execute_query(self, query):
        # 执行自定义查询
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        # 如果是SELECT查询，则会有description，否则为None
        if self.cursor.description:
            headers = [description[0] for description in self.cursor.description]
            return data, headers
        else:
            # 不再自动提交非SELECT查询，让应用层控制提交
            return [], []
    
    def commit(self):
        """提交所有待处理的事务"""
        self.conn.commit()
    
    def rollback(self):
        """回滚所有待处理的事务"""
        self.conn.rollback()
