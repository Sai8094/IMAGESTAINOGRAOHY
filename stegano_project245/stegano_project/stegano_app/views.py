from django.shortcuts import render
from django.conf import settings
import stepic
from PIL import Image
import os

def index(request):
    return render(request, 'index.html')


def hide_text_in_image(image, text):
    data = text.encode('utf-8')

    # Convert image to RGB if it's not already
    if image.mode not in ['RGB', 'RGBA']:
        image = image.convert('RGB')

    return stepic.encode(image, data)


def encryption_view(request):
    message = ''
    if request.method == 'POST':
        text = request.POST.get('text')
        image_file = request.FILES.get('image')

        if not text or not image_file:
            message = 'Please provide both text and an image.'
        else:
            try:
                image = Image.open(image_file)

                if image.mode not in ['RGB', 'RGBA']:
                    image = image.convert('RGB')

                # Encode text into image
                new_image = hide_text_in_image(image, text)

                # Save encrypted image
                save_dir = os.path.join(settings.MEDIA_ROOT, 'encrypted_images')
                os.makedirs(save_dir, exist_ok=True)

                filename = 'new_' + os.path.basename(image_file.name)
                image_path = os.path.join(save_dir, filename)

                new_image.save(image_path, format="PNG")

                message = 'Text has been encrypted and saved successfully.'
            except Exception as e:
                message = f"An error occurred during encryption: {e}"

    return render(request, 'encryption.html', {'message': message})


def extract_text_from_image(image):
    if image.mode not in ['RGB', 'RGBA']:
        image = image.convert('RGB')

    data = stepic.decode(image)
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data


def decryption_view(request):
    text = ''
    error_message = ''

    if request.method == 'POST':
        image_file = request.FILES.get('image')

        if not image_file:
            error_message = 'No file uploaded. Please select an image.'
        else:
            try:
                image = Image.open(image_file)

                if image.mode not in ['RGB', 'RGBA']:
                    image = image.convert('RGB')

                text = extract_text_from_image(image)

                if not text.strip():
                    error_message = 'No hidden text was found in the image.'

            except Exception as e:
                error_message = f'An error occurred during decryption: {e}'

    return render(request, 'decryption.html', {
        'text': text,
        'error_message': error_message
    })
