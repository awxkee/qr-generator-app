from io import BytesIO

from flask import Flask, send_file
import sdqrcode

app = Flask(__name__)

# init with a default config
generator = sdqrcode.init(config="default_diffusers")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/qr')
def get_qr(pid):
    images = generator.generate_sd_qrcode(
        prompt="A beautiful minecraft landscape",
        steps=30,
        cfg_scale=7,
        width=768,
        height=768,
        seed=-1,
        controlnet_weights=[0.35, 0.65],  # [weight_cn_1, weight_cn_2, ...]
        controlnet_startstops=[(0, 1), (0.35, 0.7)],
        # [(start_cn_1, end_cn_1), ... ]. (0.35, 0.7) means apply CN after 35% of total steps until 70% of total steps
        qrcode_text="https://koll.ai",
        qrcode_error_correction="high",
        qrcode_box_size=10,
        qrcode_border=4,
        qrcode_fill_color="black",
        qrcode_back_color="white",
    )
    img_io = BytesIO()
    images[0].save(img_io, 'PNG', quality=100)
    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run()
