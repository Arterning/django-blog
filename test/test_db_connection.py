"""
数据库连接诊断脚本
用于排查PostgreSQL连接问题
"""
import os
import sys
from pathlib import Path

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

print("=" * 60)
print("PostgreSQL连接诊断")
print("=" * 60)

# 1. 检查.env文件
print("\n1. 检查.env文件...")
env_file = BASE_DIR / '.env'
if env_file.exists():
    print(f"   ✓ .env文件存在: {env_file}")
    print(f"   文件编码检测...")

    # 读取文件内容并检测编码
    with open(env_file, 'rb') as f:
        raw_data = f.read()
        print(f"   文件大小: {len(raw_data)} bytes")

        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                content = raw_data.decode(encoding)
                print(f"   ✓ 成功使用 {encoding} 编码读取")
                if encoding == 'utf-8':
                    break
            except UnicodeDecodeError as e:
                print(f"   ✗ {encoding} 解码失败: {e}")
else:
    print(f"   ✗ .env文件不存在: {env_file}")
    sys.exit(1)

# 2. 加载环境变量
print("\n2. 加载环境变量...")
from dotenv import load_dotenv
load_dotenv(env_file, encoding='utf-8')

# 3. 读取数据库配置
print("\n3. 读取数据库配置...")
db_config = {
    'NAME': os.getenv('DB_NAME', 'NOT_SET'),
    'USER': os.getenv('DB_USER', 'NOT_SET'),
    'PASSWORD': os.getenv('DB_PASSWORD', 'NOT_SET'),
    'HOST': os.getenv('DB_HOST', 'NOT_SET'),
    'PORT': os.getenv('DB_PORT', 'NOT_SET'),
}

for key, value in db_config.items():
    if key == 'PASSWORD':
        # 隐藏密码，只显示长度
        print(f"   {key}: {'*' * len(value) if value != 'NOT_SET' else 'NOT_SET'} (长度: {len(value)})")
        # 检查密码编码
        if value != 'NOT_SET':
            try:
                value.encode('utf-8')
                print(f"      ✓ 密码UTF-8编码正常")
            except UnicodeEncodeError as e:
                print(f"      ✗ 密码编码错误: {e}")
    else:
        print(f"   {key}: {value}")

# 4. 测试psycopg2连接
print("\n4. 测试psycopg2直接连接...")
try:
    import psycopg2

    # 构建连接参数
    conn_params = {
        'dbname': db_config['NAME'],
        'user': db_config['USER'],
        'password': db_config['PASSWORD'],
        'host': db_config['HOST'],
        'port': db_config['PORT'],
        'client_encoding': 'UTF8',
    }

    print(f"   连接参数: dbname={conn_params['dbname']}, user={conn_params['user']}, host={conn_params['host']}, port={conn_params['port']}")

    conn = psycopg2.connect(**conn_params)
    print("   ✓ psycopg2连接成功!")

    # 测试查询
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL版本: {version[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   ✗ psycopg2连接失败: {e}")
    print(f"   错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试Django数据库连接
print("\n5. 测试Django数据库连接...")
try:
    import django
    django.setup()

    from django.db import connection

    # 测试连接
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"   ✓ Django数据库连接成功! 测试查询结果: {result}")

except Exception as e:
    print(f"   ✗ Django数据库连接失败: {e}")
    print(f"   错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 所有测试通过! 数据库配置正确。")
print("=" * 60)
