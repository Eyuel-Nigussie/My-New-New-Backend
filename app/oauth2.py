from fastapi import Depends, status, HTTPException
#jose to generate and validate JWT token
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi.security import OAuth2PasswordBearer

#endpoint of login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "2ks9knskj20jslj18vansd023jlkasddkcksl"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 


#data param is used to putting data into payload
def create_access_token(data: dict): 
  to_encode = data.copy() #make copy to manupilate few things of data passed
  expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire}) #adde expiration field

  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #encode

  return encoded_jwt



def verify_access_token(token: str, credentials_exception):
    try:    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #extract the data by user id we put on the payload & store on id of type id
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data



#take token, extract id,veify token is correct,  then maybe automatically fetch user from db 
# and then add it as param in our path op function    
def get_current_user(token: str =  Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)