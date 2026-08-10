import flet as ft
import requests
import base64
import os

API_URL = "http://127.0.0.1:8000/predict"


class PlantDiseaseApp:

    def __init__(self, page: ft.Page):

        self.page = page
        self.selected_image = None

        self.result_text = ft.Text(
            "",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_700,
        )

        self.confidence_text = ft.Text(size=18)

        self.preview = ft.Image(
            width=450,
            height=450,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=15,
        )

        self.loading = ft.ProgressRing(visible=False)

        self.file_picker = ft.FilePicker(
            on_result=self.pick_result
        )

        self.page.overlay.append(self.file_picker)

        self.content = ft.Container(
            expand=True,
            padding=25,
        )

        self.page.title = "Plant Disease Recognition System"
        self.page.window.width = 1400
        self.page.window.height = 850
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.scroll = ft.ScrollMode.AUTO

        self.build_ui()
    def build_ui(self):

        sidebar = ft.Container(
            width=250,
            bgcolor="#E8F5E9",
            padding=20,
            border_radius=10,

            content=ft.Column(

                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[

                    ft.Icon(
                        ft.Icons.ECO,
                        size=70,
                        color=ft.Colors.GREEN,
                    ),

                    ft.Text(
                        "Plant Disease\nRecognition",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Divider(),

                    ft.ElevatedButton(
                        text="Home",
                        width=190,
                        height=50,
                        on_click=lambda e: self.show_home(),
                    ),

                    ft.ElevatedButton(
                        text="About",
                        width=190,
                        height=50,
                        on_click=lambda e: self.show_about(),
                    ),

                    ft.ElevatedButton(
                        text="Disease Recognition",
                        width=190,
                        height=50,
                        on_click=lambda e: self.show_disease(),
                    ),

                    ft.Container(expand=True),

                    ft.Text(
                        "TensorFlow CNN",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),

                    ft.Text(
                        "FastAPI Backend",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),

                    ft.Text(
                        "Flet Desktop App",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),
                ]
            )
        )

        self.content.content = self.home_page()

        self.page.add(

            ft.Row(

                expand=True,

                controls=[

                    sidebar,

                    ft.VerticalDivider(width=1),

                    self.content,

                ]
            )
        )
    def show_home(self):

        self.content.content = self.home_page()

        self.page.update()
    def show_about(self):

        self.content.content = self.about_page()

        self.page.update() 
    def show_disease(self):

        self.content.content = self.disease_page()

        self.page.update()
    def home_page(self):

        image_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "home_page.jpeg",
        )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=25,
            controls=[

                ft.Text(
                    "Plant Disease Recognition System",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "AI-powered Crop Disease Detection using Deep Learning",
                    size=18,
                    color=ft.Colors.GREY_700,
                ),

                ft.Image(
                    src=image_path,
                    width=850,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=15,
                ),

                ft.Card(
                    content=ft.Container(
                        padding=25,
                        content=ft.Column(
                            controls=[

                                ft.Text(
                                    "Welcome",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "Welcome to the Plant Disease Recognition System! "
                                    "This application uses a Convolutional Neural Network "
                                    "(CNN) trained on thousands of crop leaf images to "
                                    "identify plant diseases quickly and accurately."
                                ),
                            ]
                        )
                    )
                ),

                ft.Text(
                    "How It Works",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(

                    spacing=25,

                    controls=[

                        ft.Card(
                            content=ft.Container(
                                width=210,
                                padding=20,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(ft.Icons.UPLOAD, size=50),
                                        ft.Text(
                                            "Upload Image",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Choose a leaf image from your computer.",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                ),
                            )
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=210,
                                padding=20,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(ft.Icons.PSYCHOLOGY, size=50),
                                        ft.Text(
                                            "AI Analysis",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "TensorFlow CNN analyzes the uploaded image.",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                ),
                            )
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=210,
                                padding=20,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=50),
                                        ft.Text(
                                            "Prediction",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Receive the detected disease with confidence.",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                ),
                            )
                        ),
                    ],
                ),

                ft.Text(
                    "Why Choose Our System?",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    spacing=20,
                    controls=[

                        ft.Chip(label=ft.Text("Fast Prediction")),

                        ft.Chip(label=ft.Text("CNN Deep Learning")),

                        ft.Chip(label=ft.Text("38 Disease Classes")),

                        ft.Chip(label=ft.Text("Simple Interface")),

                        ft.Chip(label=ft.Text("High Accuracy")),
                    ]
                ),
            ],
        )
    def about_page(self):

        return ft.Column(

            scroll=ft.ScrollMode.AUTO,

            spacing=20,

            controls=[

                ft.Text(
                    "About the Project",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Card(
                    content=ft.Container(

                        padding=20,

                        content=ft.Column(

                            controls=[

                                ft.Text(
                                    "Dataset",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "The dataset consists of approximately "
                                    "87,000 RGB images of healthy and diseased "
                                    "crop leaves divided into 38 classes."
                                ),
                            ]
                        )
                    )
                ),

                ft.Row(

                    spacing=20,

                    controls=[

                        ft.Card(
                            content=ft.Container(
                                width=180,
                                height=120,
                                alignment=ft.alignment.center,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            "87K+",
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text("Images"),
                                    ],
                                ),
                            )
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=180,
                                height=120,
                                alignment=ft.alignment.center,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            "38",
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text("Disease Classes"),
                                    ],
                                ),
                            )
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=180,
                                height=120,
                                alignment=ft.alignment.center,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            "CNN",
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text("TensorFlow Model"),
                                    ],
                                ),
                            )
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=180,
                                height=120,
                                alignment=ft.alignment.center,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            "FastAPI",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text("Backend"),
                                    ],
                                ),
                            )
                        ),
                    ],
                ),

                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column(
                            controls=[

                                ft.Text(
                                    "Technologies Used",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text("• TensorFlow / Keras"),

                                ft.Text("• FastAPI"),

                                ft.Text("• Flet"),

                                ft.Text("• Python"),

                                ft.Text("• CNN Image Classification"),
                            ]
                        )
                    )
                ),
            ],
        )
    def disease_page(self):

        self.plant_text = ft.Text(
            "",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_700,
        )

        self.disease_text = ft.Text(
            "",
            size=20,
            color=ft.Colors.RED_700,
        )

        self.confidence_bar = ft.ProgressBar(
            width=300,
            value=0,
            color=ft.Colors.GREEN,
        )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=25,
            controls=[

                ft.Text(
                    "Disease Recognition",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Upload a leaf image and let the AI identify the disease.",
                    size=18,
                    color=ft.Colors.GREY_700,
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=40,

                    controls=[

                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                width=480,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[

                                        self.preview,

                                        ft.ElevatedButton(
                                            "Choose Image",
                                            width=220,
                                            height=45,
                                            on_click=lambda e:
                                            self.file_picker.pick_files(
                                                allow_multiple=False
                                            ),
                                        ),

                                        ft.ElevatedButton(
                                            "Predict",
                                            width=220,
                                            height=45,
                                            bgcolor=ft.Colors.GREEN,
                                            color=ft.Colors.WHITE,
                                            on_click=self.predict,
                                        ),

                                        self.loading,
                                    ],
                                ),
                            ),
                        ),

                        ft.Card(
                            content=ft.Container(
                                width=420,
                                padding=25,
                                content=ft.Column(
                                    spacing=15,
                                    controls=[

                                        ft.Text(
                                            "Prediction Result",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),

                                        ft.Divider(),

                                        ft.Text(
                                            "Plant",
                                            weight=ft.FontWeight.BOLD,
                                        ),

                                        self.plant_text,

                                        ft.Text(
                                            "Disease",
                                            weight=ft.FontWeight.BOLD,
                                        ),

                                        self.disease_text,

                                        ft.Text(
                                            "Confidence",
                                            weight=ft.FontWeight.BOLD,
                                        ),

                                        self.confidence_bar,

                                        self.confidence_text,
                                    ],
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )
    def pick_result(self, e):

        if not e.files:
            return

        self.selected_image = e.files[0].path

        with open(self.selected_image, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        self.preview.src_base64 = encoded
        self.preview.visible = True

        self.plant_text.value = ""
        self.disease_text.value = ""
        self.confidence_text.value = ""
        self.confidence_bar.value = 0

        self.page.update()
    def predict(self, e):

            if self.selected_image is None:

                self.plant_text.value = "No image selected"
                self.disease_text.value = "Please choose an image first."

                self.page.update()
                return

            try:

                with open(self.selected_image, "rb") as f:

                    response = requests.post(
                        API_URL,
                        files={"file": f},
                    )

                data = response.json()

                prediction = data["prediction"]

                confidence = float(data["confidence"])

                if "___" in prediction:

                    plant, disease = prediction.split("___")

                else:

                    plant = prediction
                    disease = prediction

                disease = disease.replace("_", " ")

                self.plant_text.value = plant

                self.disease_text.value = disease

                self.confidence_text.value = f"{confidence:.2f}%"

                self.confidence_bar.value = confidence / 100

            except Exception as ex:

                self.plant_text.value = "Error"

                self.disease_text.value = str(ex)

                self.confidence_bar.value = 0

            self.loading.visible = False

            self.page.update()

def main(page: ft.Page):
    PlantDiseaseApp(page)

ft.app(target=main)
    