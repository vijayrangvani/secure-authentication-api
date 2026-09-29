import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta,timezone
import jwt

load_dotenv()

def hash_password(password:str)->str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes,salt)
    return hashed_password.decode("utf-8")

def verify_password(password:str,hashed_password:str)->bool:
    password_bytes = password.encode("utf-8")
    hash_password_bytes=hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes,hash_password_bytes)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(user_id:int,username:str,role:str):
    payload={
        "sub":str(user_id),
        "username":username,
        "role":role,
        "exp":datetime.now(timezone.utc)+timedelta(minutes=30)
    }
    token = jwt.encode(
        payload,SECRET_KEY,algorithm = ALGORITHM)
    return token

def decode_access_token(token:str):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=ALGORITHM
    )

def create_refresh_token(username:str):
    payload={
        "sub":username,
        "token_type":"refresh",
        "exp":datetime.now(timezone.utc)+timedelta(days=7)
    }
    token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return token

if __name__=="__main__":
    token = create_access_token(user_id=1,username="vijay",role="user")
    print(token)
    payload = decode_access_token(token)
    print(payload)