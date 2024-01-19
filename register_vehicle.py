
def scan_qr_code(self):
    # Capture a frame from the camera
    camera = self.ids.camera
    image_texture = camera.export_as_texture()

    # Decode the frame to check for a QR code
    try:
        decoded_qr = self.decode_qr_code(image_texture.pixels)
        if decoded_qr:
            self.qr_code_result = decoded_qr
            self.show_qr_result_popup()
        else:
            self.show_error_popup("No QR code found!")
    except Exception as e:
        self.show_error_popup(f"Error: {str(e)}")


def decode_qr_code(self, image_pixels):
    # Convert the image pixels to a BytesIO object
    image_bytes = BytesIO(image_pixels)
    # Try to decode the QR code
    qr_code = qrcode.QRCode()
    qr_code.add_data(image_bytes)
    qr_code.make(fit=True)
    decoded_qr = qr_code.make_image(fill_color="black", back_color="white")
    return decoded_qr


def show_qr_result_popup(self):
    content = BoxLayout(orientation="vertical")
    content.add_widget(Label(text="QR Code Result"))
    content.add_widget(Image(texture=self.ids.camera.export_as_texture()))
    content.add_widget(Label(text=self.qr_code_result))

    popup = Popup(
        title="QR Code Result",
        content=content,
        size_hint=(None, None),
        size=(400, 400),
        auto_dismiss=True,
    )
    popup.open()


def show_error_popup(self, message):
    content = BoxLayout(orientation="vertical")
    content.add_widget(Label(text=message))

    popup = Popup(
        title="Error",
        content=content,
        size_hint=(None, None),
        size=(300, 200),
        auto_dismiss=True,
    )
    popup.open()

