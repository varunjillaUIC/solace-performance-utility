# from fastapi import APIRouter
# from pydantic import BaseModel
# import json, os

# router = APIRouter(prefix="/api")

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROFILES_FILE = os.path.join(BASE_DIR, "../../data/profiles.json")


# class Profile(BaseModel):
#     name: str
#     host: str
#     vpn: str
#     username: str
#     password: str


# def load():
#     if not os.path.exists(PROFILES_FILE):
#         return []
#     try:
#         with open(PROFILES_FILE) as f:
#             content = f.read().strip()
#             return json.loads(content) if content else []
#     except (json.JSONDecodeError, IOError):
#         return []


# def save(profiles):
#     os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
#     with open(PROFILES_FILE, "w") as f:
#         json.dump(profiles, f, indent=2)


# @router.get("/profiles")
# def get_profiles():
#     return load()


# @router.post("/profiles")
# def add_profile(profile: Profile):
#     profiles = [p for p in load() if p["name"] != profile.name]
#     profiles.append(profile.dict())
#     save(profiles)
#     return {"status": "saved"}


# @router.delete("/profiles/{name}")
# def delete_profile(name: str):
#     save([p for p in load() if p["name"] != name])
#     return {"status": "deleted"}


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import json, os

router = APIRouter(prefix="/api")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_FILE = os.path.join(BASE_DIR, "../../data/profiles.json")


class Profile(BaseModel):
    name: str
    host: str
    vpn: str
    username: str
    password: str

    @field_validator("name", "host")
    @classmethod
    def not_blank(cls, v: str, info):
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()


def load():
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE) as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except (json.JSONDecodeError, IOError):
        return []


def save(profiles):
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


@router.get("/profiles")
def get_profiles():
    return load()


@router.post("/profiles")
def add_profile(profile: Profile):
    profiles = [p for p in load() if p["name"] != profile.name]
    profiles.append(profile.dict())
    save(profiles)
    return {"status": "saved"}


@router.delete("/profiles/{name}")
def delete_profile(name: str):
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Profile name cannot be empty")
    remaining = [p for p in load() if p["name"] != name]
    save(remaining)
    return {"status": "deleted"}