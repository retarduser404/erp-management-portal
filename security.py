from werkzeug.security import generate_password_hash, check_password_hash

# Hash a password
def hash_password(password):
    return generate_password_hash(password)

# Check a password
def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)

# TODO: Implement two-factor authentication logic here

