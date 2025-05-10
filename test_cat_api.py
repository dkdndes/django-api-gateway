import requests
import json

# Base URL for our API Gateway
BASE_URL = "http://localhost:12000/api"

def test_random_cats():
    """Test the random cats endpoint"""
    url = f"{BASE_URL}/cats/random"
    response = requests.get(url)
    
    print(f"Random Cats - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_cat_breeds():
    """Test the cat breeds endpoint"""
    url = f"{BASE_URL}/cats/breeds"
    response = requests.get(url)
    
    print(f"Cat Breeds - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        # Print just the first 2 breeds to keep output manageable
        print(json.dumps(data[:2], indent=2))
        print(f"Total breeds: {len(data)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_breed_by_id():
    """Test getting a specific breed by ID"""
    # Using 'abys' (Abyssinian) as an example breed ID
    breed_id = "abys"
    url = f"{BASE_URL}/cats/breeds"
    response = requests.get(url)
    
    print(f"All Breeds - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        # Find the specific breed by ID
        breed = next((b for b in data if b.get('id') == breed_id), None)
        if breed:
            print(f"Found breed with ID {breed_id}:")
            print(json.dumps(breed, indent=2))
        else:
            print(f"Breed with ID {breed_id} not found")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_images_by_breed():
    """Test getting images for a specific breed"""
    # Using 'beng' (Bengal) as an example breed ID
    breed_id = "beng"
    url = f"{BASE_URL}/cats/images/breed?breed_ids={breed_id}&limit=10"
    response = requests.get(url)
    
    print(f"Images by Breed ({breed_id}) - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        # Print just the first image to keep output manageable
        if data:
            print(json.dumps(data[0], indent=2))
            print(f"Total images: {len(data)}")
        else:
            print("No images found")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    print("Testing TheCatAPI integration with Django API Gateway")
    print("=" * 50)
    
    test_random_cats()
    test_cat_breeds()
    test_breed_by_id()
    test_images_by_breed()
    
    print("Tests completed!")