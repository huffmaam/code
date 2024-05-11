import random
import string
from faker import Faker
from sqlalchemy import create_engine, text

fake = Faker('zh_CN')  # 使用中文配置

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# def random_chinese_sentence(min, max):
#     sentence_length = random.randint(min, max)
#     return ''.join(random.choice(characters) for _ in range(sentence_length))


def random_int(min, max):
    return random.randint(min, max)


# 读取中文文本文件
with open("荷塘月色.txt", "r", encoding="utf-8") as file:
    characters = file.read()

# 创建数据库引擎
engine = create_engine('mysql+pymysql://root:abc123@localhost/social_blog')

# 连接到数据库
connection = engine.connect()



users = []
for i in range(100):  # 创建100个用户
    username = fake.name()

    # 随机选择一个域名
    domain_choices = ['qq.com', 'gmail.com', '163.com']
    selected_domain = random.choice(domain_choices)
    email = fake.email(domain=selected_domain)

    password = random_string(10)

    avatar = 'imgs/avatar/avatar' + str(random_int(1, 6)) + '.jpg'
    bio = fake.paragraph(15)
    users.append((username, email, password, avatar, bio))

# 插入用户数据
for user in users:
    connection.execute(text("""
        INSERT INTO User ( Username, Email, Password, Avatar, Bio)
        VALUES (:username, :email, :password, :avatar, :bio)
    """), username=user[0], email=user[1], password=user[2], avatar=user[3], bio=user[4])

blogs = []
for i in range(200):  # 创建200篇博客
    author_id = random_int(1, 100)
    title = fake.sentence()
    content = fake.paragraph(random_int(10, 40))
    likes_count = random_int(0, 1000)
    blogs.append((author_id, title, content, likes_count))

# 插入博客数据
for blog in blogs:
    connection.execute(text("""
        INSERT INTO Blog (AuthorID, Title, Content, LikesCount)
        VALUES (:author_id, :title, :content, :likes_count)
    """), author_id=blog[0], title=blog[1], content=blog[2], likes_count=blog[3])

# 生成评论数据
comments = []
for i in range(2000):  # 创建2000条评论
    blog_id = random_int(1, 200)
    user_id = random_int(1, 100)
    content = fake.paragraph(random_int(1,10))
    comments.append((blog_id, user_id, content))

# 插入评论数据
for comment in comments:
    connection.execute(text("""
        INSERT INTO Comment (BlogID, CommenterID, Content)
        VALUES (:blog_id, :user_id, :content)
    """), blog_id=comment[0], user_id=comment[1], content=comment[2])

# 生成关注表
follows = []
for i in range(2000):  # 创建2000条关注关系
    follower_id = random_int(1, 100)
    following_id = random_int(1, 100)
    follows.append((follower_id, following_id))

# 插入评论数据
for follow in follows:
    connection.execute(text("""
        INSERT INTO Follow (FollowerId, FollowingId)
        VALUES (:follower_id, :following_id)
    """), follower_id=follow[0], following_id=follow[1])

upvotes = []
for i in range(2000):  # 创建2000条点赞信息
    user_id = random_int(1, 100)
    blog_id = random_int(1, 200)
    upvotes.append((user_id, blog_id))

# 插入点赞信息
for upvote in upvotes:
    connection.execute(text("""
        INSERT INTO Upvote (UserID, BlogID)
        VALUES (:user_id, :blog_id)
    """), user_id=upvote[0], blog_id=upvote[1])
