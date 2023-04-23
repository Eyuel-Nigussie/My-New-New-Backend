from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm #instead of retriving user credential passing in the body, we gonna use this, a built in utility 
from sqlalchemy.orm import Session  
from .. import database, schemas, models, utils, oauth2
router = APIRouter(tags=['Authentication'])

#you can replace /login with your own if you want to access
#also to retrieve user_credentials: )Auth2PasswordRequestForm is built in method instead of using
#user_credentials = schemas.UserLogin
@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    #but oauth2 only returns username and password
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='User not found')
    # if not user.check_password(user_credentials.password):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect password')
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
 #we are putting user id on the payload  
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", 'user': user}
    # access_token = user.generate_access_token()

