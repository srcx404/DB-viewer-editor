import sqlite3
import os
import random
from datetime import datetime, timedelta

def create_test_database(db_path='test_database.db'):
    """
    创建测试数据库并填充示例数据
    """
    # 如果文件已存在，则先删除
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"正在创建测试数据库: {db_path}")
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        registration_date TEXT NOT NULL,
        last_login TEXT,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    ''')
    
    # 创建产品分类表
    cursor.execute('''
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES categories(id)
    )
    ''')
    
    # 创建产品表
    cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category_id INTEGER NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')
    
    # 创建订单表
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 创建订单明细表
    cursor.execute('''
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')
    
    print("表结构已创建")
    
    # 生成用户数据
    usernames = ["user" + str(i) for i in range(1, 51)]
    emails = [f"user{i}@example.com" for i in range(1, 51)]
    password_hashes = ["hash_" + str(random.randint(10000, 99999)) for _ in range(50)]
    
    now = datetime.now()
    registration_dates = [(now - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(50)]
    last_logins = [(now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(50)]
    is_actives = [random.choice([0, 1]) for _ in range(50)]
    
    users_data = []
    for i in range(50):
        users_data.append((
            i+1, 
            usernames[i], 
            emails[i], 
            password_hashes[i], 
            registration_dates[i], 
            last_logins[i], 
            is_actives[i]
        ))
    
    cursor.executemany(
        "INSERT INTO users (id, username, email, password_hash, registration_date, last_login, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
        users_data
    )
    
    print("已添加 50 个用户数据")
    
    # 生成产品分类数据
    main_categories = [
        (1, "电子产品", "各种电子设备和配件", None),
        (2, "服装", "男女服装和配饰", None),
        (3, "家具", "家居和办公家具", None),
        (4, "食品", "食品和饮料", None),
        (5, "图书", "各类图书和杂志", None)
    ]
    
    sub_categories = [
        (6, "手机", "智能手机和配件", 1),
        (7, "电脑", "笔记本和台式电脑", 1),
        (8, "相机", "数码相机和摄像设备", 1),
        (9, "男装", "男士服装", 2),
        (10, "女装", "女士服装", 2),
        (11, "儿童服装", "儿童服装和配饰", 2),
        (12, "客厅家具", "沙发、茶几等", 3),
        (13, "卧室家具", "床、衣柜等", 3),
        (14, "办公家具", "办公桌、椅子等", 3),
        (15, "零食", "各类零食和小吃", 4),
        (16, "饮料", "各类饮品", 4),
        (17, "小说", "各类小说", 5),
        (18, "教育", "教育和学习资料", 5),
        (19, "杂志", "各类杂志期刊", 5)
    ]
    
    cursor.executemany(
        "INSERT INTO categories (id, name, description, parent_id) VALUES (?, ?, ?, ?)",
        main_categories + sub_categories
    )
    
    print(f"已添加 {len(main_categories) + len(sub_categories)} 个产品分类")
    
    # 生成产品数据
    products = []
    product_names = [
        "iPhone 13", "华为 P40", "小米 12", "三星 Galaxy S22", "OPPO Find X5",
        "MacBook Pro", "联想 ThinkPad", "华硕 ZenBook", "戴尔 XPS", "微软 Surface",
        "佳能 EOS R5", "索尼 A7III", "富士 X-T4", "尼康 Z6", "GoPro Hero 10",
        "男士牛仔裤", "男士T恤", "男士夹克", "男士衬衫", "男士外套",
        "女士连衣裙", "女士牛仔裤", "女士T恤", "女士衬衫", "女士外套",
        "儿童T恤", "儿童裤子", "儿童连衣裙", "儿童外套", "婴儿连体衣",
        "三人沙发", "茶几", "电视柜", "角几", "沙发垫",
        "床垫", "衣柜", "床头柜", "梳妆台", "化妆镜",
        "办公桌", "办公椅", "会议桌", "文件柜", "书架",
        "薯片", "巧克力", "饼干", "坚果", "糖果",
        "可乐", "矿泉水", "果汁", "咖啡", "茶",
        "《活着》", "《三体》", "《百年孤独》", "《红楼梦》", "《战争与和平》",
        "《高等数学》", "《英语语法大全》", "《计算机科学导论》", "《物理学原理》", "《经济学原理》",
        "《时尚芭莎》", "《读者》", "《科学美国人》", "《国家地理》", "《经济学人》"
    ]
    
    product_descriptions = [f"{name}的详细描述，这是一个示例文本。" for name in product_names]
    product_prices = [random.uniform(10.0, 9999.9) for _ in range(len(product_names))]
    product_prices = [round(price, 2) for price in product_prices]
    
    # 将产品分配到适当的分类
    category_ids = []
    for i, name in enumerate(product_names):
        if i < 5:
            category_ids.append(6)  # 手机
        elif i < 10:
            category_ids.append(7)  # 电脑
        elif i < 15:
            category_ids.append(8)  # 相机
        elif i < 20:
            category_ids.append(9)  # 男装
        elif i < 25:
            category_ids.append(10)  # 女装
        elif i < 30:
            category_ids.append(11)  # 儿童服装
        elif i < 35:
            category_ids.append(12)  # 客厅家具
        elif i < 40:
            category_ids.append(13)  # 卧室家具
        elif i < 45:
            category_ids.append(14)  # 办公家具
        elif i < 50:
            category_ids.append(15)  # 零食
        elif i < 55:
            category_ids.append(16)  # 饮料
        elif i < 60:
            category_ids.append(17)  # 小说
        elif i < 65:
            category_ids.append(18)  # 教育
        else:
            category_ids.append(19)  # 杂志
    
    stocks = [random.randint(0, 1000) for _ in range(len(product_names))]
    created_dates = [(now - timedelta(days=random.randint(1, 500))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(len(product_names))]
    
    for i in range(len(product_names)):
        products.append((
            i+1,
            product_names[i],
            product_descriptions[i],
            product_prices[i],
            category_ids[i],
            stocks[i],
            created_dates[i]
        ))
    
    cursor.executemany(
        "INSERT INTO products (id, name, description, price, category_id, stock_quantity, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        products
    )
    
    print(f"已添加 {len(products)} 个产品数据")
    
    # 生成订单数据
    orders = []
    order_statuses = ["已下单", "已支付", "已发货", "已完成", "已取消"]
    
    for i in range(1, 101):  # 创建100个订单
        user_id = random.randint(1, 50)
        order_date = (now - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S')
        # 总金额暂时为0，后面会更新
        status = random.choice(order_statuses)
        
        orders.append((i, user_id, order_date, 0, status))
    
    cursor.executemany(
        "INSERT INTO orders (id, user_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
        orders
    )
    
    print("已创建 100 个订单")
    
    # 生成订单明细数据
    order_items = []
    item_id = 1
    
    # 更新订单总金额
    for order_id in range(1, 101):
        # 每个订单有1-5个商品
        num_items = random.randint(1, 5)
        order_total = 0
        
        for _ in range(num_items):
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 5)
            price_per_unit = products[product_id-1][3]  # 获取产品价格
            
            order_items.append((item_id, order_id, product_id, quantity, price_per_unit))
            item_id += 1
            
            order_total += quantity * price_per_unit
        
        # 更新订单总金额
        cursor.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (round(order_total, 2), order_id))
    
    cursor.executemany(
        "INSERT INTO order_items (id, order_id, product_id, quantity, price_per_unit) VALUES (?, ?, ?, ?, ?)",
        order_items
    )
    
    print(f"已添加 {len(order_items)} 条订单明细")
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    print(f"测试数据库创建完成: {db_path}")
    return db_path

if __name__ == "__main__":
    db_path = create_test_database()
    print(f"测试数据库已生成在: {os.path.abspath(db_path)}")
    print("现在您可以在数据库查看器中打开这个数据库文件进行测试。")
