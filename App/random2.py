import random

from faker import Faker


fake = Faker('zh_CN')  # 使用中文配置
chinese_sentence = fake.sentence()
chinese_paragraph = fake.paragraph(30)

# 随机选择一个域名
domain_choices = ['qq.com', 'gmail.com', '163.com']
selected_domain = random.choice(domain_choices)

print(fake.name())
print(fake.email(domain=selected_domain))
print(chinese_sentence)
print(chinese_paragraph)
print(len(chinese_paragraph))
print(fake.image_url(width=None, height=None))
print('--------')
# 生成包含 5 个段落的文本，每个段落包含 5 句话
# paragraphs = fake.paragraphs(
#     nb=5,
#     ext_word_list=None,
#     variable_nb_sentences=True,
#     nb_sentences=5,
#     ext_sentences_list=None)
#
# for paragraph in paragraphs:
#     print(paragraph)

# print(fake.text(nb_sentences=5))