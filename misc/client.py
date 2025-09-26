import requests

def send_image_to_server(image_path):
    url = 'http://localhost:5000/predict'

    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print('Error:', response.status_code)
        return None



if __name__ == '__main__':
    image_path = 'testing-signs/004.png'
    result = send_image_to_server(image_path)

    if result:
        for prediction in result["predictions"]:
            print(f"Class: {prediction['class']}, Confidence: {prediction['confidence']}")