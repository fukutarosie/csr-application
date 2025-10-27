from src.entity import User

res = User.create_user('admin5', 'SomePass123', 'gwen-dup@gmail.com', 'Gwen Duplicate', 1)
print('Result:', res)
