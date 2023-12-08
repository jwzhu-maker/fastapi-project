import datetime

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
security = HTTPBasic()

# Below key is for algo: "HS256"
# Secret key for JWT signing (replace with your own secret key)
SECRET_KEY = "your_secret_key_HS256"

# Below key and code is for algo: "RS256"
# Load the private key for signing JWT tokens
# with open("privateKey_20230817T103151798Z.pem", "rb") as key_file:
#     PRIVATE_KEY = key_file.read()
#
# # Load the public key for verifying JWT tokens
# with open("publicKey_20230817T103151798Z.pem", "rb") as key_file:
#     PUBLIC_KEY = key_file.read()


# Configure CORS
origins = ["*"]  # Update with your client's origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2PasswordBearer is a class that helps in extracting the JWT token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Mock user database (replace with your actual user authentication logic)
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "1",
    },
    "user2": {
        "username": "user2",
        "password": "2",
    },
}


def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    # Check username and password against your database or authentication system
    if (
        credentials.username.strip().lower() in fake_users_db
        and credentials.password
        == fake_users_db[credentials.username.strip().lower()]["password"]
    ):
        return credentials.username
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/v2/face/oauth/token")
def oauth_token(body: dict, username: str = Depends(verify_user)):
    payload = {
        # "aud": "UOB",
        "iss": "BIO",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "sub": username,
    }  # You can customize the payload as needed
    # Below code is for algo "HS256"
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Below code is for alog "RS256"
    # jwt_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    return {
        "access_token": jwt_token,
        "expires_in": 60 * 60 * 2,
        "token_type": "bearer",
    }


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # Below code is for algo "HS256"
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Below code is for alog "RS256"
        # payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])

        username: str = payload.get("sub")
        if username is None:
            # raise HTTPException(status_code=401, detail="Invalid token")
            return None

        # Check if the token is expired
        expiration_timestamp = payload.get("exp")
        if (
            expiration_timestamp is None
            or datetime.datetime.utcnow()
            > datetime.datetime.fromtimestamp(expiration_timestamp)
        ):
            # raise HTTPException(status_code=401, detail="Token has expired")
            return None

        # Validate the audience (aud) claim
        # audience = payload.get("aud")
        # if audience != "UOB":  # Replace with your expected audience
        #     raise HTTPException(status_code=401, detail="Invalid audience")

        return username
    except jwt.DecodeError:
        # raise HTTPException(
        #     status_code=401, detail="Token signature verification failed"
        # )
        return None


@app.post("/api/v2/face/verify/token")
def verify_token_endpoint(username: str = Depends(verify_token)):
    # Here, you can perform additional checks if needed
    # For example, checking if the username exists in your user database
    if username.strip().lower() not in fake_users_db:
        # raise HTTPException(status_code=401, detail="Invalid username")
        return {"isValid": False}
    return {"isValid": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
