from fastapi import FastAPI,Depends,HTTPException
from database import engine,Base,get_db
from models import User
from schemas import UserCreate,UserLogin,UserResponse,UserUpdate,PasswordUpdate,RefreshTokenRequest
from sqlalchemy.orm import Session
from security import hash_password,verify_password,create_access_token,decode_access_token,create_refresh_token, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError

app = FastAPI(
        title = "Secure Authentication API")

Base.metadata.create_all(bind=engine)

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user(token:str=Depends(oauth2_schema)):
    payload = decode_access_token(token)
    return payload

@app.get("/")
def home():
    return {
        "msg":"Secure Authentication API is running"
    }

@app.get("/db-test")
def database_test():
    try:
        with engine.connect():
            return {
                "msg":"Database Connection Successful"
            }
    except Exception as e:
        return {
            "msg":"Database connection Error",
            "error":str(e)
        }

@app.post("/register")
def register(
    user:UserCreate,
    db:Session =Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        return{
           "msg":"Username Already exists.."
        }
    password_hash = hash_password(user.password)
    new_user = User(
        username = user.username,
        password_hash = password_hash,
        role = "user"
    )
    db.add(new_user)
    db.commit()
    return {
        "message":"User Registration Successful",
        "UserName":new_user.username,
        "role":new_user.role
    }

@app.post("/login")
def login(user:UserLogin,db:Session=Depends(get_db)):
    user_db = db.query(User).filter(User.username==user.username).first()
    if not user_db:
        return {
            "message":"Invalid UserName or password"
        }
    if not verify_password(user.password,user_db.password_hash):
        return {
            "message":"Invalid UserName or password"
        }
    access_token = create_access_token(user_db.id,user_db.username,user_db.role)
    refresh_token = create_refresh_token(user_db.username)
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,  
        "token_type":"Bearer"
    }

@app.post("/token")
def token(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user_db = db.query(User).filter(form_data.username == User.username).first()
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or Password"
        )
    if not verify_password(form_data.password,user_db.password_hash):
        raise HTTPException(
            status=401,
            detail="Invalid Username or Password"
        )
    access_token = create_access_token(user_db.id,user_db.username,user_db.role)
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

@app.post("/refresh")
def refresh_token(request:RefreshTokenRequest,db:Session=Depends(get_db)):
     try:
          payload = jwt.decode(request.refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
          if payload.get("token_type") != "refresh":
               raise HTTPException(
                    status_code=404,
                    detail="Invalid refresh Token"
               )
          username =payload.get("sub")
          user_db = db.query(User).filter(User.username == username).first()
          if not user_db:
               raise HTTPException(
                    status_code=404,
                    detail="User not found"
               )
          access_token=create_access_token(user_db.id,user_db.username,user_db.role)
          return {
               "acces_token":access_token,
               "token_type":"Bearer"
          }

     except JWTError:
          raise HTTPException(
               status_code=401,
               detail="Invalid or expired refresh token")

@app.get("/protected")
def protected(current_user = Depends(get_current_user)):
    return {
        "Msg":"You are authorized",
        "Username":current_user
    }

def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code = 401,
            detail = "Admin access required"
        )
    return current_user


@app.get("/admin")
def admin_area(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=401,
            detail = "Admin access required"
        )
    return current_user

@app.get("/users",response_model=list[UserResponse])
def get_users(username:str | None = None,current_user=Depends(require_admin),db:Session=Depends(get_db)):
    if username:
        return db.query(User).filter(User.username == username)
    return db.query(User).all()

@app.get("/users/{id}",response_model=UserResponse)
def user_by_id(id:int,current_user=Depends(require_admin),db:Session=Depends(get_db)):
               user =  db.query(User).filter(User.id==id).first()
               if not user:
                    raise HTTPException(
                         status_code=404,
                         detail="User not found"
                    )

               return user


# @app.patch("/user-update/{id}",response_model=UserResponse)
# def user_update(id:int,user_update:UserUpdate,current_user=Depends(require_admin),db:Session=Depends(get_db)):
#      user = db.query(User).filter(User.id==id).first()
#      if not user:
#           raise HTTPException(
#                status_code=404,
#                detail="User not found"
#           )
#      user.role = user_update.role
#      db.commit()
#      return user

@app.delete("/user-delete/{id}")
def user_delete(id:int,current_user=Depends(require_admin),db:Session=Depends(get_db)):

     result = db.query(User).filter(User.id == id).delete()
     if not result:
          raise HTTPException(
               status_code=404,
               detail="User not found"
          )
     db.commit()
     return f"User with id{id} is deleted successfully"

@app.patch("/password-update/",response_model=UserResponse)
def password_update(user_password:PasswordUpdate,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
     user = db.query(User).filter(current_user["sub"] == User.id).first()
     user.password_hash = hash_password(user_password.password)
     db.commit()
     return user 

@app.get("/search-users",response_model=list[UserResponse])
def get_users(id:int | None = None,current_user=Depends(require_admin),db:Session=Depends(get_db)):
     if not id:
          user = db.query(User).all()
          return user
     user = db.query(User).filter(User.id == id).first()
     if not user:
          raise HTTPException(
               status_code=404,
               detail="User Not found"
          )
     return [user]

@app.patch("/update-role/{id}",response_model=UserResponse)
def change_role(id:int,new_role:UserUpdate,current_user=Depends(require_admin),db:Session=Depends(get_db)):
     user = db.query(User).filter(User.id==id).first()
     if not user:
          raise HTTPException(
               status_code=404,
               detail="User Not Found"
          )
     user.role=new_role.role
     db.commit()
     return user
