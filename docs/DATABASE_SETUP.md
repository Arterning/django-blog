# 数据库配置指南

## 问题说明

如果你遇到了 `UnicodeDecodeError: 'utf-8' codec can't decode byte` 错误，这通常是因为PostgreSQL密码包含特殊字符导致的编码问题。

## 解决方案

### 方案1：使用环境变量配置（推荐）

#### 步骤1：创建 .env 文件

在项目根目录创建 `.env` 文件（与manage.py同级）：

```bash
# Windows PowerShell
New-Item -Path .env -ItemType File

# 或者直接在文件资源管理器中创建
```

#### 步骤2：编辑 .env 文件

复制以下内容到 `.env` 文件，并修改为你的实际配置：

```env
# PostgreSQL数据库配置
DB_NAME=django_blog
DB_USER=postgres
DB_PASSWORD=你的密码
DB_HOST=localhost
DB_PORT=5432
```

**重要提示**：
- ⚠️ 密码中如果有特殊字符（如中文、特殊符号），建议修改PostgreSQL密码为纯英文+数字
- ⚠️ `.env` 文件已在 `.gitignore` 中，不会被git提交

#### 步骤3：验证配置

运行以下命令测试数据库连接：

```bash
uv run python manage.py check --database default
```

### 方案2：重置PostgreSQL密码（推荐用于解决编码问题）

#### 步骤1：连接到PostgreSQL

```bash
# 使用psql连接
psql -U postgres
```

#### 步骤2：修改密码为纯英文

```sql
-- 修改postgres用户密码（使用纯英文+数字）
ALTER USER postgres WITH PASSWORD 'MyNewPassword123';

-- 退出
\q
```

#### 步骤3：更新 .env 文件

```env
DB_PASSWORD=MyNewPassword123
```

### 方案3：创建新的数据库用户（最佳实践）

#### 步骤1：创建专用数据库和用户

```bash
# 连接到PostgreSQL
psql -U postgres
```

```sql
-- 创建新用户（使用简单密码）
CREATE USER django_user WITH PASSWORD 'django123456';

-- 创建数据库
CREATE DATABASE django_blog OWNER django_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE django_blog TO django_user;

-- 退出
\q
```

#### 步骤2：更新 .env 文件

```env
DB_NAME=django_blog
DB_USER=django_user
DB_PASSWORD=django123456
DB_HOST=localhost
DB_PORT=5432
```

## 完整配置步骤

### 1. 确保PostgreSQL正在运行

```bash
# Windows - 检查PostgreSQL服务状态
# 打开"服务"应用，查找PostgreSQL服务

# 或使用命令
sc query postgresql-x64-14  # 版本号可能不同
```

### 2. 测试数据库连接

```bash
# 使用psql测试连接
psql -U postgres -h localhost -p 5432

# 如果能成功连接，说明PostgreSQL运行正常
```

### 3. 创建 .env 文件

参考上面的方案1或方案3。

### 4. 运行数据库迁移

```bash
# 应用迁移
uv run python manage.py migrate

# 如果遇到错误，检查：
# 1. PostgreSQL是否正在运行
# 2. .env文件中的密码是否正确
# 3. 数据库是否已创建
```

### 5. 创建超级用户

```bash
uv run python manage.py createsuperuser
```

## 常见问题排查

### 问题1: 连接被拒绝 (Connection refused)

**原因**: PostgreSQL服务未启动

**解决**:
```bash
# Windows: 启动PostgreSQL服务
net start postgresql-x64-14  # 版本号根据实际情况修改
```

### 问题2: 密码认证失败 (password authentication failed)

**原因**: 密码错误

**解决**:
1. 检查 `.env` 文件中的密码是否正确
2. 尝试使用psql手动连接验证密码
3. 必要时重置密码（参考方案2）

### 问题3: 数据库不存在 (database does not exist)

**原因**: 数据库未创建

**解决**:
```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE django_blog;

-- 退出
\q
```

### 问题4: UnicodeDecodeError

**原因**: 密码包含特殊字符

**解决**:
- 使用方案2或方案3，设置纯英文+数字的密码

## 验证配置是否成功

运行以下命令，如果没有错误则配置成功：

```bash
# 检查数据库连接
uv run python manage.py check --database default

# 查看数据库表
uv run python manage.py dbshell
\dt
\q

# 应用迁移
uv run python manage.py migrate
```

## 配置文件位置

- 环境变量文件: `.env` (项目根目录)
- Django配置文件: `mysite/settings.py`
- 模板文件: `.env.template`

## 安全提示

1. ⚠️ 不要将 `.env` 文件提交到git仓库
2. ⚠️ 生产环境使用强密码
3. ⚠️ 定期更换数据库密码
4. ⚠️ 使用专用数据库用户，而不是postgres超级用户

## 需要帮助？

如果按照以上步骤仍然遇到问题，请提供以下信息：

1. PostgreSQL版本: `psql --version`
2. 错误信息完整截图
3. .env文件内容（隐藏密码）
4. 是否能用psql连接数据库
