import os
from io import BytesIO

from flask import Flask, send_file, request, render_template
import sdqrcode

app = Flask(__name__)

if os.environ.get('PROD') is not None:
    generator = sdqrcode.init(config="default_diffusers")


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/qr', methods=["POST", "GET"])
def get_qr():
    if os.environ.get('PROD') is not None:
        if request.method == 'POST':
            payload = request.json
            prompt = payload['prompt']
            qr_contents = payload['qr_contents']
        elif request.method == 'GET':
            prompt = request.args.get('prompt')
            qr_contents = request.args.get('qr_contents')
        else:
            prompt = 'A beautiful winter landscape'
            qr_contents = 'Radzivon'
        images = generator.generate_sd_qrcode(
            prompt=prompt,
            steps=30,
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
        return send_file(img_io, mimetype='image/png')
    else:
        with open('static/test.jpg', "rb") as fh:
            buf = BytesIO(fh.read())
        return send_file(buf, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
