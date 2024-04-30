table_info_prompt = """
### 1. book_info (书籍信息)
- book_id: int
- book_name: varchar(255)
- author_country: varchar(255)
- book_period: varchar(32)
- book_type: varchar(255)
- book_content_theme: varchar(255)
- readability_range: varchar(255)
- word_count: varchar(255)
- mainly_affects_character: varchar(255)
- special_attention: varchar(255)

### 2. emotion (情感)
- method: varchar(255)
- id: int (自增)

### 3. learn (学习)
- method: varchar(255)
- id: int (自增)

### 4. like_books (喜欢的书籍)
- like_id: int (自增)
- student_id: int
- book_id: int

### 5. message (消息)
- message_id: int (自增)
- student_id1: int
- student_id2: int
- content: varchar(255)
- direction: enum('0','1')

### 6. psychology (心理)
- method: varchar(255)
- id: int (自增)

### 7. social (社交)
- method: varchar(255)
- id: int (自增)

### 8. stu_character (学生性格)
- method: varchar(255)
- id: int (自增)

### 9. student (学生)
- student_id: int
- student_name: varchar(255)
- （与此相关的还有许多关于学生信息和喜好的字段）

### 10. student_score (学生分数)
- student_id: int
- psychology: bigint unsigned
- social: bigint unsigned
- stu_character: bigint unsigned
- learn: bigint unsigned
- emotion: bigint unsigned

### 11. student_statistics (学生统计)
- （与 student_score 类似，包含对应的 int 字段）

### 12. word_cloud (词云)
- （未提供字段信息）
"""

characters = """
树立明确的价值观：确定自己的核心价值观，建立积极的品德准则，指导行为和决策。
参与志愿活动：参与公益或志愿服务，培养责任感和同理心，发展品德和社会责任感。
责任担当： 承担学业责任，及时完成任务，培养对事情负责的态度。
尊重他人： 尊重同学和老师，学会倾听和理解，建立良好人际关系。
守时习惯： 养成守时习惯，提高时间管理能力，培养责任感。
团队协作： 参与团队项目，学会合作与分享，培养集体荣誉感。
友善待人： 保持友善态度，用温暖言行影响身边的同学。
自律训练： 培养自律，控制冲动，提高自我管理能力。
乐观心态： 培养积极的生活态度，面对困难保持乐观。
反思自省： 定期反思个人行为，找到改进之处，不断提升品格素养。
"""