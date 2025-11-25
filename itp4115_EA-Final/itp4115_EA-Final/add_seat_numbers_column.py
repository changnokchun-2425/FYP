"""
直接添加 seat_numbers 列到 ticket 表
使用方法: python add_seat_numbers_column.py
"""
import sqlite3
import os
import sys

# 獲取數據庫路徑
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'app.db')

print(f"腳本目錄: {script_dir}")
print(f"數據庫路徑: {db_path}")
print(f"數據庫存在: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("\n✗ 錯誤: 找不到數據庫文件 app.db")
    sys.exit(1)

# 連接到數據庫
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 首先列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n數據庫中的所有表: {[t[0] for t in tables]}")
    
    # 檢查 ticket 表是否存在
    if not any(t[0] == 'ticket' for t in tables):
        print("\n✗ 錯誤: ticket 表不存在")
        print("請先運行數據庫遷移創建表:")
        print("  flask --app run.py db upgrade")
        sys.exit(1)
    
    # 檢查列是否已存在
    cursor.execute("PRAGMA table_info(ticket)")
    columns_info = cursor.fetchall()
    columns = [column[1] for column in columns_info]
    
    print(f"\n當前 ticket 表的列: {columns}")
    
    if 'seat_numbers' in columns:
        print("\n✓ seat_numbers 列已存在於 ticket 表中")
    else:
        # 添加列
        print("\n正在添加 seat_numbers 列...")
        cursor.execute("ALTER TABLE ticket ADD COLUMN seat_numbers VARCHAR(256)")
        conn.commit()
        print("✓ 成功添加 seat_numbers 列到 ticket 表")
        
        # 驗證添加成功
        cursor.execute("PRAGMA table_info(ticket)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"更新後的列: {new_columns}")
    
except Exception as e:
    print(f"\n✗ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()

print("\n完成!")
