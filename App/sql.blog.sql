-- 创建用户表
DROP TABLE IF EXISTS User;
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    Username VARCHAR(255) NOT NULL COMMENT '用户名',
    Email VARCHAR(255) NOT NULL COMMENT '邮箱',
    Password VARCHAR(255) NOT NULL COMMENT '密码',
    RegistrationTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    Avatar VARCHAR(255) COMMENT '头像',
    Bio TEXT COMMENT '个人简介'
    -- 其他用户信息字段，根据需要添加
);

-- 创建博客表
DROP TABLE IF EXISTS Blog;
CREATE TABLE Blog (
    BlogID INT PRIMARY KEY AUTO_INCREMENT COMMENT '博客ID',
    AuthorID INT COMMENT '作者ID',
    Title VARCHAR(255) NOT NULL COMMENT '标题',
    Content TEXT NOT NULL COMMENT '内容',
    PublishTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    LikesCount INT DEFAULT 0 COMMENT '点赞数',
    FOREIGN KEY (AuthorID) REFERENCES User(UserID)
    -- 其他博客信息字段，根据需要添加
);

-- 创建评论表
DROP TABLE IF EXISTS Comment;
CREATE TABLE Comment (
    CommentID INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID',
    BlogID INT COMMENT '博客ID',
    CommenterID INT COMMENT '评论者ID',
    Content TEXT NOT NULL COMMENT '评论内容',
    CommentTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
    FOREIGN KEY (BlogID) REFERENCES Blog(BlogID),
    FOREIGN KEY (CommenterID) REFERENCES User(UserID)
    -- 其他评论信息字段，根据需要添加
);

-- 创建关注表
DROP TABLE IF EXISTS Follow;
CREATE TABLE Follow (
    FollowID INT PRIMARY KEY AUTO_INCREMENT COMMENT '关注ID',
    FollowerID INT COMMENT '关注者ID',
    FollowingID INT COMMENT '被关注者ID',
    FOREIGN KEY (FollowerID) REFERENCES User(UserID),
    FOREIGN KEY (FollowingID) REFERENCES User(UserID)
);


-- 创建点赞表
DROP TABLE IF EXISTS Upvote;
CREATE TABLE Upvote (
    LikeID INT PRIMARY KEY COMMENT '点赞ID',
    UserID INT COMMENT '用户ID',
    BlogID INT COMMENT '博客ID',
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (BlogID) REFERENCES Blog(BlogID)
);

-- -- 创建消息表
-- DROP TABLE IF EXISTS Message;
-- CREATE TABLE Message (
--     MessageID INT PRIMARY KEY COMMENT '消息ID',
--     SenderID INT COMMENT '发送者ID',
--     RecipientID INT COMMENT '接收者ID',
--     Content TEXT NOT NULL COMMENT '消息内容',
--     SendTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
--     IsRead BOOLEAN DEFAULT FALSE COMMENT '是否已读',
--     FOREIGN KEY (SenderID) REFERENCES User(UserID),
--     FOREIGN KEY (RecipientID) REFERENCES User(UserID)
-- );
