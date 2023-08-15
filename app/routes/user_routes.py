from flask import Blueprint, request, jsonify
from app import user_collection
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import hashlib

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/signup", methods=["POST"])
def sign_up():
    new_user = request.get_json()
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()

    user = user_collection.find_one({"username": new_user["username"]})
    if not user:
        user_collection.insert_one(new_user)
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": "Username already exists"}), 409

@user_bp.route("/login", methods=["POST"])
def log_in():
    login_details = request.get_json()
    user_from_db = user_collection.find_one({'username': login_details['username']})

    if user_from_db:
        encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrypted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            return jsonify(access_token=access_token), 200

    return jsonify({"message": "The username or password is incorrect"}), 401

@user_bp.route("/account", methods=["GET"])
@jwt_required()
def view_account():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if user_from_db:
        user_from_db.pop('_id')
        user_from_db.pop('password')
        return jsonify(user_from_db), 200
    else:
        return jsonify({"message": "User not found"}), 404

@user_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if user_from_db:
        user_collection.delete_one({'username': current_user})
        return jsonify({"message": "Account deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
@user_bp.route("/changepassword", methods=["POST"])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if not user_from_db:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    old_password_hash = hashlib.sha256(old_password.encode("utf-8")).hexdigest()
    if old_password_hash != user_from_db['password']:
        return jsonify({"message": "Invalid old password"}), 401

    new_password_hash = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
    user_collection.update_one({'username': current_user}, {"$set": {"password": new_password_hash}})
    
    return jsonify({"message": "Password updated successfully"}), 200

@user_bp.route("/favorites", methods=["POST"])
@jwt_required()
def add_favorite_pet():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if user_from_db:
        data = request.get_json()
        pet_id = data.get("pet_id")

        favorite_pets = user_from_db.get("favorite_pets", [])  

        if pet_id not in favorite_pets:
            user_collection.update_one({'username': current_user}, {"$push": {"favorite_pets": pet_id}})
            return jsonify({"message": "Pet added to favorites"}), 200
        else:
            return jsonify({"message": "Pet already in favorites"}), 409

    return jsonify({"message": "User not found"}), 404

@user_bp.route("/favorites", methods=["GET"])
@jwt_required()
def view_all_favorite_pets():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if user_from_db:
        favorite_pets = user_from_db["favorite_pets"]
        return jsonify({"favorite_pets": favorite_pets}), 200
    else:
        return jsonify({"message": 'User not found'}), 404

@user_bp.route("/favorites", methods=["DELETE"])
@jwt_required()
def delete_favorite_pet():
    current_user = get_jwt_identity()
    user_from_db = user_collection.find_one({'username': current_user})

    if user_from_db:
        data = request.get_json()
        pet_id = data.get("pet_id")

        if pet_id in user_from_db["favorite_pets"]:
            user_collection.update_one({'username': current_user}, {"$pull": {"favorite_pets": pet_id}})
            return jsonify({"message": "Pet removed from favorites"}), 200
        else:
            return jsonify({"message": "Pet not found in favorites"}), 404

    return jsonify({"message": "User not found"}), 404


    
