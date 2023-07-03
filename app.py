import os
from io import BytesIO
from PIL import Image

from flask import Flask, send_file, request, render_template
import sdqrcode

app = Flask(__name__)

if os.environ.get('PROD') is not None:
    generator = sdqrcode.init(config="default_diffusers")

def resize_image_aspect_fit(image, target_size):
    # Get the original size of the image
    original_size = image.size

    # Calculate the aspect ratios of the image and the target size
    aspect_ratio = original_size[0] / original_size[1]
    target_aspect_ratio = target_size[0] / target_size[1]

    # Calculate the new size that maintains the aspect ratio
    if aspect_ratio > target_aspect_ratio:
        new_size = (target_size[0], int(target_size[0] / aspect_ratio))
    else:
        new_size = (int(target_size[1] * aspect_ratio), target_size[1])

    # Resize the image using the calculated size
    image.thumbnail(new_size, Image.LANCZOS)

    # Create a new blank image with the target size
    resized_image = Image.new('RGB', target_size, (255, 255, 255))

    # Calculate the position to paste the resized image
    position = ((target_size[0] - new_size[0]) // 2, (target_size[1] - new_size[1]) // 2)

    # Paste the resized image onto the blank image
    resized_image.paste(image, position)

    return resized_image

@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/qr', methods=["POST"])
def get_qr():
    use_prompt_generator = False
    if request.method == 'POST':
        payload = request.form
        prompt = payload.get('prompt')
        qr_contents = payload.get('qr_contents')
        if prompt is not None:
            use_prompt_generator = True
        else:
            file = request.files['file']
            pil_image = resize_image_aspect_fit(Image.open(file), [768, 768])
            use_prompt_generator = False
    elif request.method == 'GET':
        prompt = request.args.get('prompt')
        qr_contents = request.args.get('qr_contents')
    else:
        prompt = 'A beautiful winter landscape'
        qr_contents = 'Radzivon'
    if os.environ.get('PROD') is not None:
        if use_prompt_generator:
            images = generator.generate_sd_qrcode(
                prompt=prompt,
                steps=25,
                cfg_scale=7,
                width=768,
                height=768,
                seed=-1,
                controlnet_weights=[0.35, 0.65],  # [weight_cn_1, weight_cn_2, ...]
                controlnet_startstops=[(0, 1), (0.35, 0.7)],
                # [(start_cn_1, end_cn_1), ... ]. (0.35, 0.7) means apply CN after 35% of total steps until 70% of total steps
                qrcode_text=qr_contents,
                qrcode_error_correction="high",
                qrcode_box_size=10,
                qrcode_border=4,
                qrcode_fill_color="black",
                qrcode_back_color="white",
            )
        else:
            images = generator.generate_sd_qrcode(
                mode='img2img',
                input_image=pil_image,
                steps=17,
                cfg_scale=7,
                width=768,
                height=768,
                seed=-1,
                controlnet_weights=[0.35, 0.65],  # [weight_cn_1, weight_cn_2, ...]
                controlnet_startstops=[(0, 1), (0.35, 0.7)],
                # [(start_cn_1, end_cn_1), ... ]. (0.35, 0.7) means apply CN after 35% of total steps until 70% of total steps
                qrcode_text=qr_contents,
                qrcode_error_correction="high",
                qrcode_box_size=10,
                qrcode_border=4,
                qrcode_fill_color="black",
                qrcode_back_color="white",
            )
        print(f'length of generated codes: {len(images)}')
        img_io = BytesIO()
        images[0].save(img_io, 'PNG', quality=100)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    else:
        with open('static/test.jpg', "rb") as fh:
            buf = BytesIO(fh.read())
        return send_file(buf, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
