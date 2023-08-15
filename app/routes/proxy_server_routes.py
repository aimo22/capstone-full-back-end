from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
import requests
import html

load_dotenv()

proxy_bp = Blueprint("proxy_bp", __name__)

rescue_key = os.environ.get("RESCUE_KEY") 

@proxy_bp.route("/search", methods =["GET"])
def get_pets():
    postalcode_query = request.args.get("postalcode_query")
    miles_query = request.args.get("miles_query")
    if not postalcode_query and not miles_query:
        return {"message": " must provide a postal code and radius (miles)"}
    elif not postalcode_query:
        return {"message": " must provide a postal code"}
    elif not miles_query:
        return {"message": " must provide a radius (miles)"}
    
    body = {
        "data": {
            "filterRadius":
            {
                "miles": miles_query,
                "postalcode": postalcode_query
            }
        }
    }

    response = requests.get(
        "https://api.rescuegroups.org/v5/public/animals/search/available/haspic",
        params={"limit": 250},
        headers={"Authorization": rescue_key, "Content-Type":"application/vnd.api+json"},
        json=body
    )

    data = response.json().get("data")
    simplified_pets = []

    for pet in data:
        attributes = pet.get("attributes")
        id = pet.get("id")
        name = attributes.get("name", "")
        age = attributes.get("ageString", "")
        age_group = attributes.get("ageGroup", "")
        picture = attributes.get("pictureThumbnailUrl", "")
        url = attributes.get("url", "")
        sex = attributes.get("sex","")

        species_id = pet.get("relationships").get("species").get("data")[0].get("id")
        if species_id == "3":
            species = "Cat"
        elif species_id == "8":
            species = "Dog"
        else:
            species = "Other"
        if age == "":
            display_age = age_group
        else:
            display_age = age
        querywords = name.split()
        if name == "" or sex == "" or picture == "" or url == "" or age_group == "" or len(querywords) > 3:
            continue  
        else:
            simplified_pet = {  
                "name": name,
                "age": display_age,
                "species": species,
                "picture": picture,
                "id": id
            }

        simplified_pets.append(simplified_pet)

    return jsonify(simplified_pets), 200

@proxy_bp.route("/id", methods =["GET"])
def get_one_pet():
    id = request.args.get("id")

    if not id:
        return {"message": "Must provide a valid ID"}
    
    response = requests.get(
        f"https://api.rescuegroups.org/v5/public/animals/{id}",
        headers={"Authorization": rescue_key, "Content-Type":"application/vnd.api+json"},
    )
    data = response.json().get("data")
    included = response.json().get("included")
    if data:
            attributes = data[0].get("attributes")
            name = attributes.get("name")
            age = attributes.get("ageString", "")
            age_group = attributes.get("ageGroup")
            sex = attributes.get("sex")
            description = attributes.get("descriptionText")
            for i in included:
                if i["type"] == "pictures":
                    picture = i["attributes"]["large"]["url"]
                    break
            url = attributes.get("url")
            if age == "":
                display_age = age_group
            else:
                display_age = age
            cleaned_description = html.unescape(description)

            pet_info = {
                "id": id,
                "name": name,
                "age": display_age,
                "sex": sex,
                "description": cleaned_description,
                "picture": picture,
                "url": url,
            }

            return jsonify(pet_info), 200
    return {"message": "Pet not found"}, 404

@proxy_bp.route("/fav_id", methods=["GET"])
def get_favorite_pets():
    ids = request.args.get("ids")

    if not ids:
        return {"message": "Must provide valid IDs"}

    ids_list = ids.split(",")

    favorite_pets_info = []

    for id in ids_list:
        response = requests.get(
            f"https://api.rescuegroups.org/v5/public/animals/{id}",
            headers={"Authorization": rescue_key, "Content-Type": "application/vnd.api+json"},
        )
        data = response.json().get("data")

        for pet in data:
            attributes = pet.get("attributes")
            name = attributes.get("name")
            age = attributes.get("ageString", "")
            age_group = attributes.get("ageGroup")
            picture = attributes.get("pictureThumbnailUrl")
            id = pet.get("id")
            if age == "":
                display_age = age_group
            else:
                display_age = age

            pet_info = {
                "id": id,
                "name": name,
                "age": display_age,
                "picture": picture,
            }

            favorite_pets_info.append(pet_info)

    return jsonify(favorite_pets_info), 200